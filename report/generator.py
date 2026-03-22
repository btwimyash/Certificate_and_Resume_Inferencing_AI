# report/generator.py

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from reportlab.platypus import Flowable


# ── Colors ─────────────────────────────────────────────────
NAVY         = colors.HexColor("#0D1B2A")
SLATE        = colors.HexColor("#1E3A5F")
ACCENT       = colors.HexColor("#2563EB")
ACCENT_LIGHT = colors.HexColor("#DBEAFE")
GREEN        = colors.HexColor("#16A34A")
GREEN_LIGHT  = colors.HexColor("#DCFCE7")
AMBER        = colors.HexColor("#B45309")
AMBER_LIGHT  = colors.HexColor("#FEF3C7")
GRAY_50      = colors.HexColor("#F9FAFB")
GRAY_100     = colors.HexColor("#F3F4F6")
GRAY_200     = colors.HexColor("#E5E7EB")
GRAY_400     = colors.HexColor("#9CA3AF")
GRAY_600     = colors.HexColor("#4B5563")
GRAY_700     = colors.HexColor("#374151")
GRAY_900     = colors.HexColor("#111827")
WHITE        = colors.white


# ── Confidence Bar Flowable ─────────────────────────────────
class ConfidenceBar(Flowable):
    def __init__(self, confidence, skill_type, width=100, height=8):
        super().__init__()
        self.confidence  = confidence
        self.skill_type  = skill_type
        self.bar_width   = width
        self.bar_height  = height
        self.width       = width
        self.height      = height

    def draw(self):
        bar_color = GREEN if self.skill_type == "explicit" else ACCENT
        filled    = int(self.confidence * self.bar_width)

        # Background track
        self.canv.setFillColor(GRAY_200)
        self.canv.roundRect(0, 0, self.bar_width, self.bar_height, 3, fill=1, stroke=0)

        # Filled portion
        if filled > 0:
            self.canv.setFillColor(bar_color)
            self.canv.roundRect(0, 0, filled, self.bar_height, 3, fill=1, stroke=0)


# ── Style Definitions ───────────────────────────────────────
def _make_style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)


S = {
    "h1": _make_style("h1",
        fontName="Helvetica-Bold", fontSize=20,
        textColor=WHITE, leading=26, alignment=TA_LEFT),

    "h1_sub": _make_style("h1_sub",
        fontName="Helvetica", fontSize=9,
        textColor=colors.HexColor("#93C5FD"), leading=14),

    "section": _make_style("section",
        fontName="Helvetica-Bold", fontSize=11,
        textColor=NAVY, leading=16, spaceBefore=4),

    "label": _make_style("label",
        fontName="Helvetica-Bold", fontSize=7,
        textColor=GRAY_400, leading=10, spaceAfter=3),

    "value": _make_style("value",
        fontName="Helvetica", fontSize=10,
        textColor=GRAY_700, leading=14),

    "stat_n": _make_style("stat_n",
        fontName="Helvetica-Bold", fontSize=26,
        textColor=NAVY, leading=30, alignment=TA_CENTER),

    "stat_n_accent": _make_style("stat_n_accent",
        fontName="Helvetica-Bold", fontSize=26,
        textColor=ACCENT, leading=30, alignment=TA_CENTER),

    "stat_n_green": _make_style("stat_n_green",
        fontName="Helvetica-Bold", fontSize=26,
        textColor=GREEN, leading=30, alignment=TA_CENTER),

    "stat_n_amber": _make_style("stat_n_amber",
        fontName="Helvetica-Bold", fontSize=26,
        textColor=AMBER, leading=30, alignment=TA_CENTER),

    "stat_l": _make_style("stat_l",
        fontName="Helvetica", fontSize=8,
        textColor=GRAY_400, leading=11, alignment=TA_CENTER),

    "rank": _make_style("rank",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=GRAY_400, alignment=TA_CENTER, leading=14),

    "skill_name": _make_style("skill_name",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=GRAY_900, leading=14),

    "skill_reason": _make_style("skill_reason",
        fontName="Helvetica-Oblique", fontSize=8,
        textColor=GRAY_400, leading=11),

    "badge_ex": _make_style("badge_ex",
        fontName="Helvetica-Bold", fontSize=7,
        textColor=GREEN, alignment=TA_CENTER, leading=10),

    "badge_im": _make_style("badge_im",
        fontName="Helvetica-Bold", fontSize=7,
        textColor=AMBER, alignment=TA_CENTER, leading=10),

    "pct_ex": _make_style("pct_ex",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=GREEN, alignment=TA_RIGHT, leading=14),

    "pct_im": _make_style("pct_im",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=ACCENT, alignment=TA_RIGHT, leading=14),

    "breakdown_skill": _make_style("breakdown_skill",
        fontName="Helvetica", fontSize=9,
        textColor=GRAY_700, leading=14),

    "breakdown_pct_ex": _make_style("breakdown_pct_ex",
        fontName="Helvetica-Bold", fontSize=9,
        textColor=GREEN, alignment=TA_RIGHT, leading=14),

    "breakdown_pct_im": _make_style("breakdown_pct_im",
        fontName="Helvetica-Bold", fontSize=9,
        textColor=ACCENT, alignment=TA_RIGHT, leading=14),

    "footer": _make_style("footer",
        fontName="Helvetica", fontSize=8,
        textColor=GRAY_400, alignment=TA_CENTER),
}


