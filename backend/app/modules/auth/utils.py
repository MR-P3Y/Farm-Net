import re


def normalize_iran_phone(phone: str | None) -> str | None:
    if not phone:
        return None

    value = phone.strip()
    value = value.replace(" ", "")
    value = value.replace("-", "")
    value = value.replace("(", "")
    value = value.replace(")", "")

    # Persian/Arabic digits to English digits
    translation_table = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789",
    )
    value = value.translate(translation_table)

    # Remove leading +
    if value.startswith("+"):
        value = value[1:]

    # 0098912...
    if value.startswith("0098"):
        value = value[2:]

    # 0912...
    if value.startswith("0") and len(value) == 11:
        value = "98" + value[1:]

    # 912...
    if value.startswith("9") and len(value) == 10:
        value = "98" + value

    if not re.fullmatch(r"989\d{9}", value):
        raise ValueError("Invalid Iranian phone number")

    return value