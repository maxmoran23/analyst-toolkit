#!/usr/bin/env python3
"""
PDF Narrative Dashboard Report Generator
=========================================
Generates dark-background, amber-accented multi-page PDF reports:
a designed narrative document with hero stats, vector charts,
structured tables, comparison grids, and long-form analysis.

Engine: ReportLab (pure Python, no headless browser needed)

Usage:
    python3 generate_report.py                           # Demo report
    python3 generate_report.py --output my_report.pdf    # Custom output path

For programmatic use, import NarrativeDashboardReport and call its methods
to build pages, then generate().

Dependencies:
    pip3 install reportlab
"""

import argparse
import math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle


# =============================================================================
# DESIGN TOKENS
# =============================================================================

class Theme:
    """Design system constants for the narrative dashboard report."""

    # Backgrounds
    BG_PRIMARY      = HexColor('#111827')
    BG_CARD         = HexColor('#1a1f35')
    BG_CALLOUT      = HexColor('#1e2440')
    BG_TABLE_ALT    = HexColor('#151b2e')

    # Accent
    AMBER           = HexColor('#d4a574')
    AMBER_LIGHT     = HexColor('#e8c9a0')
    AMBER_DIM       = Color(0.831, 0.647, 0.455, alpha=0.15)
    AMBER_GLOW      = Color(0.831, 0.647, 0.455, alpha=0.08)

    # Text
    TEXT_PRIMARY     = HexColor('#ffffff')
    TEXT_BODY        = HexColor('#c8ccd4')
    TEXT_SECONDARY   = HexColor('#8b92a0')
    TEXT_MUTED       = HexColor('#5a6070')

    # Borders
    BORDER_SUBTLE    = HexColor('#2a3045')

    # Semantic
    SEVERITY_HIGH    = HexColor('#e05555')
    SEVERITY_POS     = HexColor('#4ade80')

    # Typography
    FONT             = 'Helvetica'
    FONT_BOLD        = 'Helvetica-Bold'

    # Page
    PAGE_W, PAGE_H   = letter  # 612 x 792 points
    MARGIN_TOP        = 0.75 * inch
    MARGIN_BOTTOM     = 0.75 * inch
    MARGIN_LEFT       = 0.83 * inch
    MARGIN_RIGHT      = 0.83 * inch
    CONTENT_W         = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class NarrativeDashboardReport:
    """Builds a multi-page PDF narrative dashboard report."""

    def __init__(self, filename='report.pdf', title='Report', subject='', date='', descriptor=''):
        self.filename = filename
        self.title = title
        self.subject = subject
        self.date = date
        self.descriptor = descriptor
        self.c = canvas.Canvas(filename, pagesize=letter)
        self.page_num = 0
        self.T = Theme

    # -------------------------------------------------------------------------
    # LOW-LEVEL HELPERS
    # -------------------------------------------------------------------------

    def _fill_background(self):
        """Fill the entire page with the dark background color."""
        self.c.setFillColor(self.T.BG_PRIMARY)
        self.c.rect(0, 0, self.T.PAGE_W, self.T.PAGE_H, fill=1, stroke=0)

    def _new_page(self, with_header=True):
        """Start a new page with dark background and optional running header."""
        if self.page_num > 0:
            self.c.showPage()
        self.page_num += 1
        self._fill_background()
        if with_header and self.page_num > 1:
            self._draw_page_header()

    def _draw_page_header(self):
        """Running header: 'Title — Subject — Date | Page N'"""
        self.c.setFont(self.T.FONT, 8)
        self.c.setFillColor(self.T.TEXT_MUTED)
        header = f"{self.title} — {self.subject} — {self.date} | Page {self.page_num}"
        self.c.drawString(self.T.MARGIN_LEFT, self.T.PAGE_H - 40, header)

    def _x(self, offset=0):
        """Left margin + offset."""
        return self.T.MARGIN_LEFT + offset

    def _content_top(self):
        """Y position for content start (below header)."""
        return self.T.PAGE_H - self.T.MARGIN_TOP - (24 if self.page_num > 1 else 0)

    def _draw_text(self, x, y, text, font='Helvetica', size=10, color=None, align='left'):
        """Draw a single line of text."""
        if color is None:
            color = self.T.TEXT_BODY
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        if align == 'center':
            self.c.drawCentredString(x, y, text)
        elif align == 'right':
            self.c.drawRightString(x, y, text)
        else:
            self.c.drawString(x, y, text)

    def _draw_section_title(self, y, title, subtitle=None):
        """Draw ALL CAPS section title + optional subtitle. Returns new y."""
        self.c.setFont(self.T.FONT_BOLD, 18)
        self.c.setFillColor(self.T.TEXT_PRIMARY)
        # Manual letter spacing by drawing chars individually
        self._draw_spaced_text(self._x(), y, title.upper(), self.T.FONT_BOLD, 18,
                               self.T.TEXT_PRIMARY, spacing=2.5)
        y -= 18
        if subtitle:
            y -= 6
            self.c.setFont(self.T.FONT, 13)
            self.c.setFillColor(self.T.TEXT_BODY)
            self.c.drawString(self._x(), y, subtitle)
            y -= 20
        else:
            y -= 14
        return y

    def _draw_spaced_text(self, x, y, text, font, size, color, spacing=2):
        """Draw text with additional letter spacing."""
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        for char in text:
            self.c.drawString(x, y, char)
            x += self.c.stringWidth(char, font, size) + spacing

    def _draw_wrapped_text(self, x, y, text, width, font='Helvetica', size=10,
                           color=None, leading=15):
        """Draw text that wraps within a given width. Returns new y position."""
        if color is None:
            color = self.T.TEXT_BODY
        style = ParagraphStyle(
            'body',
            fontName=font,
            fontSize=size,
            leading=leading,
            textColor=color,
        )
        p = Paragraph(text, style)
        w, h = p.wrap(width, 500)
        p.drawOn(self.c, x, y - h)
        return y - h - 4

    def _draw_accent_line(self, y, width=None, full=False):
        """Draw an amber accent line or full-width subtle divider."""
        self.c.setStrokeColor(self.T.AMBER if not full else self.T.BORDER_SUBTLE)
        self.c.setLineWidth(1 if full else 2)
        w = (self.T.CONTENT_W if full else (width or 48))
        self.c.line(self._x(), y, self._x() + w, y)
        return y - 12

    def _draw_card(self, x, y, w, h, title, value, desc):
        """Draw a comparison card with background, title, value, description."""
        # Card background
        self.c.setFillColor(self.T.BG_CARD)
        self.c.setStrokeColor(self.T.BORDER_SUBTLE)
        self.c.setLineWidth(0.5)
        self.c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)

        # Card title
        self._draw_text(x + 12, y - 18, title.upper(), self.T.FONT, 8,
                        self.T.TEXT_SECONDARY)
        # Card value
        self._draw_text(x + 12, y - 38, str(value), self.T.FONT_BOLD, 20,
                        self.T.AMBER)
        # Card description
        self._draw_wrapped_text(x + 12, y - 48, desc, w - 24,
                                self.T.FONT, 8.5, self.T.TEXT_BODY, leading=12)

    def _draw_table(self, y, headers, rows, col_widths=None):
        """Draw a styled data table. Returns new y position."""
        num_cols = len(headers)
        if col_widths is None:
            col_widths = [self.T.CONTENT_W / num_cols] * num_cols

        x_start = self._x()
        row_height = 24

        # Header row
        self.c.setFillColor(self.T.BG_CARD)
        self.c.rect(x_start, y - row_height, self.T.CONTENT_W, row_height, fill=1, stroke=0)
        self.c.setStrokeColor(self.T.BORDER_SUBTLE)
        self.c.setLineWidth(0.5)
        self.c.line(x_start, y - row_height, x_start + self.T.CONTENT_W, y - row_height)

        cx = x_start
        for i, hdr in enumerate(headers):
            self._draw_text(cx + 8, y - 16, hdr.upper(), self.T.FONT_BOLD, 8.5,
                            self.T.TEXT_SECONDARY)
            cx += col_widths[i]

        y -= row_height

        # Data rows
        for row_idx, row in enumerate(rows):
            rh = row_height
            # Alternating background
            if row_idx % 2 == 1:
                self.c.setFillColor(self.T.BG_TABLE_ALT)
                self.c.rect(x_start, y - rh, self.T.CONTENT_W, rh, fill=1, stroke=0)

            cx = x_start
            for col_idx, cell in enumerate(row):
                color = self.T.TEXT_PRIMARY if col_idx == 0 else self.T.TEXT_BODY
                font = self.T.FONT_BOLD if col_idx == 0 else self.T.FONT
                self._draw_text(cx + 8, y - 16, str(cell), font, 9, color)
                cx += col_widths[col_idx]

            # Row border
            self.c.setStrokeColor(self.T.BORDER_SUBTLE)
            self.c.line(x_start, y - rh, x_start + self.T.CONTENT_W, y - rh)
            y -= rh

        return y - 8

    # -------------------------------------------------------------------------
    # CHART HELPERS
    # -------------------------------------------------------------------------

    def _draw_bell_curve(self, y, marker_pos=0.85, marker_label='142',
                         axis_labels=None):
        """Draw a bell curve distribution chart with position marker.
        marker_pos: 0.0 (left) to 1.0 (right) — where the subject sits.
        """
        cx_start = self._x()
        chart_w = self.T.CONTENT_W
        chart_h = 120
        cy_base = y - chart_h

        # Bell curve points (standard normal approximation)
        points = []
        for i in range(100):
            t = i / 99.0
            x = cx_start + t * chart_w
            # Gaussian: exp(-((t-0.5)/0.15)^2)
            g = math.exp(-((t - 0.5) / 0.16) ** 2)
            py = cy_base + g * (chart_h - 20)
            points.append((x, py))

        # Baseline
        self.c.setStrokeColor(self.T.BORDER_SUBTLE)
        self.c.setLineWidth(0.5)
        self.c.line(cx_start, cy_base, cx_start + chart_w, cy_base)

        # Filled area under curve (very subtle)
        path = self.c.beginPath()
        path.moveTo(cx_start, cy_base)
        for px, py in points:
            path.lineTo(px, py)
        path.lineTo(cx_start + chart_w, cy_base)
        path.close()
        self.c.setFillColor(Color(0.78, 0.80, 0.83, alpha=0.06))
        self.c.drawPath(path, fill=1, stroke=0)

        # Curve line
        self.c.setStrokeColor(Color(0.78, 0.80, 0.83, alpha=0.4))
        self.c.setLineWidth(1.5)
        path2 = self.c.beginPath()
        path2.moveTo(points[0][0], points[0][1])
        for px, py in points[1:]:
            path2.lineTo(px, py)
        self.c.drawPath(path2, fill=0, stroke=1)

        # Highlighted right tail (amber)
        marker_idx = int(marker_pos * 99)
        path3 = self.c.beginPath()
        path3.moveTo(points[marker_idx][0], cy_base)
        for px, py in points[marker_idx:]:
            path3.lineTo(px, py)
        path3.lineTo(cx_start + chart_w, cy_base)
        path3.close()
        self.c.setFillColor(Color(0.831, 0.647, 0.455, alpha=0.3))
        self.c.drawPath(path3, fill=1, stroke=0)

        # Marker line
        mx = points[marker_idx][0]
        my = points[marker_idx][1]
        self.c.setStrokeColor(self.T.AMBER)
        self.c.setLineWidth(2)
        self.c.line(mx, cy_base - 5, mx, my)

        # Marker label
        self._draw_text(mx, cy_base - 18, marker_label, self.T.FONT_BOLD, 11,
                        self.T.AMBER, align='center')

        # Axis labels
        if axis_labels:
            positions = [0.0, 0.25, 0.5, 0.75, 1.0]
            for i, lbl in enumerate(axis_labels[:5]):
                lx = cx_start + positions[i] * chart_w
                self._draw_text(lx, cy_base - 30, lbl, self.T.FONT, 7,
                                self.T.TEXT_MUTED, align='center')

        return cy_base - 40

    def _draw_radar_chart(self, cx, cy, radius, values, labels, max_val=None):
        """Draw a radar/spider chart centered at (cx, cy).
        values: list of numeric values
        labels: list of axis label strings
        max_val: normalization ceiling (defaults to max of values * 1.1)
        """
        n = len(values)
        if max_val is None:
            max_val = max(values) * 1.1

        angles = [2 * math.pi * i / n - math.pi / 2 for i in range(n)]

        def polar_to_xy(angle, r):
            return cx + r * math.cos(angle), cy + r * math.sin(angle)

        # Grid rings (3 levels)
        for level in [0.33, 0.66, 1.0]:
            r = radius * level
            self.c.setStrokeColor(self.T.BORDER_SUBTLE)
            self.c.setLineWidth(0.5)
            path = self.c.beginPath()
            for i, angle in enumerate(angles):
                x, y = polar_to_xy(angle, r)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.close()
            self.c.drawPath(path, fill=0, stroke=1)

        # Axis lines
        for angle in angles:
            x, y = polar_to_xy(angle, radius)
            self.c.setStrokeColor(self.T.BORDER_SUBTLE)
            self.c.setLineWidth(0.5)
            self.c.line(cx, cy, x, y)

        # Data polygon (filled)
        data_points = []
        for i, val in enumerate(values):
            r = radius * (val / max_val)
            x, y = polar_to_xy(angles[i], r)
            data_points.append((x, y))

        path = self.c.beginPath()
        path.moveTo(data_points[0][0], data_points[0][1])
        for x, y in data_points[1:]:
            path.lineTo(x, y)
        path.close()

        self.c.setFillColor(Color(0.831, 0.647, 0.455, alpha=0.15))
        self.c.setStrokeColor(self.T.AMBER)
        self.c.setLineWidth(1.5)
        self.c.drawPath(path, fill=1, stroke=1)

        # Data points
        for x, y in data_points:
            self.c.setFillColor(self.T.AMBER)
            self.c.circle(x, y, 3, fill=1, stroke=0)

        # Labels
        for i, label in enumerate(labels):
            lx, ly = polar_to_xy(angles[i], radius + 16)
            align = 'center'
            if math.cos(angles[i]) > 0.3:
                align = 'left'
                lx += 4
            elif math.cos(angles[i]) < -0.3:
                align = 'right'
                lx -= 4
            self._draw_text(lx, ly - 3, label, self.T.FONT, 8,
                            self.T.TEXT_BODY, align=align)

    # -------------------------------------------------------------------------
    # PAGE BUILDERS
    # -------------------------------------------------------------------------

    def add_cover_page(self, hero_number, hero_label, hero_sublabel,
                       kpis, methodology_text, methodology_detail=''):
        """
        Build the cover/hero page.

        kpis: list of (value, label) tuples, typically 3
        """
        self._new_page(with_header=False)
        y = self._content_top()

        # Title block (centered)
        center_x = self.T.PAGE_W / 2
        self._draw_spaced_text(
            center_x - self.c.stringWidth(self.title.upper(), self.T.FONT_BOLD, 22) / 2 -
            len(self.title) * 2,
            y, self.title.upper(), self.T.FONT_BOLD, 22,
            self.T.TEXT_PRIMARY, spacing=4
        )
        y -= 28
        self._draw_text(center_x, y, self.descriptor or '',
                        self.T.FONT, 14, self.T.TEXT_BODY, align='center')
        y -= 18
        meta = f"{self.subject} · {self.date}"
        if self.descriptor:
            meta += f" · {self.descriptor}"
        self._draw_text(center_x, y, meta, self.T.FONT, 10,
                        self.T.TEXT_MUTED, align='center')
        y -= 48

        # Hero stat
        self._draw_text(center_x, y, str(hero_number), self.T.FONT_BOLD, 84,
                        self.T.AMBER, align='center')
        y -= 20
        self._draw_text(center_x, y, hero_label, self.T.FONT, 14,
                        self.T.TEXT_PRIMARY, align='center')
        y -= 16
        self._draw_text(center_x, y, hero_sublabel, self.T.FONT, 10,
                        self.T.TEXT_SECONDARY, align='center')
        y -= 36

        # KPI pills
        pill_w = 120
        pill_h = 50
        gap = 20
        total_w = len(kpis) * pill_w + (len(kpis) - 1) * gap
        start_x = (self.T.PAGE_W - total_w) / 2

        for i, (val, label) in enumerate(kpis):
            px = start_x + i * (pill_w + gap)
            py = y

            # Pill background
            self.c.setFillColor(self.T.BG_CARD)
            self.c.setStrokeColor(self.T.BORDER_SUBTLE)
            self.c.setLineWidth(0.5)
            self.c.roundRect(px, py - pill_h, pill_w, pill_h, 6, fill=1, stroke=1)

            # Value
            self._draw_text(px + pill_w / 2, py - 22, str(val),
                            self.T.FONT_BOLD, 24,
                            self.T.AMBER if i == 0 else self.T.TEXT_PRIMARY,
                            align='center')
            # Label
            self._draw_spaced_text(
                px + pill_w / 2 - self.c.stringWidth(label.upper(), self.T.FONT, 7.5) / 2,
                py - 40, label.upper(), self.T.FONT, 7.5,
                self.T.TEXT_SECONDARY, spacing=0.8
            )

        y -= pill_h + 24

        # Accent line
        y = self._draw_accent_line(y, full=True)
        y -= 4

        # Methodology paragraph
        y = self._draw_wrapped_text(
            self._x(), y, methodology_text,
            self.T.CONTENT_W, self.T.FONT, 10.5, self.T.TEXT_BODY, leading=16
        )

        if methodology_detail:
            y -= 4
            y = self._draw_wrapped_text(
                self._x(), y, methodology_detail,
                self.T.CONTENT_W, self.T.FONT, 9, self.T.TEXT_SECONDARY, leading=14
            )

    def add_distribution_page(self, dist_subtitle, marker_pos, marker_label,
                              axis_labels, explanation,
                              positioning_subtitle, cards):
        """
        Build the distribution/positioning page.

        cards: list of (title, value, description) tuples
        """
        self._new_page()
        y = self._content_top()

        y = self._draw_section_title(y, 'Population Distribution', dist_subtitle)
        y = self._draw_bell_curve(y, marker_pos, marker_label, axis_labels)
        y -= 4
        y = self._draw_wrapped_text(self._x(), y, explanation,
                                     self.T.CONTENT_W, self.T.FONT, 10,
                                     self.T.TEXT_BODY, leading=15)
        y -= 8
        y = self._draw_accent_line(y, full=True)
        y -= 4

        # Positioning section
        self._draw_spaced_text(self._x(), y, 'CONTEXTUAL POSITIONING',
                               self.T.FONT_BOLD, 14, self.T.TEXT_PRIMARY, spacing=2)
        y -= 20
        self._draw_text(self._x(), y, positioning_subtitle,
                        self.T.FONT, 13, self.T.TEXT_BODY)
        y -= 24

        # 2x2 card grid
        card_w = (self.T.CONTENT_W - 12) / 2
        card_h = 90
        for i, (title, value, desc) in enumerate(cards[:4]):
            col = i % 2
            row = i // 2
            cx = self._x() + col * (card_w + 12)
            cy = y - row * (card_h + 10)
            self._draw_card(cx, cy, card_w, card_h, title, value, desc)

    def add_radar_page(self, subtitle, values, labels, analysis_text, max_val=None):
        """Build the radar/profile page."""
        self._new_page()
        y = self._content_top()

        y = self._draw_section_title(y, 'Subcomponent Profile', subtitle)

        # Radar chart (centered, with legend to the right)
        chart_cx = self._x() + 130
        chart_cy = y - 130
        self._draw_radar_chart(chart_cx, chart_cy, 100, values, labels, max_val)

        # Legend to the right of chart
        legend_x = self._x() + 290
        legend_y = y - 40
        for i, (label, val) in enumerate(zip(labels, values)):
            self._draw_text(legend_x, legend_y - i * 20, label,
                            self.T.FONT, 10, self.T.TEXT_BODY)
            self._draw_text(legend_x + 170, legend_y - i * 20, str(val),
                            self.T.FONT_BOLD, 10, self.T.AMBER, align='right')

        y = chart_cy - 120

        # Analysis paragraph
        y = self._draw_wrapped_text(self._x(), y, analysis_text,
                                     self.T.CONTENT_W, self.T.FONT, 10,
                                     self.T.TEXT_BODY, leading=15)

    def add_evidence_page(self, subtitle, table_headers, table_rows,
                          col_widths=None, signals=None):
        """
        Build the evidence table page.

        signals: list of (title, analysis_text) tuples for narrative subsections
        """
        self._new_page()
        y = self._content_top()

        y = self._draw_section_title(y, 'Evidence Base', subtitle)

        self._draw_text(self._x(), y, 'Source Weighting',
                        self.T.FONT_BOLD, 13, self.T.TEXT_PRIMARY)
        y -= 20

        y = self._draw_table(y, table_headers, table_rows, col_widths)
        y -= 8

        if signals:
            self._draw_text(self._x(), y, 'Strongest Signals',
                            self.T.FONT_BOLD, 13, self.T.TEXT_PRIMARY)
            y -= 20
            for title, text in signals:
                self._draw_text(self._x(), y, title, self.T.FONT_BOLD, 11,
                                self.T.TEXT_PRIMARY)
                y -= 14
                y = self._draw_wrapped_text(self._x(), y, text,
                                             self.T.CONTENT_W, self.T.FONT, 10,
                                             self.T.TEXT_BODY, leading=15)
                y -= 8

    def add_comparison_page(self, title, subtitle, intro,
                            headers, rows, col_widths=None, summary=''):
        """Build a comparison grid page."""
        self._new_page()
        y = self._content_top()

        y = self._draw_section_title(y, title, subtitle)

        if intro:
            y = self._draw_wrapped_text(self._x(), y, intro,
                                         self.T.CONTENT_W, self.T.FONT, 10,
                                         self.T.TEXT_BODY, leading=15)
            y -= 8

        y = self._draw_table(y, headers, rows, col_widths)

        if summary:
            y -= 4
            y = self._draw_wrapped_text(self._x(), y, summary,
                                         self.T.CONTENT_W, self.T.FONT, 10,
                                         self.T.TEXT_BODY, leading=15)

    def add_narrative_page(self, title, subtitle, sections, callout=None):
        """
        Build a narrative analysis page.

        sections: list of (subsection_title, text) tuples
        callout: (title, text) tuple for optional callout box
        """
        self._new_page()
        y = self._content_top()

        y = self._draw_section_title(y, title, subtitle)

        for sec_title, sec_text in sections:
            self._draw_text(self._x(), y, sec_title, self.T.FONT_BOLD, 13,
                            self.T.TEXT_PRIMARY)
            y -= 18
            y = self._draw_wrapped_text(self._x(), y, sec_text,
                                         self.T.CONTENT_W, self.T.FONT, 10,
                                         self.T.TEXT_BODY, leading=15)
            y -= 12

        if callout:
            ct, ctxt = callout
            # Callout box
            box_x = self._x()
            # Estimate height
            style = ParagraphStyle('cb', fontName=self.T.FONT, fontSize=10,
                                   leading=15, textColor=self.T.TEXT_BODY)
            p = Paragraph(ctxt, style)
            w, h = p.wrap(self.T.CONTENT_W - 36, 400)
            box_h = h + 44

            self.c.setFillColor(self.T.BG_CALLOUT)
            self.c.roundRect(box_x, y - box_h, self.T.CONTENT_W, box_h,
                             4, fill=1, stroke=0)
            # Left amber border
            self.c.setFillColor(self.T.AMBER)
            self.c.rect(box_x, y - box_h, 3, box_h, fill=1, stroke=0)

            # Callout title
            self._draw_spaced_text(box_x + 18, y - 20, ct.upper(),
                                   self.T.FONT_BOLD, 11, self.T.AMBER, spacing=1.5)
            # Callout text
            p.drawOn(self.c, box_x + 18, y - box_h + 12)
            y -= box_h + 12

    def add_trait_page(self, title, subtitle, intro, headers, rows,
                       analysis_title='', analysis_text=''):
        """Build a trait/matrix page."""
        self._new_page()
        y = self._content_top()

        y = self._draw_section_title(y, title, subtitle)

        if intro:
            y = self._draw_wrapped_text(self._x(), y, intro,
                                         self.T.CONTENT_W, self.T.FONT, 10,
                                         self.T.TEXT_BODY, leading=15)
            y -= 8

        self._draw_text(self._x(), y, 'Key Attributes',
                        self.T.FONT_BOLD, 13, self.T.TEXT_PRIMARY)
        y -= 20

        y = self._draw_table(y, headers, rows)
        y -= 8

        if analysis_title:
            self._draw_text(self._x(), y, analysis_title, self.T.FONT_BOLD, 13,
                            self.T.TEXT_PRIMARY)
            y -= 18
            y = self._draw_wrapped_text(self._x(), y, analysis_text,
                                         self.T.CONTENT_W, self.T.FONT, 10,
                                         self.T.TEXT_BODY, leading=15)

    def add_methodology_page(self, subtitle, sections, change_items=None):
        """
        Build the methodology page.

        sections: list of (title, text) tuples
        change_items: list of (title, description) for "what would change" section
        """
        self._new_page()
        y = self._content_top()

        y = self._draw_section_title(y, 'Analytical Methodology', subtitle)

        for sec_title, sec_text in sections:
            self._draw_text(self._x(), y, sec_title, self.T.FONT_BOLD, 13,
                            self.T.TEXT_PRIMARY)
            y -= 18
            y = self._draw_wrapped_text(self._x(), y, sec_text,
                                         self.T.CONTENT_W, self.T.FONT, 10,
                                         self.T.TEXT_BODY, leading=15)
            y -= 12

        if change_items:
            self._draw_text(self._x(), y, 'What Would Change the Assessment',
                            self.T.FONT_BOLD, 13, self.T.TEXT_PRIMARY)
            y -= 20

            for item_title, item_desc in change_items:
                # Subtle border top
                self.c.setStrokeColor(self.T.BORDER_SUBTLE)
                self.c.setLineWidth(0.5)
                self.c.line(self._x(), y + 4, self._x() + self.T.CONTENT_W, y + 4)

                self._draw_text(self._x(), y - 8, item_title, self.T.FONT_BOLD, 10.5,
                                self.T.TEXT_PRIMARY)
                y -= 20
                y = self._draw_wrapped_text(self._x(), y, item_desc,
                                             self.T.CONTENT_W, self.T.FONT, 9.5,
                                             self.T.TEXT_BODY, leading=14)
                y -= 8

    def add_footer_page(self, report_type_disclaimer, sources, usage_disclaimer):
        """Build the footer/disclaimer page."""
        self._new_page()

        # Position at bottom of page
        y = self.T.MARGIN_BOTTOM + 80

        # Divider line
        self.c.setStrokeColor(self.T.BORDER_SUBTLE)
        self.c.setLineWidth(0.5)
        self.c.line(self._x(), y + 20, self._x() + self.T.CONTENT_W, y + 20)

        # Generated date
        self._draw_text(self._x(), y, f"Generated {self.date} · {report_type_disclaimer}",
                        self.T.FONT, 9, self.T.TEXT_SECONDARY)
        y -= 16

        # Sources
        self._draw_wrapped_text(self._x(), y, f"Sources: {sources}",
                                 self.T.CONTENT_W, self.T.FONT, 8,
                                 self.T.TEXT_MUTED, leading=12)
        y -= 20

        # Usage disclaimer
        self._draw_wrapped_text(self._x(), y, usage_disclaimer,
                                 self.T.CONTENT_W, self.T.FONT, 8,
                                 self.T.TEXT_MUTED, leading=12)

    # -------------------------------------------------------------------------
    # GENERATE
    # -------------------------------------------------------------------------

    def generate(self):
        """Finalize and save the PDF."""
        self.c.save()
        print(f"PDF generated: {self.filename} ({self.page_num} pages)")
        return self.filename


