# report/resume_generator.py

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from report.styles import (
    NAVY, SLATE, ACCENT, ACCENT_LIGHT, GREEN, GREEN_LIGHT,
    AMBER, AMBER_LIGHT, PURPLE, PURPLE_LIGHT,
    GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_600, GRAY_700, GRAY_900, WHITE,
    S, _make_style, ConfidenceBar, PROFICIENCY_COLORS, build_footer
)


# ── Header ──────────────────────────────────────────────────
def _build_header(resume, W):
    name      = resume.get("candidate_name", "Candidate Report")
    generated = datetime.now().strftime("%B %d, %Y at %H:%M")

    title_row = Table(
        [[Paragraph(name, S["h1"])]],
        colWidths=[W]
    )
    title_row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("TOPPADDING",    (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))

    sub_row = Table(
        [[Paragraph(f"Resume Skill Analysis Report &nbsp;·&nbsp; {generated}", S["h1_sub"])]],
        colWidths=[W]
    )
    sub_row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
    ]))

    return [title_row, sub_row, Spacer(1, 14)]


# ── Candidate Details ────────────────────────────────────────
def _build_details(resume, W):
    cw = (W - 8) / 2

    def cell(label, value):
        return [
            Paragraph(label, S["label"]),
            Paragraph(str(value or "—"), S["value"]),
        ]

    exp_years = resume.get("total_experience_years", 0)
    exp_label = f"{exp_years} year{'s' if exp_years != 1 else ''}"

    t = Table([
        [
            Table([cell("CANDIDATE", resume.get("candidate_name", "—"))], colWidths=[cw]),
            Table([cell("EXPERIENCE", exp_label)],                         colWidths=[cw]),
        ],
        [
            Table([cell("SUMMARY", resume.get("summary", "—"))], colWidths=[cw]),
            Spacer(cw, 1),
        ],
    ], colWidths=[cw + 4, cw + 4])

    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), GRAY_50),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY_200),
        ("LINEBELOW",     (0,0), (-1,0),  0.5, GRAY_200),
        ("LINEBETWEEN",   (0,0), (0,-1),  0.5, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))

    return [Paragraph("Candidate Details", S["section"]),
            Spacer(1, 6), t, Spacer(1, 16)]


# ── Experience Table ─────────────────────────────────────────
def _build_experience(experience, W):
    if not experience:
        return []

    th_style = _make_style("exp_th",
        fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, leading=11)

    header = [
        Paragraph("Job Title",  th_style),
        Paragraph("Company",    th_style),
        Paragraph("Duration",   th_style),
    ]
    cw = [W * 0.38, W * 0.38, W * 0.24]

    rows = [header]
    ts   = [
        ("BACKGROUND",    (0,0), (-1,0),  NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY_200),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, GRAY_200),
    ]

    for i, exp in enumerate(experience, 1):
        row_bg = WHITE if i % 2 == 0 else GRAY_50
        ts.append(("BACKGROUND", (0, i), (-1, i), row_bg))
        rows.append([
            Paragraph(exp.get("title",    "—"), S["table_bold"]),
            Paragraph(exp.get("company",  "—"), S["table_text"]),
            Paragraph(exp.get("duration", "—"), S["table_text"]),
        ])

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(ts))

    return [Paragraph("Work Experience", S["section"]),
            Spacer(1, 6), t, Spacer(1, 16)]


# ── Education Table ──────────────────────────────────────────
def _build_education(education, W):
    if not education:
        return []

    th_style = _make_style("edu_th",
        fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, leading=11)

    header = [
        Paragraph("Degree",      th_style),
        Paragraph("Institution", th_style),
        Paragraph("Year",        th_style),
    ]
    cw = [W * 0.35, W * 0.45, W * 0.20]

    rows = [header]
    ts   = [
        ("BACKGROUND",    (0,0), (-1,0),  NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY_200),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, GRAY_200),
    ]

    for i, edu in enumerate(education, 1):
        row_bg = WHITE if i % 2 == 0 else GRAY_50
        ts.append(("BACKGROUND", (0, i), (-1, i), row_bg))
        rows.append([
            Paragraph(edu.get("degree",      "—"), S["table_bold"]),
            Paragraph(edu.get("institution", "—"), S["table_text"]),
            Paragraph(edu.get("year",        "—"), S["table_text"]),
        ])

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(ts))

    return [Paragraph("Education", S["section"]),
            Spacer(1, 6), t, Spacer(1, 16)]


