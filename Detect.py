import re
import spacy

nlp = spacy.load("en_core_web_sm")

email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
url_pattern = re.compile(r'(https?:\/\/[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)')
PLATFORM_DOMAIN = "myvault-web.codextechnolife.com"

number_words = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million", "billion"
}

def isEmail(text: str) -> bool:
    return bool(email_pattern.search(text))

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
    if hasNumberWords(text):
        return True
    if hasNumber(text):
        return True
    if hasAddress(text):
        return True
    return False

if __name__ == "__main__":
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
        "https://myvault-web.codextechnolife.com/home",
        "http://myvault-web.codextechnolife.com/about",
        "http://facebook.com/profile.php?id=100067107434462",
        "This is just a normal sentence with no URLs",
        "Contact me at test@example.com or visit example.org",
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
