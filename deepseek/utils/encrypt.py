import gzip
import json
import base64


from Crypto.Cipher    import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

def aes_encrypt(data, key:str):
    iv        = b'0102030405060708'
    key_bytes = key.encode('utf-8')

    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, separators=[",", ":"])
    else:
        data_str = str(data)

    block_size     = 16
    data_bytes     = data_str.encode('utf-8')
    padding_length = (block_size - (len(data_bytes) % block_size)) % block_size
    padded_data    = data_bytes + b'\x00' * padding_length
    cipher         = AES.new(key_bytes, AES.MODE_CBC, iv)

    return cipher.encrypt(padded_data).hex()

def rsa_encrypt(data, public_key):
    key            = RSA.import_key(public_key)
    cipher         = PKCS1_v1_5.new(key)
    encrypted_data = cipher.encrypt(data.encode('utf-8'))

    return base64.b64encode(encrypted_data).decode('utf-8')

def gzip_data(data):
    json_string       = json.dumps(data, separators=[",", ":"])
    compressed        = gzip.compress(json_string.encode('utf-8'))
    compressed_base64 = base64.b64encode(compressed).decode('utf-8')

    return compressed_base64
