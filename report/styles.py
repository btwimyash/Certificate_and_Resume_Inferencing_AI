# report/styles.py
# Shared styles, colors, and flowables used by both certificate and resume reports.

from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
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
PURPLE       = colors.HexColor("#7C3AED")
PURPLE_LIGHT = colors.HexColor("#EDE9FE")
GRAY_50      = colors.HexColor("#F9FAFB")
GRAY_100     = colors.HexColor("#F3F4F6")
GRAY_200     = colors.HexColor("#E5E7EB")
GRAY_400     = colors.HexColor("#9CA3AF")
GRAY_600     = colors.HexColor("#4B5563")
GRAY_700     = colors.HexColor("#374151")
GRAY_900     = colors.HexColor("#111827")
WHITE        = colors.white


# ── Style Helper ────────────────────────────────────────────
def _make_style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)


# ── Shared Style Dictionary ─────────────────────────────────
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

    "stat_n_navy": _make_style("stat_n_navy",
        fontName="Helvetica-Bold", fontSize=22,
        textColor=NAVY, leading=26, alignment=TA_CENTER),

    "stat_n_purple": _make_style("stat_n_purple",
        fontName="Helvetica-Bold", fontSize=22,
        textColor=PURPLE, leading=26, alignment=TA_CENTER),

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

    # Resume-specific styles
    "badge_expert": _make_style("badge_expert",
        fontName="Helvetica-Bold", fontSize=7,
        textColor=WHITE, alignment=TA_CENTER, leading=10),

    "badge_advanced": _make_style("badge_advanced",
        fontName="Helvetica-Bold", fontSize=7,
        textColor=GREEN, alignment=TA_CENTER, leading=10),

    "badge_intermediate": _make_style("badge_intermediate",
        fontName="Helvetica-Bold", fontSize=7,
        textColor=AMBER, alignment=TA_CENTER, leading=10),

    "badge_beginner": _make_style("badge_beginner",
        fontName="Helvetica-Bold", fontSize=7,
        textColor=GRAY_600, alignment=TA_CENTER, leading=10),

    "pct_expert": _make_style("pct_expert",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=NAVY, alignment=TA_RIGHT, leading=14),

    "pct_advanced": _make_style("pct_advanced",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=GREEN, alignment=TA_RIGHT, leading=14),

    "pct_intermediate": _make_style("pct_intermediate",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=AMBER, alignment=TA_RIGHT, leading=14),

    "pct_beginner": _make_style("pct_beginner",
        fontName="Helvetica-Bold", fontSize=10,
        textColor=GRAY_600, alignment=TA_RIGHT, leading=14),

    "table_text": _make_style("table_text",
        fontName="Helvetica", fontSize=9,
        textColor=GRAY_700, leading=13),

    "table_bold": _make_style("table_bold",
        fontName="Helvetica-Bold", fontSize=9,
        textColor=GRAY_900, leading=13),
}


# ── Confidence Bar Flowable ─────────────────────────────────
class ConfidenceBar(Flowable):
    def __init__(self, confidence, color, width=100, height=8):
        super().__init__()
        self.confidence = confidence
        self.bar_color  = color
        self.bar_width  = width
        self.bar_height = height
        self.width      = width
        self.height     = height

    def draw(self):
        filled = int(self.confidence * self.bar_width)

        self.canv.setFillColor(GRAY_200)
        self.canv.roundRect(0, 0, self.bar_width, self.bar_height, 3, fill=1, stroke=0)

        if filled > 0:
            self.canv.setFillColor(self.bar_color)
            self.canv.roundRect(0, 0, filled, self.bar_height, 3, fill=1, stroke=0)


# ── Proficiency color mapping ────────────────────────────────
PROFICIENCY_COLORS = {
    "Expert":       (NAVY,   GRAY_100,    NAVY),
    "Advanced":     (GREEN,  GREEN_LIGHT, GREEN),
    "Intermediate": (AMBER,  AMBER_LIGHT, colors.HexColor("#D97706")),
    "Beginner":     (GRAY_600, GRAY_100,  GRAY_400),
}


# ── Footer (shared) ──────────────────────────────────────────
def build_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY_400)
    canvas.drawCentredString(
        A4[0] / 2,
        14 * mm,
        f"Generated by CertLens  ·  Confidential  ·  Page {doc.page}"
    )
    canvas.restoreState()
