# AI Skill Inferencing System

An AI-powered system that analyzes professional certificates and resumes (PDF, JPG, PNG, WEBP) using Google Gemini's vision API to extract and infer skills, then generates formatted PDF reports.

## Features

**Certificate Analysis**
- Detects certificate title, issuer, domain, and level
- Extracts explicit and implicit skills with confidence scores (50%–100%)
- Generates a professional PDF report

**Resume Analysis**
- Extracts candidate profile, work experience, and education
- Infers skills with proficiency levels (Beginner → Expert)
- Supports multi-page PDFs (up to 10 pages)
- Generates a detailed PDF report

## Setup

**Prerequisites:** Python 3.10+

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

> Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

## Usage

### Web UI (Streamlit)

```bash
streamlit run app.py
```

Upload a certificate or resume from the sidebar, click **Analyze**, then download the PDF report or JSON results.

### CLI

**Certificate inference:**
```bash
python main.py --file path/to/cert.pdf
python main.py --file path/to/cert.pdf --output results.json --report report.pdf
```

**Resume inference:**
```bash
python main.py --mode resume --file path/to/resume.pdf
python main.py --mode resume --file path/to/resume.pdf --output results.json --report resume_report.pdf
```

**CLI arguments:**

| Argument   | Required | Description                              |
|------------|----------|------------------------------------------|
| `--file`   | Yes      | Path to input file (PDF, JPG, PNG, WEBP) |
| `--mode`   | No       | `certificate` (default) or `resume`      |
| `--output` | No       | Path to save raw JSON results            |
| `--report` | No       | Path to save PDF report                  |

### Check available Gemini models

```bash
python check_models.py
```

## Project Structure

```
├── app.py                    # Streamlit web UI
├── main.py                   # CLI entry point
├── check_models.py           # Utility to list available Gemini models
├── inference/
│   ├── extractor.py          # File loading & image conversion
│   ├── model.py              # Gemini API calls & JSON repair
│   └── prompt.py             # Inference prompts
└── report/
    ├── styles.py             # Shared PDF styles and colors
    ├── generator.py          # Certificate PDF report generator
    └── resume_generator.py   # Resume PDF report generator
```

## Output Schemas

**Certificate:**
```json
{
  "certificate": { "title": "", "issuer": "", "domain": "", "level": "" },
  "skills": [{ "skill": "", "type": "explicit|implicit", "confidence": 0.0, "reason": "" }]
}
```

**Resume:**
```json
{
  "resume": {
    "candidate_name": "", "summary": "", "total_experience_years": 0,
    "education": [{ "degree": "", "institution": "", "year": "" }],
    "experience": [{ "title": "", "company": "", "duration": "" }]
  },
  "skills": [{ "skill": "", "proficiency": "Beginner|Intermediate|Advanced|Expert", "confidence": 0.0, "source": "", "reason": "" }]
}
```

## Dependencies

| Package               | Purpose                     |
|-----------------------|-----------------------------|
| `google-generativeai` | Gemini vision API           |
| `pymupdf`             | PDF to image conversion     |
| `Pillow`              | Image processing            |
| `reportlab`           | PDF report generation       |
| `streamlit`           | Web UI                      |
| `python-dotenv`       | Environment variable loading|
