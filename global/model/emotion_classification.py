from pprint import pprint
from transformers import pipeline

class EmotionClassification():
    """감정 분석하는 클래스입니다."""
    def __init__(self):
        self.classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base",
                      return_all_scores=True)

    def analyze(self, text : str, show_info : bool = False):
        """감정 분석하는 메서드입니다."""
        result = self.classifier(text)
        if show_info:
            pprint(result)
        top_label = max(result[0], key=lambda x: x["score"])
        pretected_emotion = top_label["label"]
        return pretected_emotion


if __name__ == "__main__":
    emotion = EmotionClassification()
    text = """
    i love you
    """
    result = emotion.analyze(text, show_info=True)
    print(result)

