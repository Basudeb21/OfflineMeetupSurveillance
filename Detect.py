import re
import spacy
import pytesseract
import redis
import json
from PIL import Image
import requests
from io import BytesIO
import sys, os
from datetime import datetime

# ─────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'api')))
from insert_db import save_message_to_db, save_attachment_to_db
from api.database import get_db

# ─────────────────────────────────────────────
# REDIS & TESSERACT SETUP
# ─────────────────────────────────────────────
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
TEXT_REDIS_QUEUE = "fliqz_moderation_text_queue"
OCR_REDIS_QUEUE = "fliqz_moderation_image_video_queue"

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
nlp = spacy.load("en_core_web_sm")

# ─────────────────────────────────────────────
# REGEX PATTERNS
# ─────────────────────────────────────────────
email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
url_pattern = re.compile(r'(https?:\/\/[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)')
phone_pattern = re.compile(r'\+?\d[\d\s\-()]{7,}\d')
PLATFORM_DOMAIN = "myvault-web.codextechnolife.com"
number_words = {
    "zero","one","two","three","four","five","six","seven","eight","nine",
    "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
    "seventeen","eighteen","nineteen","twenty","thirty","forty","fifty",
    "sixty","seventy","eighty","ninety","hundred","thousand","million","billion"
}

# ─────────────────────────────────────────────
# DETECTION HELPERS
# ─────────────────────────────────────────────
def isEmail(text): return bool(email_pattern.search(text))
def hasPhoneNumber(text): return bool(phone_pattern.search(text))
def hasNumber(n): return isinstance(n, int) or (isinstance(n, str) and any(ch.isdigit() for ch in n) and PLATFORM_DOMAIN not in n)
def hasNumberWords(text): return any(w in number_words for w in re.findall(r'\b[a-zA-Z]+\b', text.lower()))
def hasForbiddenURL(text):
    for match in url_pattern.finditer(text):
        url = match.group(0).rstrip('.,!?')
        if not re.search(r'\.[a-zA-Z]{2,}', url): continue
        if PLATFORM_DOMAIN not in url: return True
    return False
def hasAddress(text): return any(ent.label_ in {"GPE","LOC","FAC"} for ent in nlp(text).ents)
def isPersonalDetails(text): 
    return any([hasForbiddenURL(text), isEmail(text), hasPhoneNumber(text), hasNumberWords(text), hasNumber(text), hasAddress(text)])

# ─────────────────────────────────────────────
# OCR EXTRACTION
# ─────────────────────────────────────────────
def extract_text_from_file(file_path_or_url: str):
    try:
        if file_path_or_url.startswith("http"):
            response = requests.get(file_path_or_url)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(file_path_or_url)
        return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error in OCR: {e}")
        return ""

# ─────────────────────────────────────────────
# REDIS HANDLER
# ─────────────────────────────────────────────
def process_redis_messages():
    print("🎧 Listening to Redis queues...")

    while True:
        try:
            # Wait for messages from either queue
            queue_name, message = r.blpop([TEXT_REDIS_QUEUE, OCR_REDIS_QUEUE])
            data = json.loads(message)

            if queue_name == TEXT_REDIS_QUEUE:
                text_to_check = data.get("text", "")
                if data.get("filename"):
                    text_to_check += " " + extract_text_from_file(data["filename"])
                result = isPersonalDetails(text_to_check)
                save_message_to_db(data, result)
                print(f"✅ [TEXT] Processed → personal={result}")

            elif queue_name == OCR_REDIS_QUEUE:
                filename = data.get("filename")
                if not filename:
                    print("❌ No filename in OCR message")
                    continue
                extracted_text = extract_text_from_file(filename)
                result = isPersonalDetails(extracted_text)
                save_attachment_to_db(data, result)
                print(f"✅ [IMAGE/VIDEO] Processed → personal={result}")

        except Exception as e:
            print("❌ Redis Processing Error:", repr(e))

# ─────────────────────────────────────────────
# MAIN ENTRY
# ─────────────────────────────────────────────
if __name__ == "__main__":
    process_redis_messages()