# ── Stats Cards ──────────────────────────────────────────────
def _build_stats(skills, W):
    levels   = ["Expert", "Advanced", "Intermediate", "Beginner"]
    counts   = {lvl: sum(1 for s in skills if s.get("proficiency") == lvl) for lvl in levels}
    cw       = (W - 12) / 4

    num_styles = {
        "Expert":       S["stat_n_navy"],
        "Advanced":     S["stat_n_green"],
        "Intermediate": S["stat_n_amber"],
        "Beginner":     S["stat_n"],
    }
    bg_colors = {
        "Expert":       GRAY_100,
        "Advanced":     GREEN_LIGHT,
        "Intermediate": AMBER_LIGHT,
        "Beginner":     GRAY_50,
    }
    borders = {
        "Expert":       NAVY,
        "Advanced":     GREEN,
        "Intermediate": colors.HexColor("#D97706"),
        "Beginner":     GRAY_400,
    }

    def card(level):
        inner = Table([
            [Paragraph(str(counts[level]), num_styles[level])],
            [Paragraph(level,              S["stat_l"])],
        ], colWidths=[cw - 4])
        inner.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-1), 12),
            ("BOTTOMPADDING", (0,0), (-1,-1), 12),
            ("LEFTPADDING",   (0,0), (-1,-1), 4),
            ("RIGHTPADDING",  (0,0), (-1,-1), 4),
            ("BACKGROUND",    (0,0), (-1,-1), bg_colors[level]),
            ("BOX",           (0,0), (-1,-1), 1, borders[level]),
        ]))
        return inner

    total_card = Table([
        [Paragraph(str(len(skills)), S["stat_n_accent"])],
        [Paragraph("Total Skills",  S["stat_l"])],
    ], colWidths=[cw - 4])
    total_card.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("BACKGROUND",    (0,0), (-1,-1), ACCENT_LIGHT),
        ("BOX",           (0,0), (-1,-1), 1, ACCENT),
    ]))

    row = Table([[
        total_card,
        card("Expert"),
        card("Advanced"),
        card("Intermediate"),
        card("Beginner"),
    ]], colWidths=[cw + 4, cw + 2, cw + 2, cw + 2, cw + 2])

    row.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 3),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))

    return [Paragraph("Summary", S["section"]),
            Spacer(1, 6), row, Spacer(1, 16)]


# ── Skills Table ─────────────────────────────────────────────
def _build_skills_table(skills, W):
    cw = [24, 160, 68, 60, 90, 32]

    th_style = _make_style("rth",
        fontName="Helvetica-Bold", fontSize=8,
        textColor=WHITE, alignment=TA_CENTER, leading=11)
    th_left  = _make_style("rth_l",
        fontName="Helvetica-Bold", fontSize=8,
        textColor=WHITE, leading=11)

    header = [
        Paragraph("#",           th_style),
        Paragraph("Skill",       th_left),
        Paragraph("Proficiency", th_style),
        Paragraph("Source",      th_left),
        Paragraph("Confidence",  th_style),
        Paragraph("%",           th_style),
    ]

    rows = [header]
    ts   = [
        ("BACKGROUND",    (0,0), (-1,0),  NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY_200),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, GRAY_200),
        ("LINEBEFORE",    (1,0), (1,-1),  0.3, GRAY_200),
        ("LINEBEFORE",    (2,0), (2,-1),  0.3, GRAY_200),
        ("LINEBEFORE",    (3,0), (3,-1),  0.3, GRAY_200),
        ("LINEBEFORE",    (4,0), (4,-1),  0.3, GRAY_200),
        ("LINEBEFORE",    (5,0), (5,-1),  0.3, GRAY_200),
    ]

    badge_styles = {
        "Expert":       ("badge_expert",       NAVY,   GRAY_100, NAVY),
        "Advanced":     ("badge_advanced",     GREEN,  GREEN_LIGHT, GREEN),
        "Intermediate": ("badge_intermediate", AMBER,  AMBER_LIGHT, colors.HexColor("#D97706")),
        "Beginner":     ("badge_beginner",     GRAY_600, GRAY_100, GRAY_400),
    }
    pct_styles = {
        "Expert":       S["pct_expert"],
        "Advanced":     S["pct_advanced"],
        "Intermediate": S["pct_intermediate"],
        "Beginner":     S["pct_beginner"],
    }
    bar_colors = {
        "Expert":       NAVY,
        "Advanced":     GREEN,
        "Intermediate": AMBER,
        "Beginner":     GRAY_400,
    }

    for i, skill in enumerate(skills, 1):
        name        = skill.get("skill", "")
        proficiency = skill.get("proficiency", "Intermediate")
        conf        = skill.get("confidence", 0)
        reason      = skill.get("reason", "")
        source      = skill.get("source", "")
        row_bg      = WHITE if i % 2 == 0 else GRAY_50

        ts.append(("BACKGROUND", (0, i), (-1, i), row_bg))

        rank = Paragraph(str(i), S["rank"])

        skill_inner = Table([
            [Paragraph(name,   S["skill_name"])],
            [Paragraph(reason, S["skill_reason"])],
        ], colWidths=[cw[1] - 4])
        skill_inner.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-1), 1),
            ("BOTTOMPADDING", (0,0), (-1,-1), 1),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
            ("RIGHTPADDING",  (0,0), (-1,-1), 0),
        ]))

        bstyle_key, b_text_color, b_bg, b_bdr = badge_styles.get(
            proficiency, badge_styles["Intermediate"]
        )
        badge = Table(
            [[Paragraph(proficiency.upper(), S[bstyle_key])]],
            colWidths=[cw[2] - 8]
        )
        badge.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), b_bg),
            ("BOX",           (0,0), (-1,-1), 0.5, b_bdr),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING",   (0,0), (-1,-1), 4),
            ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ]))

        source_p = Paragraph(source, S["skill_reason"])

        bar_color = bar_colors.get(proficiency, GRAY_400)
        bar = ConfidenceBar(conf, bar_color, width=cw[4] - 12, height=7)

        pct = Paragraph(f"{conf:.0%}", pct_styles.get(proficiency, S["pct_beginner"]))

        rows.append([rank, skill_inner, badge, source_p, bar, pct])

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(ts))

    return [Paragraph("Inferred Skills", S["section"]),
            Spacer(1, 6), t, Spacer(1, 16)]


