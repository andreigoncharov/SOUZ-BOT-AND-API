import re

text = '093-660-28-69      '


def normalize_phone_number(phone_number):
    phone_numbers = phone_number.split()
    normalized_numbers = []
    for number in phone_numbers:
        cleaned_numbers = re.findall(r'\d+', number)
        cleaned_number = ''.join(cleaned_numbers)
        if cleaned_number.startswith('0'):
            cleaned_number = '+380' + cleaned_number[1:]
        elif cleaned_number.startswith('380'):
            cleaned_number = '+380' + cleaned_number[3:]
        elif cleaned_number.startswith('+380'):
            pass
        else:
            return ""
        normalized_numbers.append(cleaned_number)
    return ' '.join(normalized_numbers)


print(normalize_phone_number(text))