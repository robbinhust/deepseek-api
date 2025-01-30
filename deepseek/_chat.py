from ._api import DeepSeekApi

class Conversation:
    def __init__(self, api: DeepSeekApi):
        self.api                = api
        self.chat_session_id    = None
        self.current_message_id = None

    def continuous_chat(self, chat_session_id=None):
        if not chat_session_id:
            self.chat_session_id = self.api.create_session()
        
        else:
            self.chat_session_id = chat_session_id
            title, self.current_message_id, chat_messages = self.api.fetch_chat_history(chat_session_id)
            
            print("TITLE", title, "\n\n")

            for chat_msg in chat_messages:
                print(f"{chat_msg.get('role')}: ", chat_msg.get("content"), "\n")


        while True:
            prompt = input("USER: ")
            print()

            for msg in self.api.completion(
                self.chat_session_id,
                prompt,
                parent_message_id=self.current_message_id,
            ):
                print(msg.get("message"), end="", flush=True)
                self.current_message_id = msg.get("message_id")

            print("\n")

