import deepl
from dotenv import load_dotenv
import os
load_dotenv()


class DeepLAdapter:
    def __init__(self):
        auth_key = os.getenv("DEEPL_SECRET_KEY")
        self.translator = deepl.Translator(auth_key)

    async def translate(self, message, target_lang="EN-US", show_info : bool = False):
        result = self.translator.translate_text(message, target_lang=target_lang)
        if show_info == True:
            print(result)
        return result

    def print_supported_languages(self):
        for lang in self.translator.get_target_languages():
            print(lang.code, lang.name)

if __name__ == "__main__":
    deepl = DeepLAdapter()
    message = "안녕"
    deepl.print_supported_languages()