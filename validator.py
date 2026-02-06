"""
Data validation module for scraped data.
Checks required fields, URL format, content length, and flags invalid records with reasons.
"""

import re
from typing import Any, List, Optional, Tuple
from urllib.parse import urlparse


# -----------------------------------------------------------------------------
# Required Fields
# -----------------------------------------------------------------------------

REQUIRED_FIELDS = frozenset({'title', 'content', 'url'})


def check_required_fields(
    record: dict,
    required: Optional[frozenset] = None,
    field_aliases: Optional[dict] = None,
) -> list[str]:
    """
    Check that record contains all required fields with non-empty values.
    Returns list of validation error messages (empty if valid).

    field_aliases: map canonical names to actual keys, e.g. {'title': 'name'}
    """
    required = required or REQUIRED_FIELDS
    field_aliases = field_aliases or {}
    errors = []

    for field in required:
        key = field_aliases.get(field, field)
        value = record.get(key)

        if value is None or value == '':
            errors.append(f"missing required field: {field}")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"required field '{field}' is empty or whitespace-only")

    return errors


# -----------------------------------------------------------------------------
# URL Validation
# -----------------------------------------------------------------------------

# Regex for URL validation (supports http, https, and common schemes)
URL_PATTERN = re.compile(
    r'^https?://'  # scheme
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
    r'localhost|'  # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)


def validate_url_format(url: Any, field_name: str = 'url') -> Optional[str]:
    """
    Validate that url is a well-formed HTTP/HTTPS URL.
    Returns error message if invalid, None if valid.
    """
    if url is None or url == '':
        return f"missing {field_name}"

    url_str = str(url).strip()
    if not url_str:
        return f"{field_name} is empty"

    try:
        parsed = urlparse(url_str)
        if parsed.scheme not in ('http', 'https'):
            return f"{field_name}: invalid scheme (expected http or https)"
        if not parsed.netloc:
            return f"{field_name}: missing host/domain"
        # Basic format check
        if not URL_PATTERN.match(url_str):
            return f"{field_name}: malformed URL format"
    except Exception as e:
        return f"{field_name}: invalid URL - {e}"

    return None


# -----------------------------------------------------------------------------
# Content Length
# -----------------------------------------------------------------------------

def check_content_length_minimum(
    value: Any,
    minimum: int,
    field_name: str = 'content',
) -> Optional[str]:
    """
    Check that string content meets minimum length.
    Returns error message if too short, None if valid.
    """
    if value is None:
        return f"{field_name}: missing (need at least {minimum} chars)"

    text = str(value)
    length = len(text.strip())

    if length < minimum:
        return f"{field_name}: too short ({length} chars, minimum {minimum})"

    return None


# -----------------------------------------------------------------------------
# Record Validation & Flagging
# -----------------------------------------------------------------------------

ValidationResult = Tuple[bool, List[str]]  # (is_valid, list of reasons)


def validate_record(
    record: dict,
    required_fields: Optional[frozenset] = None,
    field_aliases: Optional[dict] = None,
    url_field: str = 'url',
    content_field: str = 'content',
    content_min_length: int = 1,
) -> ValidationResult:
    """
    Validate a single record. Returns (is_valid, list of reasons).

    - Checks required fields (title, content, url by default)
    - Validates URL format
    - Checks content length minimum
    - Collects all reasons for invalid records
    """
    reasons = []

    # Required fields
    reasons.extend(
        check_required_fields(record, required_fields, field_aliases)
    )

    # URL format (skip if missing - already caught by required check)
    url_key = field_aliases.get('url', url_field) if field_aliases else url_field
    url_value = record.get(url_key)
    if url_value is not None and str(url_value).strip():
        url_error = validate_url_format(url_value, url_field)
        if url_error:
            reasons.append(url_error)

    # Content length minimum (skip if missing/empty - already caught by required check)
    content_key = field_aliases.get('content', content_field) if field_aliases else content_field
    content_value = record.get(content_key)
    if content_value is not None and str(content_value).strip():
        length_error = check_content_length_minimum(
            content_value, content_min_length, content_field
        )
        if length_error:
            reasons.append(length_error)

    is_valid = len(reasons) == 0
    return (is_valid, reasons)


def validate_data(
    data: List[dict],
    required_fields: Optional[frozenset] = None,
    field_aliases: Optional[dict] = None,
    url_field: str = 'url',
    content_field: str = 'content',
    content_min_length: int = 1,
) -> Tuple[List[dict], List[Tuple[int, dict, List[str]]]]:
    """
    Validate a list of records. Returns:
    - valid_records: list of records that passed validation
    - invalid_records: list of (index, record, reasons) for failed records
    """
    valid_records = []
    invalid_records = []

    for i, record in enumerate(data):
        is_valid, reasons = validate_record(
            record,
            required_fields=required_fields,
            field_aliases=field_aliases,
            url_field=url_field,
            content_field=content_field,
            content_min_length=content_min_length,
        )
        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append((i, record, reasons))

    return valid_records, invalid_records