# =============================================================================
# DEMO: Generate a sample report to verify the design system
# =============================================================================

def demo():
    """Generate a demo report showing all page types."""
    report = NarrativeDashboardReport(
        filename='/tmp/narrative_dashboard_demo.pdf',
        title='Sample Analysis',
        subject='Demo Subject',
        date='April 2026',
        descriptor='Full-Spectrum Assessment'
    )

    # Cover
    report.add_cover_page(
        hero_number='87.3',
        hero_label='Composite Performance Score',
        hero_sublabel='Range: 82-91 | Prior: 84.1 | 94th percentile',
        kpis=[
            ('Top 6%', 'Population rank'),
            ('94th', 'Percentile'),
            ('+3.2', 'vs. prior period'),
        ],
        methodology_text=(
            'This report synthesizes data from multiple analytical sources '
            'to produce a composite assessment. All metrics are derived from '
            'observed performance patterns mapped to standardized frameworks.'
        ),
        methodology_detail=(
            'Methodology: Multi-source triangulation weighted by reliability '
            'and independence across six primary signal categories.'
        ),
    )

    # Distribution
    report.add_distribution_page(
        dist_subtitle='Where the Subject Sits on the Curve',
        marker_pos=0.82,
        marker_label='87.3',
        axis_labels=['-2σ', '-1σ', 'Mean', '+1σ', '+2σ'],
        explanation=(
            'The shaded amber region represents the fraction at or above the '
            'composite score. At 1.6 standard deviations above the mean, this '
            'encompasses approximately 6% of the comparison population.'
        ),
        positioning_subtitle='Benchmark Comparisons',
        cards=[
            ('Peer Group A', '#2-5', 'Strong positioning within the primary comparison set.'),
            ('Peer Group B', '#8-15', 'Above median in a pre-selected high-performance cohort.'),
            ('Industry Avg', 'Top 10%', 'Well above industry baseline across all dimensions.'),
            ('Elite Cohort', '#30-50', 'Mid-pack in the most selective comparison group.'),
        ],
    )

    # Radar
    report.add_radar_page(
        subtitle='The Shape of the Performance',
        values=[92, 88, 85, 78, 90, 82],
        labels=['Dimension A', 'Dimension B', 'Dimension C',
                'Dimension D', 'Dimension E', 'Dimension F'],
        analysis_text=(
            'Profile shape matters more than the composite number. The A-D gap '
            '(~14 points) reveals a distinctive pattern that standard assessments '
            'often underweight. This asymmetry suggests specialized strength in '
            'applied domains with a processing-speed constraint.'
        ),
    )

    # Evidence
    report.add_evidence_page(
        subtitle='What the Assessment Is Built On',
        table_headers=['Signal Source', 'Weight', 'Range', 'Confidence'],
        table_rows=[
            ['Primary dataset', '30%', '85-92', 'High'],
            ['Secondary metrics', '25%', '82-90', 'High'],
            ['Behavioral signals', '20%', '80-88', 'Medium-High'],
            ['Historical record', '15%', '78-85', 'Medium'],
            ['Cross-validation', '10%', '84-91', 'Medium'],
        ],
        col_widths=[200, 60, 100, 132],
        signals=[
            ('Pattern Complexity', 'Analysis of structural patterns reveals...'),
            ('Transfer Rate', 'Cross-domain application speed indicates...'),
        ],
    )

    # Narrative
    report.add_narrative_page(
        title='Growth Trajectory',
        subtitle='Can This Score Move?',
        sections=[
            ('Upward Potential', 'Based on current trajectory and identified growth vectors...'),
            ('Plateau Risk', 'Environmental constraints may limit ceiling without intervention...'),
        ],
        callout=('Key Insight', 'The most impactful lever for continued improvement is not raw capability '
                 'increase but rather optimizing the quality of inputs the existing capability processes.'),
    )

    # Footer
    report.add_footer_page(
        report_type_disclaimer='Analytical assessment only — not a certified evaluation',
        sources='Multi-source data synthesis · Standardized framework mapping',
        usage_disclaimer='This document is a personal analytical exercise.',
    )

    report.generate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PDF Narrative Dashboard Generator')
    parser.add_argument('--output', '-o', default='/tmp/narrative_dashboard_demo.pdf',
                        help='Output PDF path')
    parser.add_argument('--demo', action='store_true', default=True,
                        help='Generate demo report')
    args = parser.parse_args()
    demo()