# ── Proficiency Breakdown ─────────────────────────────────────
def _build_breakdown(skills, W):
    levels = ["Expert", "Advanced", "Intermediate", "Beginner"]
    grouped = {lvl: [s for s in skills if s.get("proficiency") == lvl] for lvl in levels}

    hdr_bgs  = {"Expert": NAVY,  "Advanced": GREEN,  "Intermediate": colors.HexColor("#D97706"), "Beginner": GRAY_600}
    body_bgs = {"Expert": GRAY_100, "Advanced": GREEN_LIGHT, "Intermediate": AMBER_LIGHT, "Beginner": GRAY_50}
    borders  = {"Expert": NAVY,  "Advanced": GREEN,  "Intermediate": colors.HexColor("#D97706"), "Beginner": GRAY_400}
    pct_stys = {
        "Expert":       S["pct_expert"],
        "Advanced":     S["pct_advanced"],
        "Intermediate": S["pct_intermediate"],
        "Beginner":     S["pct_beginner"],
    }

    cw = (W - 12) / 4

    def skill_list(skill_items, pct_style):
        rows = []
        for s in skill_items:
            rows.append([
                Paragraph(f"• {s.get('skill', '')}", S["breakdown_skill"]),
                Paragraph(f"{s.get('confidence', 0):.0%}", pct_style),
            ])
        if not rows:
            rows.append([Paragraph("None", S["value"]), Paragraph("", S["value"])])
        t = Table(rows, colWidths=[cw - 30, 24])
        t.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
            ("RIGHTPADDING",  (0,0), (-1,-1), 0),
            ("LINEBELOW",     (0,0), (-1,-2), 0.3, GRAY_200),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ]))
        return t

    def section(lvl):
        hdr_text = f"  {lvl}  ({len(grouped[lvl])})"
        txt_color = WHITE if lvl in ("Expert", "Advanced", "Intermediate", "Beginner") else WHITE
        hdr = Table(
            [[Paragraph(hdr_text, _make_style(
                f"bh_{lvl}", fontName="Helvetica-Bold", fontSize=9,
                textColor=WHITE, leading=13)
            )]], colWidths=[cw]
        )
        hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), hdr_bgs[lvl]),
            ("TOPPADDING",    (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))
        body = Table(
            [[skill_list(grouped[lvl], pct_stys[lvl])]],
            colWidths=[cw]
        )
        body.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), body_bgs[lvl]),
            ("BOX",           (0,0), (-1,-1), 0.5, borders[lvl]),
            ("TOPPADDING",    (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ]))
        return hdr, body

    sections = [section(lvl) for lvl in levels]
    grid = Table([
        [s[0] for s in sections],
        [s[1] for s in sections],
    ], colWidths=[cw + 3] * 4)

    grid.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 3),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))

    return [Paragraph("Proficiency Breakdown", S["section"]),
            Spacer(1, 6), grid, Spacer(1, 16)]


# ── Main Entry Point ─────────────────────────────────────────
def generate_resume_report(result: dict, output_path: str) -> str:
    resume = result.get("resume", {})
    skills = result.get("skills", [])

    W, H   = A4
    margin = 18 * mm
    usable = W - 2 * margin

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin,  bottomMargin=22 * mm,
        title=f"Resume Report — {resume.get('candidate_name', 'Candidate')}",
        author="CertLens",
    )

    story = []
    story += _build_header(resume, usable)
    story += _build_details(resume, usable)
    story += _build_experience(resume.get("experience", []), usable)
    story += _build_education(resume.get("education", []),  usable)
    story += _build_stats(skills, usable)
    story += _build_skills_table(skills, usable)
    story += _build_breakdown(skills, usable)

    doc.build(story, onFirstPage=build_footer, onLaterPages=build_footer)
    return os.path.abspath(output_path)
