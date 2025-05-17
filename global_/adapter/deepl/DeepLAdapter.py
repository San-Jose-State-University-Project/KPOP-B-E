import deepl
from dotenv import load_dotenv
import os
load_dotenv()


class DeepLAdapter:
    def __init__(self):
        auth_key = os.getenv("DEEPL_SECRET_KEY")
        self.translator = deepl.Translator(auth_key)

    def translate(self, message, target_lang="EN-US", show_info : bool = False):
        result = self.translator.translate_text(message, target_lang=target_lang)
        if show_info == True:
            print(result)
        return result

if __name__ == "__main__":
    deepl = DeepLAdapter()
    message = "안녕"
    deepl.translate(message, show_info=True)