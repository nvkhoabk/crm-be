import re


def extract_phone(data):
    pattern1 = re.compile(r'\b(0[1-9])+([0-9]{8})\b')
    pattern2 = re.compile(r'\b(84[1-9])+([0-9]{8})\b')
    
    regex = re.compile(pattern1)
    result = regex.search(data)
    if not result:
        return None
    return result.group(0)
