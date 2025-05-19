from pprint import pprint
import time

print("import start")
start_import = time.time()
from transformers import pipeline
print(f"import end (in {time.time() - start_import:.2f}s)")

classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True,
    framework="pt"
)

class EmotionClassification():
    """감정 분석하는 클래스입니다."""
    def __init__(self):
        self.classifier = classifier

    def analyze(self, text : str, show_info : bool = False):
        """감정 분석하는 메서드입니다."""
        result = self.classifier(text)
        if show_info:
            pprint(result)
        top_label = max(result[0], key=lambda x: x["score"])
        predicted_emotion = top_label["label"]
        return predicted_emotion


if __name__ == "__main__":
    print("start")
    emotion = EmotionClassification()
    text = """
    i love you
    """
    result = emotion.analyze(text, show_info=True)
    print(result)

