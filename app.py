# app.py — SkillInferencing AI Web UI

import os
import io
import json
import tempfile
import streamlit as st

from inference.extractor import load_certificate, load_resume
from inference.model import infer_skills, infer_resume_skills
from report.generator import generate_report
from report.resume_generator import generate_resume_report


# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="SkillInferencing AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("🎓 SkillInferencing AI")
    st.caption("AI Powered Skill Analysis")
    st.divider()

    mode = st.radio(
        "Analysis Mode",
        options=["Certificate Analysis", "Resume Analysis"],
        index=0,
    )

    uploaded_file = st.file_uploader(
        "Upload File",
        type=["pdf", "jpg", "jpeg", "png", "webp"],
        help="Supports PDF, JPG, PNG, WEBP",
    )

    analyze_btn = st.button(
        "Analyze",
        type="primary",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

    st.divider()


# ── Helper: save upload to temp file (Windows-safe) ──────────
def _save_temp(uploaded) -> str:
    suffix = os.path.splitext(uploaded.name)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.read())
    tmp.close()
    return tmp.name


# ── Helper: generate PDF to bytes ────────────────────────────
def _report_bytes(result: dict, mode_is_resume: bool) -> bytes:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    if mode_is_resume:
        generate_resume_report(result, tmp.name)
    else:
        generate_report(result, tmp.name)
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data


# ── Session state keys ────────────────────────────────────────
RESULT_KEY  = "analysis_result"
MODE_KEY    = "analysis_mode"
REPORT_KEY  = "report_bytes"


# ── Run analysis ─────────────────────────────────────────────
if analyze_btn and uploaded_file:
    tmp_path = _save_temp(uploaded_file)
    try:
        is_resume = mode == "Resume Analysis"
        with st.spinner("Analyzing with AI..."):
            if is_resume:
                pages  = load_resume(tmp_path)
                result = infer_resume_skills(pages)
            else:
                cert_data = load_certificate(tmp_path)
                result    = infer_skills(cert_data)

        st.session_state[RESULT_KEY] = result
        st.session_state[MODE_KEY]   = mode
        st.session_state[REPORT_KEY] = _report_bytes(result, is_resume)
    except Exception as e:
        st.error(f"Analysis failed: {e}")
    finally:
        os.unlink(tmp_path)


# ── Display results ───────────────────────────────────────────
if RESULT_KEY in st.session_state:
    result    = st.session_state[RESULT_KEY]
    cur_mode  = st.session_state[MODE_KEY]
    skills    = result.get("skills", [])

    # ── Certificate Results ───────────────────────────────────
    if cur_mode == "Certificate Analysis":
        cert = result.get("certificate", {})

        st.header(cert.get("title", "Certificate Analysis"))

        explicit = [s for s in skills if s.get("type") == "explicit"]
        implicit = [s for s in skills if s.get("type") == "implicit"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Skills",    len(skills))
        col2.metric("Explicit Skills", len(explicit))
        col3.metric("Implicit Skills", len(implicit))

        with st.expander("Certificate Details", expanded=True):
            d1, d2 = st.columns(2)
            d1.markdown(f"**Title:** {cert.get('title', '—')}")
            d1.markdown(f"**Domain:** {cert.get('domain', '—')}")
            d2.markdown(f"**Issuer:** {cert.get('issuer', '—')}")
            d2.markdown(f"**Level:** {cert.get('level', '—')}")

        st.subheader("Inferred Skills")
        if skills:
            import pandas as pd
            df = pd.DataFrame([{
                "#":          i + 1,
                "Skill":      s.get("skill", ""),
                "Type":       s.get("type", "").capitalize(),
                "Confidence": f"{s.get('confidence', 0):.0%}",
                "Reason":     s.get("reason", ""),
            } for i, s in enumerate(skills)])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Resume Results ────────────────────────────────────────
    else:
        resume = result.get("resume", {})
        exp_years = resume.get("total_experience_years", 0)

        st.header(resume.get("candidate_name", "Resume Analysis"))
        st.caption(resume.get("summary", ""))

        st.metric("Total Experience", f"{exp_years} year{'s' if exp_years != 1 else ''}")

        levels = ["Expert", "Advanced", "Intermediate", "Beginner"]
        counts = {lvl: sum(1 for s in skills if s.get("proficiency") == lvl) for lvl in levels}
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Skills",   len(skills))
        c2.metric("Expert",         counts["Expert"])
        c3.metric("Advanced",       counts["Advanced"])
        c4.metric("Intermediate",   counts["Intermediate"])
        c5.metric("Beginner",       counts["Beginner"])

        experience = resume.get("experience", [])
        if experience:
            with st.expander("Work Experience", expanded=True):
                import pandas as pd
                exp_df = pd.DataFrame([{
                    "Title":    e.get("title", ""),
                    "Company":  e.get("company", ""),
                    "Duration": e.get("duration", ""),
                } for e in experience])
                st.dataframe(exp_df, use_container_width=True, hide_index=True)

        education = resume.get("education", [])
        if education:
            with st.expander("Education", expanded=True):
                import pandas as pd
                edu_df = pd.DataFrame([{
                    "Degree":      e.get("degree", ""),
                    "Institution": e.get("institution", ""),
                    "Year":        e.get("year", ""),
                } for e in education])
                st.dataframe(edu_df, use_container_width=True, hide_index=True)

        st.subheader("Inferred Skills")
        if skills:
            import pandas as pd
            df = pd.DataFrame([{
                "#":           i + 1,
                "Skill":       s.get("skill", ""),
                "Proficiency": s.get("proficiency", ""),
                "Confidence":  f"{s.get('confidence', 0):.0%}",
                "Source":      s.get("source", ""),
                "Reason":      s.get("reason", ""),
            } for i, s in enumerate(skills)])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Download Section ──────────────────────────────────────
    st.divider()
    col_dl, col_json = st.columns([1, 1])

    with col_dl:
        fname = "certificate_report.pdf" if cur_mode == "Certificate Analysis" else "resume_report.pdf"
        st.download_button(
            label="Download PDF Report",
            data=st.session_state[REPORT_KEY],
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )

    with col_json:
        st.download_button(
            label="Download JSON Results",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name="results.json",
            mime="application/json",
            use_container_width=True,
        )

# ── Welcome screen ────────────────────────────────────────────
else:
    st.title("Welcome to SkillInferencing AI")
    st.markdown(
        "Upload a **certificate** or **resume** in the sidebar to get started. "
        "SkillInferencing AI extracts and infers professional skills from your documents."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.info(
            "**Certificate Analysis**\n\n"
            "- Detects certificate title, issuer, domain, and level\n"
            "- Extracts explicit and implicit skills\n"
            "- Assigns confidence scores (50%–100%)\n"
            "- Generates a professional PDF report"
        )
    with col2:
        st.info(
            "**Resume Analysis**\n\n"
            "- Extracts candidate profile, experience, and education\n"
            "- Infers skills with proficiency levels (Beginner → Expert)\n"
            "- Supports multi-page PDFs\n"
            "- Generates a detailed PDF report"
        )
