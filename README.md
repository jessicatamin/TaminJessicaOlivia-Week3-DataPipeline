# Data Cleaning & Validation Pipeline

A Python pipeline that processes raw scraped data into clean, structured, validated JSON output. This project ingests BBC News RSS data, applies cleaning and validation, and produces a quality-assured dataset with a detailed report.

## Overview

The pipeline has three stages:

1. **Input** — Raw data (`sample_data.json`) with fields: `heading`, `content`, `url`, `pubDate`, `guid`
2. **Cleaning** — Normalize text, remove artifacts, standardize formats via `cleaner.py`
3. **Validation** — Check required fields, URL format, and content rules via `validator.py`

Output is written to `cleaned_output.json`; invalid records are filtered out and reported in `quality_report.txt`.

## Project Files

| File | Description |
|------|-------------|
| `cleaner.py` | Data cleaning functions |
| `validator.py` | Validation rules and record flagging |
| `run_pipeline.py` | Orchestrates cleaning (validation run separately) |
| `sample_data.json` | Input: raw BBC news records |
| `cleaned_output.json` | Output: cleaned and validated records |
| `quality_report.txt` | Summary stats and validation failures |

## Data Cleaning (`cleaner.py`)

- **Whitespace & HTML** — Strip tags, decode entities (`&amp;`, `&nbsp;`), collapse extra spaces
- **Encoding** — Unicode NFC normalization; fix smart quotes, dashes, non-breaking spaces
- **Dates** — Parse multiple formats and convert to ISO (`YYYY-MM-DD`)
- **Special characters** — Remove control chars and replacement characters

## Data Validation (`validator.py`)

- **Required fields** — Ensures `title` (alias: `heading`), `content`, `url` are present and non-empty
- **URL format** — Validates HTTP/HTTPS URLs
- **Content length** — Enforces minimum length
- **Invalid records** — Returns reasons for each failed record

## Usage

**Run cleaning only:**
```bash
python run_pipeline.py
```

**Full pipeline (clean + validate + report):**
```python
from cleaner import clean_data
from validator import validate_data

raw = ...  # load from JSON
cleaned = clean_data(raw, text_fields={'heading','content','url','guid'}, date_fields={'pubDate'})
valid, invalid = validate_data(cleaned, field_aliases={'title': 'heading'})
```

## Results

For the BBC News dataset (42,115 records):

- **Valid:** 42,114 records
- **Invalid:** 1 record (malformed URL)
- **Field completeness:** 100% for `heading`, `content`, `url`, `guid` in valid records
