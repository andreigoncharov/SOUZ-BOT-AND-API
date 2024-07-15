import re

text = '067 952 71 00'


def normalize_phone_number_plus(phone_number):
    cleaned_number = re.sub(r'\D', '', phone_number)

    if len(cleaned_number) == 10 and cleaned_number.startswith('0'):
        normalized_number = '+380' + cleaned_number[1:]
    elif len(cleaned_number) == 12 and cleaned_number.startswith('380'):
        normalized_number = '+380' + cleaned_number[3:]
    elif len(cleaned_number) == 13 and cleaned_number.startswith('+380'):
        normalized_number = cleaned_number
    else:
        return ''
    return normalized_number


print(normalize_phone_number_plus(text))