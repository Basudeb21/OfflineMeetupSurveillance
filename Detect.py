import re
import spacy
import os
import time
import pytesseract
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # Mac
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows

nlp = spacy.load("en_core_web_sm")

email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
url_pattern = re.compile(r'(https?:\/\/[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)')
phone_pattern = re.compile(r'\+?\d[\d\s\-()]{7,}\d') 

PLATFORM_DOMAIN = "myvault-web.codextechnolife.com"

number_words = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million", "billion"
}


def isEmail(text: str) -> bool:
    return bool(email_pattern.search(text))

def hasPhoneNumber(text: str) -> bool:
    return bool(phone_pattern.search(text))

def hasNumber(n) -> bool:
    if isinstance(n, int):
        return True
    if isinstance(n, str):
        if PLATFORM_DOMAIN in n:
            return False
        return any(ch.isdigit() for ch in n)
    return False

def hasNumberWords(text: str) -> bool:
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return any(word in number_words for word in words)

def hasForbiddenURL(text: str) -> bool:
    for match in url_pattern.finditer(text):
        url = match.group(0).rstrip('.,!?')
        if not re.search(r'\.[a-zA-Z]{2,}', url):
            continue
        if PLATFORM_DOMAIN not in url:
            return True
    return False

def hasAddress(text: str) -> bool:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in {"GPE", "LOC", "FAC"}:
            return True
    return False

def isPersonalDetails(text: str) -> bool:
    if hasForbiddenURL(text):
        return True
    if isEmail(text):
        return True
    if hasPhoneNumber(text):
        return True
    if hasNumberWords(text):
        return True
    if hasNumber(text):
        return True
    if hasAddress(text):
        return True
    return False

# -------------------------
# OCR & Folder Watcher
# -------------------------
WATCH_FOLDER = "files_to_check"

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        print(f"\n📂 New file detected: {filepath}")
        
        if filepath.lower().endswith((".png", ".jpg", ".jpeg", ".tiff")):
            text = extract_text_from_image(filepath)
            print(f"📝 OCR Extracted Text:\n{text}")
            
            if isPersonalDetails(text):
                print("⚠️ Personal details detected in image!")
            else:
                print("✅ No personal details found in image.")
        else:
            print("❌ File type not supported for OCR")

def extract_text_from_image(filepath: str) -> str:
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error in OCR: {e}")
        return ""

def start_watching(folder: str):
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=False)
    observer.start()
    print(f"👀 Watching folder: {folder}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER)

    watcher_thread = threading.Thread(target=start_watching, args=(WATCH_FOLDER,), daemon=True)
    watcher_thread.start()

    print("✅ Personal Details Detector is running.")
    print("Type any text to check, or Ctrl+C to exit.\n")

    try:
        while True:
            user_input = input("Enter text to check: ").strip()
            if not user_input:
                continue
            result = isPersonalDetails(user_input)
            print(f"Result: {result}\n")
    except KeyboardInterrupt:
        print("\nExiting...")