# ── Header ──────────────────────────────────────────────────
def _build_header(cert, W):
    title     = cert.get("title", "Certificate Report")
    generated = datetime.now().strftime("%B %d, %Y at %H:%M")

    title_row = Table(
        [[Paragraph(title, S["h1"])]],
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
        [[Paragraph(f"Skill Inference Report &nbsp;·&nbsp; {generated}", S["h1_sub"])]],
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


# ── Certificate Details ─────────────────────────────────────
def _build_details(cert, W):
    cw = (W - 8) / 2

    def cell(label, value):
        return [
            Paragraph(label, S["label"]),
            Paragraph(str(value or "—"), S["value"]),
        ]

    t = Table([
        [
            Table([cell("TITLE",  cert.get("title",  "—"))], colWidths=[cw]),
            Table([cell("ISSUER", cert.get("issuer", "—"))], colWidths=[cw]),
        ],
        [
            Table([cell("DOMAIN", cert.get("domain", "—"))], colWidths=[cw]),
            Table([cell("LEVEL",  cert.get("level",  "—"))], colWidths=[cw]),
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

    return [Paragraph("Certificate Details", S["section"]),
            Spacer(1, 6), t, Spacer(1, 16)]


# ── Stats Cards ─────────────────────────────────────────────
def _build_stats(skills, W):
    explicit = [s for s in skills if s.get("type") == "explicit"]
    implicit = [s for s in skills if s.get("type") == "implicit"]
    cw       = (W - 8) / 3

    def card(number, label, num_style, bg, border):
        inner = Table([
            [Paragraph(str(number), num_style)],
            [Paragraph(label,       S["stat_l"])],
        ], colWidths=[cw - 4])
        inner.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-1), 14),
            ("BOTTOMPADDING", (0,0), (-1,-1), 14),
            ("LEFTPADDING",   (0,0), (-1,-1), 4),
            ("RIGHTPADDING",  (0,0), (-1,-1), 4),
            ("BACKGROUND",    (0,0), (-1,-1), bg),
            ("BOX",           (0,0), (-1,-1), 1, border),
        ]))
        return inner

    row = Table([[
        card(len(skills),   "Total Skills",    S["stat_n_accent"], ACCENT_LIGHT, ACCENT),
        card(len(explicit), "Explicit Skills", S["stat_n_green"],  GREEN_LIGHT,  GREEN),
        card(len(implicit), "Implicit Skills", S["stat_n_amber"],  AMBER_LIGHT,  colors.HexColor("#D97706")),
    ]], colWidths=[cw + 4, cw + 4, cw + 4])

    row.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))

    return [Paragraph("Summary", S["section"]),
            Spacer(1, 6), row, Spacer(1, 16)]


