
import os
import json
import uuid
import base64
import hashlib
import logging


from ._const  import *
from .network import (
    make_request,
    check_response,
)

from .utils   import (
    DeepSeekHash,
    get_mime,
    gzip_data,
    aes_encrypt,
    rsa_encrypt,
    check_file_exist,
    is_file_type_accepted,
)

from safe_dict import SafeDict

logging.basicConfig(level=logging.INFO)

class DeepSeekApi:
    def __init__(self, token=None):
        self.token         = token
        self.deepseek_hash = DeepSeekHash()
        self.is_muted      = False

        if self.token:
            self.is_muted = self._check_user_mute()
        
    @property
    def headers(self):
        headers = {
            'x-client-platform': 'android',
            'x-client-version': '1.0.6',
            'x-client-locale': 'en_US',
            'x-rangers-id': '7881644457110842881',
            'user-agent': 'DeepSeek/1.0.6 Android/31',
            # 'accept': 'application/json',
            'accept-charset': 'UTF-8',
            # 'content-type': 'application/json',
        }
        
        if self.token:
            headers.update({"authorization": f"Bearer {self.token}"})
            
        return headers
    
    def __check_login(self):
        if not self.token:
            raise ValueError("Login required!")
        
    def __handle_response(self, response):
        message_id = None

        for line in response.iter_lines():
            line_str = line.decode()

            if not line_str or line_str is None:
                continue

            if "data: " in line_str:
                line_str = line_str[6:]

            if line_str == "[DONE]":
                break


            try:
                line_json = json.loads(line_str)
            except json.decoder.JSONDecodeError:
                continue

            line_json = SafeDict(line_json)

            choices = line_json.get("choices", [])
            if choices:
                content = choices[0].get("delta", {}).get("content", "")

                yield {
                    "message": content,
                    "message_id": message_id,
                }

    
    def _register_device(self):
        uuid_str = str(uuid.uuid4())
        aes_key  = hashlib.md5(uuid_str.encode('utf-8')).hexdigest()[:0x10]
        data_zip = gzip_data(DEVICE_INFO)
        data_aes = aes_encrypt(data_zip, aes_key)
        uuid_rsa = rsa_encrypt(uuid_str, RSA_PUBLIC_KEY)

        json_data = {
            'appId': 'default',
            'organization': 'P9usCUBauxft8eAmUXaZ',
            'ep': uuid_rsa,
            'data': data_aes,
            'os': 'web',
            'encode': 5,
            'compress': 2,
        }

        response = make_request(
            method="POST",
            url=API_REG_DEVICE,
            headers=self.headers,
            json=json_data
        )

        check_response(response)
        
        response_json = SafeDict(response.json())
        if response_json.get("code") == 1100:
            return response_json.get("detail", {}).get("deviceId")

        return None

    def login(self, email, password):
        device_id = self._register_device()
        
        if not device_id:
            raise ValueError("register device failed!")
        
        json_data = {
            'email': email,
            'mobile': '',
            'password': password,
            'area_code': '',
            'device_id': device_id,
            'os': 'android',
        }

        response = make_request(
            method="POST",
            url=BASE_API + LOGIN_EP,
            headers=self.headers,
            json=json_data
        )

        check_response(response)

        response_json = SafeDict(response.json())
        if response_json.get("code") == 0:

            self.token = (response_json.get("data", {})
                                       .get("user", {})
                                       .get("token"))

        if not self.token:
            raise ValueError("Login failed!")
        
        self.is_muted = self._check_user_mute()

        return self.token
    

    def _create_challenge(self, target_endpoint):
        self.__check_login()
        
        data = dict(
            target_path=target_endpoint
        )

        response = make_request(
            method="POST",
            url=BASE_API + CREATE_CHALLENGE_EP,
            headers=self.headers,
            data=json.dumps(data, separators=[",", ":"]),
        )
        
        check_response(response)

        response_json = SafeDict(response.json())
        if response_json.get("code") == 0:
            return response_json.get("data", {}).get("biz_data", {}).get("challenge", {})
        
        return dict()


    def _solve_challenge(self, target_endpoint):
        challenge_data:dict = self._create_challenge(target_endpoint)

        if not challenge_data:
            raise ValueError("get challenge_data failed!")

        answer = self.deepseek_hash.solve_hash(
            challenge_data.get("challenge"),
            challenge_data.get("salt"),
            challenge_data.get("difficulty"),
            challenge_data.get("expire_at"),
        )
        
        challenge_data.update({"answer": answer})

        x_ds_pow = dict(
            algorithm=challenge_data.get("algorithm"),
            challenge=challenge_data.get("challenge"),
            salt=challenge_data.get("salt"),
            answer=int(answer),
            signature=challenge_data.get("signature"),
            target_path=challenge_data.get("target_path"),
        )

        x_ds_pow_str = json.dumps(x_ds_pow, separators=[",", ":"])

        return base64.b64encode(x_ds_pow_str.encode("utf-8")).decode()

    def _check_user_mute(self):
        self.__check_login()

        response = make_request(
            method="GET",
            url=BASE_API + USER_INFO_EP,
            headers=self.headers,
        )

        check_response(response)
        
        response_json = SafeDict(response.json())
        if response_json.get("code") == 0:
            if response_json.get("data", {}).get("chat", {}).get("is_muted") == 0:
                return False
        
        return True
    
    def upload_file(self, file_path):
        self.__check_login()
        
        if not check_file_exist(file_path):
            raise ValueError(f"File {file_path} not exist")
        
        if not is_file_type_accepted(file_path):
            logging.info("The uploaded file format is not supported. Supported formats include PDF, DOC, XLSX, PPT, images, text, and code.")
            return None
        
        headers = {
            **self.headers,
            'x-ds-pow-response': self._solve_challenge(UPLOAD_FILE_EP),
        }

        with open(file_path, 'rb') as f:
            files = {
                "file": (
                    os.path.basename(file_path),
                    f.read(),
                    get_mime(file_path)
                )
            }

        response = make_request(
            method="POST",
            url=BASE_API + UPLOAD_FILE_EP,
            headers=headers,
            files=files
        )

        check_response(response)

        response_json = SafeDict(response.json())

        if response_json.get("data", {}).get("biz_code") == 0:
            return response_json.get("data", {}).get("biz_data", {}).get("id")

    def fetch_file(self, file_id):
        params = dict(
            file_ids=file_id
        )

        response = make_request(
            method="GET",
            url=BASE_API + FETCH_FILE_EP,
            params=params
        )

        check_response(response)
        
        response_json = SafeDict(response.json())
        if response_json.get("data", {}).get("biz_code") == 0:
            files_info = response_json.get("data", {}).get("biz_data", {}).get("files", [{}])
            if files_info:
                return SafeDict(files_info[0]).get("status")

    def fetch_chat_session(self):
        self.__check_login()

        response = make_request(
            method="GET",
            url=BASE_API + FETCH_CHAT_SS_EP,
            headers=self.headers
        )

        check_response(response)

        response_json = SafeDict(response.json())

        if response_json.get("data", {}).get("biz_code") == 0:
            return response_json.get("data", {}).get("biz_data", {}).get("chat_sessions", [])

    def fetch_chat_history(self, chat_session_id):
        self.__check_login()

        params = dict(
            chat_session_id=chat_session_id
        )

        response = make_request(
            method="GET",
            url=BASE_API + FETCH_CHAT_HIS_EP,
            headers=self.headers,
            params=params
        )

        check_response(response)

        title              = None
        current_message_id = None

        chat_messages      = []

        response_json = SafeDict(response.json())

        if response_json.get("data", {}).get("biz_code") == 0:
            biz_data           = response_json.get("data", {}).get("biz_data", {})
            title              = biz_data.get("chat_session", {}).get("title")
            current_message_id = biz_data.get("chat_session", {}).get("current_message_id")
            chat_messages      = biz_data.get("chat_messages", [])

        return title, current_message_id, chat_messages

    def create_session(self):
        self.__check_login()

        if self.is_muted:
            raise ValueError("User is muted!")
    
        data = '{"agent":"chat"}'

        response = make_request(
            method="POST",
            url=BASE_API + CREATE_SESSION_EP,
            headers=self.headers,
            data=data
        )

        check_response(response)

        response_json = SafeDict(response.json())

        if response_json.get("code") == 0:
            return response_json.get("data", {}).get("biz_data", {}).get("id")

    def delete_session(self, chat_session_id):
        self.__check_login()

        data = json.dumps({"chat_session_id": chat_session_id})

        response = make_request(
            method="POST",
            url=BASE_API + DELETE_CHAT_SS_EP,
            headers=self.headers,
            data=data,
        )

        check_response(response)

        response_json = SafeDict(response.json())

        return response_json.get("data", {}).get("biz_code") == 0

    def completion(
        self,
        chat_session_id,
        prompt,
        parent_message_id=None,
        ref_file_ids=[],
        thinking_enabled=False,
        search_enabled=False,
    ):
        self.__check_login()

        if self.is_muted:
            raise ValueError("User is muted!")
        
        headers = {
            **self.headers,
            'x-ds-pow-response': self._solve_challenge(COMPLETE_EP)
        }

        json_data = {
            'chat_session_id': chat_session_id,
            'parent_message_id': parent_message_id,
            'prompt': prompt,
            'ref_file_ids': ref_file_ids,
            'thinking_enabled': thinking_enabled,
            'search_enabled': search_enabled,
        }

        response = make_request(
            method="POST",
            url=BASE_API + COMPLETE_EP,
            headers=headers,
            json=json_data,
            stream=True
        )

        check_response(response)

        return self.__handle_response(response)

