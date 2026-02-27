"""
Module 1 — Input Sanitization Utilities
Implements sanitization rules S-01 through S-05 from Module 1 §4.3.
"""

import re
import unicodedata


# S-02: HTML tag stripping regex
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

# S-03: Common SQL injection patterns (defence-in-depth on top of parameterised queries)
_SQL_INJECTION_PATTERNS = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|UNION|CREATE|TRUNCATE)\b"
    r"|--|;|\bOR\b\s+\d+=\d+|\bAND\b\s+\d+=\d+)",
    re.IGNORECASE,
)

# Script injection patterns
_SCRIPT_PATTERN = re.compile(
    r"(javascript\s*:|on\w+\s*=|<\s*script)",
    re.IGNORECASE,
)


def strip_html(text: str) -> str:
    """S-02: Remove all HTML tags from a string."""
    return _HTML_TAG_PATTERN.sub("", text)


def trim_whitespace(text: str) -> str:
    """S-01: Trim leading/trailing whitespace."""
    return text.strip()


def normalize_unicode(text: str) -> str:
    """S-04: Apply NFC Unicode normalization for consistent comparison."""
    return unicodedata.normalize("NFC", text)


def contains_sql_injection(text: str) -> bool:
    """S-03: Detect common SQL injection patterns (defence-in-depth)."""
    return bool(_SQL_INJECTION_PATTERNS.search(text))


def contains_script_injection(text: str) -> bool:
    """S-02 extended: Detect script/JS injection patterns."""
    return bool(_SCRIPT_PATTERN.search(text))


def sanitize_string(text: str | None, *, allow_html: bool = False) -> str | None:
    """
    Full sanitization pipeline for a single string input.
    Applies: S-01 (trim) → S-02 (strip HTML) → S-04 (unicode NFC).

    Returns sanitised string or None if input is None.
    Raises ValueError if SQL or script injection is detected.
    """
    if text is None:
        return None

    # S-01: Trim
    text = trim_whitespace(text)

    # S-04: Unicode normalisation
    text = normalize_unicode(text)

    # S-03: SQL injection check (defence-in-depth) — before stripping HTML
    if contains_sql_injection(text):
        raise ValueError("Input contains potentially unsafe patterns.")

    # Script injection check — before stripping HTML so <script> tags are caught
    if contains_script_injection(text):
        raise ValueError("Input contains potentially unsafe script content.")

    # S-02: Strip HTML tags (after security checks)
    if not allow_html:
        text = strip_html(text)

    return text


def sanitize_string_list(items: list[str] | None) -> list[str] | None:
    """Sanitize each string in a list. Returns None if input is None."""
    if items is None:
        return None
    return [sanitize_string(item) for item in items]
