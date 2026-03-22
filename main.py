# main.py

import argparse
import json
import os
from inference.extractor import load_certificate
from inference.model import infer_skills
from report.generator import generate_report


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
        description="CertLens — Infer skills from certificates using Gemini AI"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to certificate file (JPG, PNG, WEBP, PDF)"
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

    print(f"\n  Loading certificate: {args.file}")
    certificate_data = load_certificate(args.file)
    print("  Certificate loaded. Sending to Gemini...")

    result = infer_skills(certificate_data)
    print_results(result)

    if args.output:
        save_results(result, args.output)

    if args.report:
        # Auto-create reports folder if it doesn't exist
        os.makedirs(os.path.dirname(args.report), exist_ok=True) \
            if os.path.dirname(args.report) else None
        print(f"  Generating PDF report...")
        path = generate_report(result, args.report)
        print(f"  ✅ Report saved to: {path}\n")


if __name__ == "__main__":
    main()


