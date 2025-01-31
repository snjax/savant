# Report Analyzer

A tool to extract critical and high-severity issues from audit reports (PDF/Markdown).

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_API_BASE_URL` (optional): Custom OpenAI-compatible API endpoint
- `OPENAI_TIMEOUT` (optional): API timeout in milliseconds (default: 1000000)

## Usage

```bash
python main.py path/to/report.pdf
```

The tool will:
1. Extract critical/high-severity issues from the report
2. Generate a structured markdown output in `issues.md`
3. Print the results to stdout

## Output Format
Issues are formatted in markdown with the following structure:

\# Issue title \
\#\# Severity \
\#\# File URL \
\#\# Line numbers (if available) \
\#\# Description
