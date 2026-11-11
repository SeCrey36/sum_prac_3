import re
from typing import List, Dict, Any, Optional


def luhn_checksum(card_number_str: str) -> bool:
    digits = [int(c) for c in card_number_str if c.isdigit()]
    if len(digits) != 16:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += d
    return checksum % 10 == 0


def validate_inn(inn_str: str) -> bool:
    digits = [int(c) for c in inn_str if c.isdigit()]
    if len(digits) == 10:
        coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        checksum = sum(d * c for d, c in zip(digits[:9], coefficients)) % 11
        check_digit = 0 if checksum == 10 else checksum
        return check_digit == digits[9]
    elif len(digits) == 12:
        c1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        c2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        sum1 = sum(d * c for d, c in zip(digits[:10], c1)) % 11
        check1 = 0 if sum1 == 10 else sum1
        sum2 = sum(d * c for d, c in zip(digits[:11], c2)) % 11
        check2 = 0 if sum2 == 10 else sum2
        return check1 == digits[10] and check2 == digits[11]
    return False


def validate_snils(snils_str: str) -> bool:
    digits = [int(c) for c in snils_str if c.isdigit()]
    if len(digits) != 11:
        return False
    number_digits = digits[:9]
    check_digits = digits[9] * 10 + digits[10]
    total = sum(d * (9 - idx) for idx, d in enumerate(number_digits))
    if total < 100:
        expected = total
    elif total in (100, 101):
        expected = 0
    else:
        rem = total % 101
        expected = 0 if rem in (100, 101) else rem
    return expected == check_digits


# --- Masking functions ---

def mask_passport(text: str) -> str:
    digits = re.sub(r'\D', '', text)
    if len(digits) == 10:
        return f"{digits[:2]}** ***{digits[-3:]}"
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return text[:2] + "****" + text[-3:]


def mask_inn(text: str) -> str:
    digits = re.sub(r'\D', '', text)
    if len(digits) >= 10:
        return f"{digits[:4]}{'*' * (len(digits) - 6)}{digits[-2:]}"
    return "****"


def mask_snils(text: str) -> str:
    digits = re.sub(r'\D', '', text)
    if len(digits) == 11:
        return f"{digits[:3]}-***-*** {digits[-2:]}"
    return "***-***-*** **"


def mask_phone(text: str) -> str:
    digits = re.sub(r'\D', '', text)
    if len(digits) == 11:
        prefix = "+7" if text.strip().startswith("+7") else "8"
        return f"{prefix} ({digits[1:4]}) ***-**-{digits[-2:]}"
    return text[:4] + "***" + text[-2:]


def mask_email(text: str) -> str:
    if "@" not in text:
        return text
    user, domain = text.split("@", 1)
    if len(user) <= 2:
        masked_user = user[0] + "***"
    else:
        masked_user = user[0] + "***" + user[-1]
    return f"{masked_user}@{domain}"


def mask_bank_card(text: str) -> str:
    digits = re.sub(r'\D', '', text)
    if len(digits) == 16:
        return f"**** **** **** {digits[-4:]}"
    return "**** **** **** ****"


# Regex patterns
PATTERNS = {
    "PASSPORT": re.compile(r'\b(?:\d{2}\s\d{2}|\d{4})\s+(?:№|номер|N)?\s*\d{6}\b', re.IGNORECASE),
    "SNILS": re.compile(r'\b\d{3}[-\s]\d{3}[-\s]\d{3}[-\s]\d{2}\b'),
    "INN": re.compile(r'\b(?:\d{10}|\d{12})\b'),
    "PHONE": re.compile(r'(?:\+7|8)[\s\-\(]*\d{3}[\s\-\)]*[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b'),
    "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    "BANK_CARD": re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b'),
}

PII_TYPE_NAMES = {
    "PASSPORT": "Паспорт РФ (серия и номер)",
    "SNILS": "СНИЛС",
    "INN": "ИНН",
    "PHONE": "Номер телефона",
    "EMAIL": "Адрес эл. почты",
    "BANK_CARD": "Номер банковской карты",
}


