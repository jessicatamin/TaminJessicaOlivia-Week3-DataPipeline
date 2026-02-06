"""
Data cleaning and validation pipeline for raw scraped data.
Processes raw scraped data into clean, structured output.
"""

import html
import re
import unicodedata
from datetime import datetime
from typing import Any, Callable, Optional, Union


# -----------------------------------------------------------------------------
# Text Cleaning
# -----------------------------------------------------------------------------

def remove_html_artifacts(text: str) -> str:
    """
    Remove HTML tags and decode HTML entities from text.
    Handles: <tags>, &nbsp;, &amp;, &quot;, &#39; etc.
    """
    if not isinstance(text, str):
        return str(text)
    # Decode HTML entities first (e.g. &amp; -> &, &nbsp; -> space)
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text


def remove_extra_whitespace(text: str) -> str:
    """
    Normalize whitespace: collapse multiple spaces, strip leading/trailing.
    Replaces newlines and tabs with single space.
    """
    if not isinstance(text, str):
        return str(text)
    # Replace various whitespace characters with standard space
    text = re.sub(r'[\t\n\r\f\v]+', ' ', text)
    # Collapse multiple spaces into one
    text = re.sub(r' +', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()


def normalize_text_encoding(text: str) -> str:
    """
    Normalize text encoding using Unicode normalization (NFC).
    Handles composition (é as single char vs e + combining accent).
    Also attempts to fix common mojibake from wrong encoding.
    """
    if not isinstance(text, str):
        return str(text)
    # Normalize to NFC (canonical composition)
    text = unicodedata.normalize('NFC', text)
    # Common mojibake fixes (e.g. utf-8 decoded as latin-1)
    mojibake_map = {
        '\u201c': '"',  # " (left double quote)
        '\u201d': '"',  # " (right double quote)
        '\u2018': "'",  # ' (left single quote)
        '\u2019': "'",  # ' (right single quote / apostrophe)
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u00a0': ' ',  # non-breaking space
        '\ufffd': '',   # replacement character (invalid)
    }
    for bad, good in mojibake_map.items():
        text = text.replace(bad, good)
    return text


def handle_special_characters(text: str, replace_invalid: bool = True) -> str:
    """
    Handle special characters appropriately:
    - Replace problematic Unicode (control chars, replacement char)
    - Optionally normalize to ASCII for strict output
    """
    if not isinstance(text, str):
        return str(text)
    # Remove control characters (0x00-0x1F, 0x7F-0x9F)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Cc')
    if replace_invalid:
        # Replace replacement character (U+FFFD) with empty
        text = text.replace('\ufffd', '')
    return text


def clean_text(
    text: str,
    remove_html: bool = True,
    normalize_whitespace: bool = True,
    normalize_encoding: bool = True,
    handle_special: bool = True,
) -> str:
    """
    Full text cleaning pipeline. Applies all cleaning steps in correct order.
    """
    if text is None:
        return ''
    text = str(text)
    if remove_html:
        text = remove_html_artifacts(text)
    if normalize_encoding:
        text = normalize_text_encoding(text)
    if handle_special:
        text = handle_special_characters(text)
    if normalize_whitespace:
        text = remove_extra_whitespace(text)
    return text


# -----------------------------------------------------------------------------
# Date Standardization
# -----------------------------------------------------------------------------

# Common date format patterns (strptime codes)
DATE_FORMATS = [
    '%Y-%m-%d',
    '%d/%m/%Y',
    '%m/%d/%Y',
    '%d-%m-%Y',
    '%m-%d-%Y',
    '%Y/%m/%d',
    '%d %B %Y',   # 05 February 2025
    '%d %b %Y',   # 05 Feb 2025
    '%B %d, %Y',  # February 05, 2025
    '%b %d, %Y',  # Feb 05, 2025
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y-%m-%d %H:%M:%S',
    '%d/%m/%y',
    '%m/%d/%y',
    '%Y%m%d',
]


def standardize_date(
    value: Union[str, datetime, None],
    output_format: str = '%Y-%m-%d',
    return_none_on_fail: bool = True,
) -> Optional[str]:
    """
    Parse various date formats and standardize to ISO format (YYYY-MM-DD).
    Supports: ISO, US, UK, and common scraped formats.
    """
    if value is None or value == '':
        return None
    if isinstance(value, datetime):
        return value.strftime(output_format)
    value = str(value).strip()
    if not value:
        return None
    # Clean the string first
    value = clean_text(value, remove_html=True, normalize_whitespace=True)
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime(output_format)
        except ValueError:
            continue
    # Try flexible parsing with common separators
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', value)
    if match:
        return f'{match.group(1)}-{match.group(2)}-{match.group(3)}'
    if return_none_on_fail:
        return None
    return value


# -----------------------------------------------------------------------------
# Record & Pipeline Cleaning
# -----------------------------------------------------------------------------

# Fields that should be cleaned as text
DEFAULT_TEXT_FIELDS = {'name', 'title', 'description', 'category', 'email', 'url', 'content'}

# Fields that may contain dates
DEFAULT_DATE_FIELDS = {'date', 'created', 'updated', 'published', 'scraped_at', 'timestamp'}


def clean_record(
    record: dict,
    text_fields: Optional[set] = None,
    date_fields: Optional[set] = None,
    custom_cleaners: Optional[dict[str, Callable[[Any], Any]]] = None,
) -> dict:
    """
    Clean a single record. Applies text cleaning to string fields,
    date standardization to date fields, and custom cleaners per field.
    """
    text_fields = text_fields or DEFAULT_TEXT_FIELDS
    date_fields = date_fields or set()
    custom_cleaners = custom_cleaners or {}
    cleaned = {}
    for key, value in record.items():
        key_lower = key.lower()
        if key in custom_cleaners:
            cleaned[key] = custom_cleaners[key](value)
        elif key_lower in {f.lower() for f in date_fields} or key in date_fields:
            cleaned[key] = standardize_date(value)
        elif key_lower in {f.lower() for f in text_fields} or key in text_fields:
            if isinstance(value, str):
                cleaned[key] = clean_text(value)
            else:
                cleaned[key] = value
        elif isinstance(value, str):
            # Clean any string field by default
            cleaned[key] = clean_text(value)
        else:
            cleaned[key] = value
    return cleaned


def clean_data(
    data: Union[list[dict], dict],
    text_fields: Optional[set] = None,
    date_fields: Optional[set] = None,
    custom_cleaners: Optional[dict[str, Callable[[Any], Any]]] = None,
) -> list[dict]:
    """
    Clean a list of records (or single record wrapped in list).
    Returns list of cleaned records.
    """
    if isinstance(data, dict):
        data = [data]
    return [
        clean_record(r, text_fields, date_fields, custom_cleaners)
        for r in data
    ]
