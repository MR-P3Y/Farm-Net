from sqlalchemy import case, func, literal

from app.common.search import normalize_search_text


_SQL_REPLACEMENTS = (
    ("ي", "ی"), ("ى", "ی"), ("ك", "ک"), ("ة", "ه"), ("ۀ", "ه"),
    ("آ", "ا"), ("أ", "ا"), ("إ", "ا"), ("ؤ", "و"), ("ئ", "ی"),
    ("ـ", ""), ("\u200c", " "), ("\u200d", " "), ("\u00a0", " "),
    ("َ", ""), ("ِ", ""), ("ُ", ""), ("ّ", ""), ("ْ", ""),
    ("ً", ""), ("ٍ", ""), ("ٌ", ""), ("ٰ", ""),
    ("۰", "0"), ("۱", "1"), ("۲", "2"), ("۳", "3"), ("۴", "4"),
    ("۵", "5"), ("۶", "6"), ("۷", "7"), ("۸", "8"), ("۹", "9"),
    ("٠", "0"), ("١", "1"), ("٢", "2"), ("٣", "3"), ("٤", "4"),
    ("٥", "5"), ("٦", "6"), ("٧", "7"), ("٨", "8"), ("٩", "9"),
)


def normalized_search_expression(column):
    expression = func.lower(func.coalesce(column, ""))
    for source, target in _SQL_REPLACEMENTS:
        expression = func.replace(expression, source, target)
    for _ in range(3):
        expression = func.replace(expression, "  ", " ")
    return expression


def search_match_expression(query: str, *columns):
    normalized = normalize_search_text(query)
    pattern = f"%{normalized}%"
    expressions = [normalized_search_expression(column).like(pattern) for column in columns]
    result = expressions[0]
    for expression in expressions[1:]:
        result = result | expression
    return result


def search_relevance_expression(query: str, title_column, *secondary_columns):
    normalized = normalize_search_text(query)
    title = normalized_search_expression(title_column)
    secondary_match = literal(False)
    for column in secondary_columns:
        secondary_match = secondary_match | normalized_search_expression(column).like(
            f"%{normalized}%"
        )
    return case(
        (title == normalized, 100),
        (title.like(f"{normalized}%"), 80),
        (title.like(f"%{normalized}%"), 60),
        (secondary_match, 30),
        else_=0,
    )
