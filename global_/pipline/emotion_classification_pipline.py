from global_.model.emotion_classification import EmotionClassification
from global_.adapter.deepl.DeepLAdapter import DeepLAdapter
from collections import Counter


class EmotionPipeline:
    def __init__(self):
        self.translator = DeepLAdapter()
        self.model = EmotionClassification()

    def classification(self, lyrics: str):
        lines = lyrics.strip().split("\n")
        predicted_emotions = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            translated_line = self.translator.translate(line).text.strip()

            if len(translated_line) > 2000:
                translated_line = translated_line[:2000]

            try:
                emotion = self.model.analyze(translated_line)
                predicted_emotions.append(emotion)
            except Exception as e:
                print(f"분석 중 오류 발생 (line='{line[:30]}...'): {e}")

        if predicted_emotions:
            emotion_count = Counter(predicted_emotions)

            filtered = [e for e in predicted_emotions if e != "neutral"]

            if filtered:
                most_common_emotion = Counter(filtered).most_common(1)[0][0]
            else:
                most_common_emotion = "neutral"

            print("감정 분포:", emotion_count)
            print("대표 감정:", most_common_emotion)
            return most_common_emotion


if __name__ == "__main__":
    pipeline = EmotionPipeline()
    lyrics = """
    저 오늘 떠나요 공항으로
    핸드폰 꺼 놔요 제발 날 찾진 말아줘
    시끄럽게 소리를 질러도 어쩔 수 없어 나
    가볍게 손을 흔들며 bye-bye

    쉬지 않고 빛났던 꿈같은 my youth
    이리저리 치이고 또 망가질 때쯤
    지쳤어, 나 미쳤어, 나 떠날 거야, 다 비켜
    I fly away

    Take me to London, Paris, New York City들
    아름다운 이 도시에 빠져서 나
    Like I'm a bird, bird, 날아다니는 새처럼
    난 자유롭게 fly, fly, 나 숨을 셔
    Take me to new world anywhere, 어디든
    답답한 이 곳을 벗어 나기만 하면
    Shining light, light, 빛나는 my youth
    자유롭게 fly, fly, 나 숨을 셔

    저 이제 쉬어요, 떠날 거예요
    노트북 꺼 놔요, 제발 날 잡진 말아줘
    시끄럽게 소리를 질러도 어쩔 수 없어 나
    가볍게 손을 흔들며 see you

    I can fly away
    Fly always, always, always
    Fly always

    Take me to new world anywhere, 어디든
    답답한 이 곳을 벗어 나기만 하면
    Shining light, light, 빛나는 my youth
    자유롭게 fly, fly, 나 숨을 셔
    """
    pipeline.classification(lyrics)
