import re

def delete_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()