# ── Skills Table ────────────────────────────────────────────
def _build_skills_table(skills, W):
    # Column widths: rank, skill+reason, badge, bar, pct
    cw = [24, 180, 58, 90, 32]

    th_style = _make_style("th",
        fontName="Helvetica-Bold", fontSize=8,
        textColor=WHITE, alignment=TA_CENTER, leading=11)
    th_left  = _make_style("th_l",
        fontName="Helvetica-Bold", fontSize=8,
        textColor=WHITE, leading=11)

    header = [
        Paragraph("#",          th_style),
        Paragraph("Skill",      th_left),
        Paragraph("Type",       th_style),
        Paragraph("Confidence", th_style),
        Paragraph("%",          th_style),
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
    ]

    for i, skill in enumerate(skills, 1):
        name       = skill.get("skill", "")
        stype      = skill.get("type", "implicit")
        conf       = skill.get("confidence", 0)
        reason     = skill.get("reason", "")
        is_ex      = stype == "explicit"
        row_bg     = WHITE if i % 2 == 0 else GRAY_50

        ts.append(("BACKGROUND", (0, i), (-1, i), row_bg))

        # Rank
        rank = Paragraph(str(i), S["rank"])

        # Skill name + reason stacked
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

        # Badge
        badge_text  = "EXPLICIT" if is_ex else "IMPLICIT"
        badge_style = S["badge_ex"] if is_ex else S["badge_im"]
        badge_bg    = GREEN_LIGHT  if is_ex else AMBER_LIGHT
        badge_bdr   = GREEN        if is_ex else colors.HexColor("#D97706")

        badge = Table(
            [[Paragraph(badge_text, badge_style)]],
            colWidths=[cw[2] - 8]
        )
        badge.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), badge_bg),
            ("BOX",           (0,0), (-1,-1), 0.5, badge_bdr),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING",   (0,0), (-1,-1), 4),
            ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ]))

        # Confidence bar
        bar = ConfidenceBar(conf, stype, width=cw[3] - 12, height=7)

        # Percentage
        pct_s = S["pct_ex"] if is_ex else S["pct_im"]
        pct   = Paragraph(f"{conf:.0%}", pct_s)

        rows.append([rank, skill_inner, badge, bar, pct])

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(ts))

    return [Paragraph("Inferred Skills", S["section"]),
            Spacer(1, 6), t, Spacer(1, 16)]


# ── Breakdown ───────────────────────────────────────────────
def _build_breakdown(skills, W):
    explicit = [s for s in skills if s.get("type") == "explicit"]
    implicit = [s for s in skills if s.get("type") == "implicit"]
    cw       = (W - 8) / 2

    def skill_rows(skill_list, pct_style):
        rows = []
        for s in skill_list:
            rows.append([
                Paragraph(f"• {s.get('skill', '')}", S["breakdown_skill"]),
                Paragraph(f"{s.get('confidence', 0):.0%}", pct_style),
            ])
        if not rows:
            rows.append([Paragraph("None", S["value"]), Paragraph("", S["value"])])
        t = Table(rows, colWidths=[cw - 36, 28])
        t.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
            ("RIGHTPADDING",  (0,0), (-1,-1), 0),
            ("LINEBELOW",     (0,0), (-1,-2), 0.3, GRAY_200),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ]))
        return t

    def section(title, skill_list, pct_style, hdr_bg, body_bg, border):
        hdr = Table(
            [[Paragraph(f"  {title}  ({len(skill_list)})", _make_style(
                "bh", fontName="Helvetica-Bold", fontSize=9,
                textColor=WHITE, leading=13)
            )]], colWidths=[cw]
        )
        hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), hdr_bg),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))

        body = Table(
            [[skill_rows(skill_list, pct_style)]],
            colWidths=[cw]
        )
        body.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), body_bg),
            ("BOX",           (0,0), (-1,-1), 0.5, border),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ]))
        return hdr, body

    ex_hdr, ex_body = section(
        "Explicit Skills", explicit, S["breakdown_pct_ex"],
        GREEN, GREEN_LIGHT, GREEN
    )
    im_hdr, im_body = section(
        "Implicit Skills", implicit, S["breakdown_pct_im"],
        colors.HexColor("#D97706"), AMBER_LIGHT, colors.HexColor("#D97706")
    )

    grid = Table([
        [ex_hdr,  im_hdr],
        [ex_body, im_body],
    ], colWidths=[cw + 4, cw + 4])

    grid.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))

    return [Paragraph("Explicit vs Implicit Breakdown", S["section"]),
            Spacer(1, 6), grid, Spacer(1, 16)]


# ── Footer ──────────────────────────────────────────────────
def _build_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY_400)
    canvas.drawCentredString(
        A4[0] / 2,
        14 * mm,
        f"Generated by CertLens  ·  Confidential  ·  Page {doc.page}"
    )
    canvas.restoreState()


# ── Main Entry Point ────────────────────────────────────────
def generate_report(result: dict, output_path: str) -> str:
    cert   = result.get("certificate", {})
    skills = result.get("skills", [])

    W, H   = A4
    margin = 18 * mm
    usable = W - 2 * margin

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin,  bottomMargin=22 * mm,
        title=f"Skill Report — {cert.get('title', 'Certificate')}",
        author="CertLens",
    )

    story = []
    story += _build_header(cert, usable)
    story += _build_details(cert, usable)
    story += _build_stats(skills, usable)
    story += _build_skills_table(skills, usable)
    story += _build_breakdown(skills, usable)

    doc.build(story, onFirstPage=_build_footer, onLaterPages=_build_footer)
    return os.path.abspath(output_path)