def find_pii_in_text(text: str, page_number: int = 1) -> List[Dict[str, Any]]:
    findings = []
    seen_keys = set()

    # 1. Bank Cards (verify with Luhn)
    for match in PATTERNS["BANK_CARD"].finditer(text):
        raw_val = match.group()
        digits = re.sub(r'\D', '', raw_val)
        if len(digits) == 16 and luhn_checksum(digits):
            masked = mask_bank_card(raw_val)
            key = ("BANK_CARD", masked, page_number)
            if key not in seen_keys:
                seen_keys.add(key)
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                context = text[start:end].replace('\n', ' ').strip()
                findings.append({
                    "pii_type": "BANK_CARD",
                    "type_name": PII_TYPE_NAMES["BANK_CARD"],
                    "raw_value": raw_val,
                    "masked_value": masked,
                    "page_number": page_number,
                    "context": context,
                })

    # 2. Passport RF
    for match in PATTERNS["PASSPORT"].finditer(text):
        raw_val = match.group()
        # Avoid treating 10 consecutive digits as passport if surrounded by digits
        masked = mask_passport(raw_val)
        key = ("PASSPORT", masked, page_number)
        if key not in seen_keys:
            seen_keys.add(key)
            start = max(0, match.start() - 25)
            end = min(len(text), match.end() + 25)
            context = text[start:end].replace('\n', ' ').strip()
            findings.append({
                "pii_type": "PASSPORT",
                "type_name": PII_TYPE_NAMES["PASSPORT"],
                "raw_value": raw_val,
                "masked_value": masked,
                "page_number": page_number,
                "context": context,
            })

    # 3. SNILS
    for match in PATTERNS["SNILS"].finditer(text):
        raw_val = match.group()
        # Validate or accept formatted SNILS
        digits = re.sub(r'\D', '', raw_val)
        if len(digits) == 11:
            masked = mask_snils(raw_val)
            key = ("SNILS", masked, page_number)
            if key not in seen_keys:
                seen_keys.add(key)
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                context = text[start:end].replace('\n', ' ').strip()
                findings.append({
                    "pii_type": "SNILS",
                    "type_name": PII_TYPE_NAMES["SNILS"],
                    "raw_value": raw_val,
                    "masked_value": masked,
                    "page_number": page_number,
                    "context": context,
                })

    # 4. INN
    for match in PATTERNS["INN"].finditer(text):
        raw_val = match.group()
        # If it passed INN checksum
        if validate_inn(raw_val):
            masked = mask_inn(raw_val)
            key = ("INN", masked, page_number)
            if key not in seen_keys:
                seen_keys.add(key)
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                context = text[start:end].replace('\n', ' ').strip()
                findings.append({
                    "pii_type": "INN",
                    "type_name": PII_TYPE_NAMES["INN"],
                    "raw_value": raw_val,
                    "masked_value": masked,
                    "page_number": page_number,
                    "context": context,
                })

    # 5. Phone
    for match in PATTERNS["PHONE"].finditer(text):
        raw_val = match.group()
        digits = re.sub(r'\D', '', raw_val)
        if len(digits) == 11:
            masked = mask_phone(raw_val)
            key = ("PHONE", masked, page_number)
            if key not in seen_keys:
                seen_keys.add(key)
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                context = text[start:end].replace('\n', ' ').strip()
                findings.append({
                    "pii_type": "PHONE",
                    "type_name": PII_TYPE_NAMES["PHONE"],
                    "raw_value": raw_val,
                    "masked_value": masked,
                    "page_number": page_number,
                    "context": context,
                })

    # 6. Email
    for match in PATTERNS["EMAIL"].finditer(text):
        raw_val = match.group()
        masked = mask_email(raw_val)
        key = ("EMAIL", masked, page_number)
        if key not in seen_keys:
            seen_keys.add(key)
            start = max(0, match.start() - 25)
            end = min(len(text), match.end() + 25)
            context = text[start:end].replace('\n', ' ').strip()
            findings.append({
                "pii_type": "EMAIL",
                "type_name": PII_TYPE_NAMES["EMAIL"],
                "raw_value": raw_val,
                "masked_value": masked,
                "page_number": page_number,
                "context": context,
            })

    return findings
