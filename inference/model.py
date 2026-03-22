# inference/model.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from inference.prompt import SKILL_INFERENCE_PROMPT, RESUME_INFERENCE_PROMPT

load_dotenv()


def _configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    genai.configure(api_key=api_key)


def _repair_json(text: str) -> str:
    """
    Closes any unclosed brackets/braces in a truncated JSON string.
    Handles cases where Gemini cuts off mid-response.
    """
    text = text.rstrip()
    if text.endswith(","):
        text = text[:-1]

    open_braces  = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")

    text += "]" * open_brackets
    text += "}" * open_braces

    return text


def _parse_response(raw_text: str) -> dict:
    cleaned = raw_text.strip()

    # Strip markdown fences
    cleaned = cleaned.removeprefix("```json").removeprefix("```")
    cleaned = cleaned.removesuffix("```")
    cleaned = cleaned.strip()

    # Extract from first {
    start = cleaned.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response.")
    cleaned = cleaned[start:]

    # Auto-repair truncated JSON
    cleaned = _repair_json(cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse model response as JSON.\n"
            f"Raw response:\n{raw_text}\nError: {e}"
        )


def infer_skills(certificate_data: dict) -> dict:
    _configure_gemini()

    model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    message = [
        {
            "mime_type": certificate_data["mime_type"],
            "data": certificate_data["data"]
        },
        SKILL_INFERENCE_PROMPT
    ]

    response = model.generate_content(
        message,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=8192
        )
    )

    raw_text = response.text
    result   = _parse_response(raw_text)

    return result


def infer_resume_skills(resume_pages: list) -> dict:
    _configure_gemini()

    model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    # Send all page images followed by the prompt
    message = [
        {"mime_type": page["mime_type"], "data": page["data"]}
        for page in resume_pages
    ] + [RESUME_INFERENCE_PROMPT]

    response = model.generate_content(
        message,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=16384
        )
    )

    raw_text = response.text
    result   = _parse_response(raw_text)

    return result