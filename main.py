# main.py

import argparse
import json
import os
from inference.extractor import load_certificate, load_resume
from inference.model import infer_skills, infer_resume_skills
from report.generator import generate_report
from report.resume_generator import generate_resume_report


def print_results(result: dict):
    cert   = result.get("certificate", {})
    skills = result.get("skills", [])

    print("\n" + "=" * 60)
    print("  CERTIFICATE DETECTED")
    print("=" * 60)
    print(f"  Title   : {cert.get('title', 'N/A')}")
    print(f"  Issuer  : {cert.get('issuer', 'N/A')}")
    print(f"  Domain  : {cert.get('domain', 'N/A')}")
    print(f"  Level   : {cert.get('level', 'N/A')}")
    print("=" * 60)

    explicit = [s for s in skills if s.get("type") == "explicit"]
    implicit = [s for s in skills if s.get("type") == "implicit"]

    print(f"\n  INFERRED SKILLS ({len(skills)} total — {len(explicit)} explicit, {len(implicit)} implicit)\n")
    print(f"  {'#':<4} {'Skill':<35} {'Type':<10} {'Confidence'}")
    print(f"  {'-'*4} {'-'*35} {'-'*10} {'-'*10}")

    for i, skill in enumerate(skills, 1):
        name       = skill.get("skill", "N/A")
        skill_type = skill.get("type", "N/A")
        confidence = skill.get("confidence", 0)
        reason     = skill.get("reason", "")
        bar        = _confidence_bar(confidence)

        print(f"  {i:<4} {name:<35} {skill_type:<10} {bar} {confidence:.0%}")
        print(f"       ↳ {reason}")
        print()

    print("=" * 60 + "\n")


def print_resume_results(result: dict):
    resume = result.get("resume", {})
    skills = result.get("skills", [])

    exp_years = resume.get("total_experience_years", 0)
    exp_label = f"{exp_years} year{'s' if exp_years != 1 else ''}"

    print("\n" + "=" * 60)
    print("  RESUME ANALYSED")
    print("=" * 60)
    print(f"  Candidate : {resume.get('candidate_name', 'N/A')}")
    print(f"  Experience: {exp_label}")
    print(f"  Summary   : {resume.get('summary', 'N/A')}")
    print("=" * 60)

    experience = resume.get("experience", [])
    if experience:
        print("\n  WORK EXPERIENCE")
        for exp in experience:
            print(f"    • {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})")

    education = resume.get("education", [])
    if education:
        print("\n  EDUCATION")
        for edu in education:
            print(f"    • {edu.get('degree', '')} — {edu.get('institution', '')} ({edu.get('year', '')})")

    levels = ["Expert", "Advanced", "Intermediate", "Beginner"]
    counts = {lvl: sum(1 for s in skills if s.get("proficiency") == lvl) for lvl in levels}

    print(f"\n  INFERRED SKILLS ({len(skills)} total)")
    parts = " | ".join(f"{lvl}: {counts[lvl]}" for lvl in levels)
    print(f"  {parts}\n")
    print(f"  {'#':<4} {'Skill':<35} {'Proficiency':<14} {'Confidence'}")
    print(f"  {'-'*4} {'-'*35} {'-'*14} {'-'*10}")

    for i, skill in enumerate(skills, 1):
        name        = skill.get("skill", "N/A")
        proficiency = skill.get("proficiency", "N/A")
        confidence  = skill.get("confidence", 0)
        reason      = skill.get("reason", "")
        bar         = _confidence_bar(confidence)

        print(f"  {i:<4} {name:<35} {proficiency:<14} {bar} {confidence:.0%}")
        print(f"       ↳ {reason}")
        print()

    print("=" * 60 + "\n")


def _confidence_bar(confidence: float) -> str:
    filled = int(confidence * 10)
    empty  = 10 - filled
    return f"[{'█' * filled}{'░' * empty}]"


def save_results(result: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"  Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="CertLens — Infer skills from certificates and resumes using Gemini AI"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to file (JPG, PNG, WEBP, PDF)"
    )
    parser.add_argument(
        "--mode",
        required=False,
        default="certificate",
        choices=["certificate", "resume"],
        help="Analysis mode: 'certificate' (default) or 'resume'"
    )
    parser.add_argument(
        "--report",
        required=False,
        default=None,
        help="Optional: path to save PDF report (e.g. reports/report.pdf)"
    )
    parser.add_argument(
        "--output",
        required=False,
        default=None,
        help="Optional: path to save raw JSON results (e.g. results.json)"
    )

    args = parser.parse_args()

    if args.mode == "resume":
        print(f"\n  Loading resume: {args.file}")
        pages = load_resume(args.file)
        print(f"  Resume loaded ({len(pages)} page(s)). Sending to Gemini...")

        result = infer_resume_skills(pages)
        print_resume_results(result)

        if args.output:
            save_results(result, args.output)

        if args.report:
            os.makedirs(os.path.dirname(args.report), exist_ok=True) \
                if os.path.dirname(args.report) else None
            print(f"  Generating PDF report...")
            path = generate_resume_report(result, args.report)
            print(f"  ✅ Report saved to: {path}\n")

    else:
        print(f"\n  Loading certificate: {args.file}")
        certificate_data = load_certificate(args.file)
        print("  Certificate loaded. Sending to Gemini...")

        result = infer_skills(certificate_data)
        print_results(result)

        if args.output:
            save_results(result, args.output)

        if args.report:
            os.makedirs(os.path.dirname(args.report), exist_ok=True) \
                if os.path.dirname(args.report) else None
            print(f"  Generating PDF report...")
            path = generate_report(result, args.report)
            print(f"  ✅ Report saved to: {path}\n")


if __name__ == "__main__":
    main()
