import re
import spacy
import os
import time
import pytesseract
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Load Spacy model
nlp = spacy.load("en_core_web_sm")

# Regex patterns
email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
url_pattern = re.compile(r'(https?:\/\/[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)')
phone_pattern = re.compile(r'\+?\d[\d\s\-()]{7,}\d')  # Phone numbers (basic)

# Platform domain (allowed URL domain)
PLATFORM_DOMAIN = "myvault-web.codextechnolife.com"

# Number words
number_words = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million", "billion"
}

# -------------------------
# Existing Functions
# -------------------------
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
# OCR + File Watcher
# -------------------------
WATCH_FOLDER = "files_to_check"

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        print(f"\n📂 New file detected: {filepath}")
        
        # Process only images (visiting cards usually images)
        if filepath.lower().endswith((".png", ".jpg", ".jpeg", ".tiff")):
            text = extract_text_from_image(filepath)
            print(f"📝 OCR Extracted Text:\n{text}")
            
            if isPersonalDetails(text):
                print("⚠️ Personal details detected in visiting card!")
            else:
                print("✅ No personal details found.")
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

# -------------------------
# Testing with Samples
# -------------------------
if __name__ == "__main__":
    # Create folder if not exists
    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER)

    # Test with text samples (existing functionality)
    samples = [
        "Email me: jane.smith@company.co.uk",
        "Call me at +1 (202) 555-0183",
        "I have one apple",
        "Budget is Five thousand only",
        "Visit https://example.com for details",
        "Check www.test.org/info now",
        "Plain domain google.com should also count",
        "No contacts here!",
        "https://myvault-web.codextechnolife.com/profile/@u8120172786",
        "http://facebook.com/profile.php?id=100067107434462",
        "I live in Kolkata on Janai Road",
        "Visit MG Street, NKR Lane, India",
        "Bali",
        "Dankuni",
        "Kolkata",
        "Bally"
    ]

    for s in samples:
        text = str(s)
        result = isPersonalDetails(text)
        print(f"Text: {s!r} -> {result}")

    # Start folder watcher for new files
    start_watching(WATCH_FOLDER)
