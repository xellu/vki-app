import re

def delete_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def extract_digits(text: str):
    out = ""
    for char in text:
        if char in "0123456789":
            out += char
    return out