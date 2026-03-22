# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CertLens** — an AI-powered system that analyzes professional certificates (PDF, JPG, PNG, WEBP) using Google Gemini's vision API to extract and infer skills, then generates formatted PDF reports.

## Setup

```bash
pip install -r requirements.txt
```

Requires a `.env` file in the project root:
```
GEMINI_API_KEY=<your_key>
```

## Running the Application

```bash
# Certificate inference (CLI)
python main.py --file path/to/cert.pdf
python main.py --file path/to/cert.pdf --output results.json --report report.pdf

# Resume inference (CLI)
python main.py --mode resume --file path/to/resume.pdf
python main.py --mode resume --file path/to/resume.pdf --output results.json --report resume_report.pdf

# Web UI
streamlit run app.py

# Check available Gemini models
python check_models.py
```

## Architecture

Two parallel inference pipelines share a common Gemini client and JSON repair layer.

```
app.py (Streamlit UI)  /  main.py (CLI)
  ├── inference/extractor.py
  │     load_certificate()       → single base64 JPEG dict (first page only)
  │     load_resume()            → list of base64 JPEG dicts (all pages, capped at 10)
  ├── inference/model.py
  │     infer_skills()           → sends 1 image + SKILL_INFERENCE_PROMPT to Gemini
  │     infer_resume_skills()    → sends N images + RESUME_INFERENCE_PROMPT to Gemini
  ├── inference/prompt.py
  │     SKILL_INFERENCE_PROMPT   — certificate extraction strategy
  │     RESUME_INFERENCE_PROMPT  — resume extraction strategy
  └── report/
        styles.py               — shared colors, ParagraphStyles, ConfidenceBar, footer
        generator.py            → generate_report()        — certificate PDF
        resume_generator.py     → generate_resume_report() — resume PDF
```

**Key design decisions:**
- All files are rendered to images before sending to Gemini (model receives images, not text)
- Resumes render all pages (up to 10) at 2x zoom; certificates render only page 0
- `gemini-2.5-flash` at `temperature=0.3`; certificates use `max_output_tokens=8192`, resumes use `16384`
- `_repair_json()` in `model.py` auto-closes truncated JSON from the API
- Shared report styles live in `report/styles.py` to avoid duplication between the two report generators

**Certificate JSON schema:**
```json
{
  "certificate": { "title": "", "issuer": "", "domain": "", "level": "" },
  "skills": [{ "skill": "", "type": "explicit|implicit", "confidence": 0.0, "reason": "" }]
}
```

**Resume JSON schema:**
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
