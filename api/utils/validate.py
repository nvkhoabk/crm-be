import re


def check_phone_number(value):
    pattern1 = re.compile("^(0[1-9])+([0-9]{8})$")
    pattern2 = re.compile("^(84[1-9])+([0-9]{8})$")
    if pattern1.match(value) is None and pattern2.match(value) is None:
        return None
    if value.find('84') == 0:
        value = value.replace('84', '0', 1)
    return value
