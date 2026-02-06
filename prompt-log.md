# Prompt Log

- Owner: jessicatamin
- Created: 2026-02-06
- Source: Prompts used in Cursor (raw)
- Notes: Due to Cursor usage limit reached, this prompt log is made using GitHub Copilot where each entry below is the original prompt text submitted to the AI. No edits were made to the prompt content.

## Prompt 1
```
Build a data cleaning and validation pipeline that processes raw scraped data into clean, structured output.

Create a data cleaning function with these features:
- Remove extra whitespace and HTML artifacts
- Normalize text encoding
- Standardize date formats to ISO format
- Handle special characters appropriately
```

## Prompt 2
```
For data validation, can you add these functions to validator.py:
- Checks for required fields (title, content, url)
- Validates URL format
- Checks content length minimums
- Flags invalid records with reasons
```

## Prompt 3
```
Can you remove everything in the sample_data.json file now and add the data from jessicatamin/downloads/bbc_news.csv and put it into sample_data.json in this project file?
```

## Prompt 4
```
Change the heading of the columns in the dataset of sample_data.json
- title to heading
- description to content
- link to url
```

## Prompt 5
```
Run data cleaning on sample_data.json using cleaner.py
```

## Prompt 6
```
Please continue to work in the cleaned_output.json and run the data validation (validator.py) on the cleaned file.
```

## Prompt 7
```
Can you make the quality report with these specifications:
- Total records processed
- Valid vs. invalid counts
- Completeness percentage per field
- Common validation failures

and save it all in the same file: qualit_report.txt
```

## Prompt 8
```
Can you rename the file to "quality_report.txt"
```

## Prompt 9
```
Can you create a README.md file to show a brief 1 page documentation of what this project did
```

## Prompt 10
```
Lastly, can you compile all the prompts that i used to generate this project into a new file: prompt-log.md to document my AI-assisted development process
```

---
End of prompt entries.
