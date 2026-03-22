# inference/prompt.py

SKILL_INFERENCE_PROMPT = """
You are an expert skill inference engine for professional certificates and credentials.

Analyze this certificate carefully and extract all skills — both explicit and implicit.

Return ONLY a valid JSON object with this exact structure (no markdown, no backticks, no extra text):
{
  "certificate": {
    "title": "Full certificate title",
    "issuer": "Issuing organization",
    "domain": "Broad domain (e.g. Cloud Computing, Data Science, Project Management)",
    "level": "Beginner / Intermediate / Advanced / Professional"
  },
  "skills": [
    {
      "skill": "Skill name",
      "type": "explicit",
      "confidence": 0.97,
      "reason": "One sentence explaining why this skill is inferred"
    }
  ]
}

Rules:
- "explicit" = directly tested or mentioned in the certificate
- "implicit" = logically required or strongly implied by the domain / level / issuer
- Confidence scoring:
  - 0.90 - 1.00 : directly tested or stated in the certificate
  - 0.70 - 0.89 : strongly implied by the domain or level
  - 0.50 - 0.69 : reasonably inferred but indirect
  - below 0.50  : skip entirely
- Sort skills by confidence score descending
- Include between 6 to 12 skills total
- Keep each reason to one short sentence
- Return ONLY the JSON object. No extra text whatsoever.
"""