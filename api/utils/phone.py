import re

from api.const import TELECOM_NUMBER


def extract_phone(data):
    pattern1 = re.compile(r'\b(0[1-9])+([0-9]{8})\b')
    pattern2 = re.compile(r'\b(84[1-9])+([0-9]{8})\b')

    regex = re.compile(pattern1)
    result = regex.search(data)
    if not result:
        return None
    return result.group(0)


def classify_telecom_number(dstchannel):
    if 'VTL' in dstchannel.upper():
        return TELECOM_NUMBER.VIETTEL
    if 'VMS' in dstchannel.upper():
        return TELECOM_NUMBER.MOBI
    if 'VNP' in dstchannel.upper():
        return TELECOM_NUMBER.VINA
    if 'OTHER' in dstchannel.upper():
        return TELECOM_NUMBER.OTHER
    if 'VINAPHONE' in dstchannel.upper():
        return TELECOM_NUMBER.VINA
    if 'MOBIFONE' in dstchannel.upper():
        return TELECOM_NUMBER.MOBI
    if 'VIETTEL' in dstchannel.upper():
        return TELECOM_NUMBER.VIETTEL

    return TELECOM_NUMBER.OTHER

# def classify_telecom_number(number):
#     if len(number) != 10:
#         return TELECOM_NUMBER.OTHER
#
#     viettel = ['086', '096', '097', '098', '039', '038', '037', '036', '035', '034', '033', '032']
#     vina = ['091', '094', '088', '083', '084', '085', '081', '082']
#     mobi = ['070', '079', '077', '076', '078', '089', '090', '093']
#
#     for head in viettel:
#         if number.startswith(head):
#             return TELECOM_NUMBER.VIETTEL
#
#     for head in vina:
#         if number.startswith(head):
#             return TELECOM_NUMBER.VINA
#
#     for head in mobi:
#         if number.startswith(head):
#             return TELECOM_NUMBER.MOBI
#
#     return TELECOM_NUMBER.OTHER
