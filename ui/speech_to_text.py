import speech_recognition as sr
from deep_translator import GoogleTranslator
import json
import re
from datetime import datetime

def load_dictionary():
    """讀取詞庫 JSON 檔案"""
    try:
        with open("dictionary.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ 詞庫檔案未找到，請先建立 dictionary.json！")
        return {}

def find_definitions(text, dictionary):
    """從語句中提取名詞，並查找詞典中的解釋"""
    found_terms = {}
    for term in dictionary.keys():
        if term in text:
            found_terms[term] = dictionary[term]
            # print(f"🔍 發現名詞：{term}，解釋：{dictionary[term]}")
    return found_terms

def record_and_transcribe(mode):
    """錄音直到 5 秒內無輸入，然後轉換語音為文字並翻譯"""
    recognizer = sr.Recognizer()
    dictionary = load_dictionary()  # 載入詞庫

    with sr.Microphone() as source:
        print("請開始說話...")
        recognizer.adjust_for_ambient_noise(source)  # 降噪

        print(f"🎤 語音模式：{mode}")

        try:
            # 設定 timeout=5，當 5 秒內無輸入時結束
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=30)
            print("錄音結束，正在轉換文字...")

            # 語音轉換（預設識別為繁體中文）
            text_cn = recognizer.recognize_google(audio, language="zh-TW")

            # 翻譯成其他語言（使用 Deep Translator）
            text_en = GoogleTranslator(source="zh-TW", target="en").translate(text_cn)
            text_de = GoogleTranslator(source="zh-TW", target="de").translate(text_cn)
            text_ja = GoogleTranslator(source="zh-TW", target="ja").translate(text_cn)

            # **如果是精確模式，則查詢詞典**
            definitions = {}
            if mode == "精確模式":
                definitions = find_definitions(text_cn, dictionary)

            # 儲存到會議紀錄（附上時間）
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            with open("history.txt", "a", encoding="utf-8") as f:
                f.write(f"{timestamp} 中文: {text_cn} | 英文: {text_en} | 德文: {text_de} | 日文: {text_ja}\n")

                # 如果有名詞解釋，儲存到紀錄
                if definitions:
                    f.write(f"🔍 名詞解釋: {json.dumps(definitions, ensure_ascii=False)}\n")

            print("defintions", definitions)

            return text_cn, text_en, text_de, text_ja, definitions

        except sr.WaitTimeoutError:
            return "⏳ 錄音超時，未偵測到語音。", "", "", "", {}
        except sr.UnknownValueError:
            return "❌ 無法辨識語音，請再試一次。", "", "", "", {}
        except sr.RequestError:
            return "⚠️ 語音服務無回應，請檢查網路。", "", "", "", {}



def search_history(keyword):
    """搜尋會議紀錄，根據關鍵字顯示結果"""
    try:
        with open("history.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 如果沒有輸入關鍵字，則顯示全部
        if not keyword.strip():
            return "".join(lines) if lines else "📌 尚無會議紀錄。"

        # 依照關鍵字過濾
        filtered_lines = [line for line in lines if keyword.lower() in line.lower()]
        return "".join(filtered_lines) if filtered_lines else f"🔍 未找到包含 `{keyword}` 的紀錄。"

    except FileNotFoundError:
        return "📌 尚無會議紀錄。"
