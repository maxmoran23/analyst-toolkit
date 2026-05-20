# HTML Email Template — Design System

A design system for building clean, mobile-friendly HTML emails: digest emails,
status updates, intelligence briefs, report deliveries. Dark header bar, indigo accent,
table-based layout that renders reliably across email clients (including Gmail, which
strips many modern CSS features).

This document is a reusable spec — a color palette, typography scale, base template,
and component library. Hand it to an AI assistant and ask it to assemble an email from
the components.

## Why table-based layout

Email clients are not browsers. Flexbox, CSS Grid, and `box-shadow` are unreliable or
stripped entirely (Gmail is the strictest common client). This system uses
`<table role="presentation">` for all layout, inline styles on every element, and a
fixed 600px content width — the patterns that render consistently everywhere.

---

## Design System

### Color Palette

| Token | Hex | Use |
|-------|-----|-----|
| header-bg | `#16162a` | Dark header bar |
| accent | `#6c63ff` | Section titles, borders, status badge |
| positive | `#10b981` | Up / positive / favorable values |
| negative | `#ef4444` | Down / negative / unfavorable values |
| summary-bg | `#f0f4ff` | Summary box background |
| summary-border | `#6c63ff` | Summary box left border |
| body-bg | `#f4f4f7` | Email outer background |
| card-bg | `#ffffff` | Email card background |
| text-primary | `#1f2937` | Body text |
| text-secondary | `#6b7280` | Supporting text, labels |
| text-muted | `#9ca3af` | Meta text, footer, table headers |
| border | `#e8e8ed` | Section borders, table header border |
| border-light | `#f0f0f5` | Row dividers |
| critical-bg / critical-text | `#fef2f2` / `#dc2626` | CRITICAL severity badge |
| high-bg / high-text | `#fff7ed` / `#ea580c` | HIGH severity badge |
| medium-bg / medium-text | `#fefce8` / `#ca8a04` | MEDIUM severity badge |
| low-bg / low-text | `#f0fdf4` / `#16a34a` | LOW severity badge |
| callout-bg / callout-border | `#eff6ff` / `#bfdbfe` | Info callout box |
| callout-text | `#1e40af` | Callout heading text |
| wins-bg | `#f0fdf4` | Positive / wins section tint |
| lessons-bg | `#fffbeb` | Lessons / caution section tint |

### Typography

| Element | Style |
|---------|-------|
| Font stack | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif` |
| Title | 20px, font-weight 700, white, letter-spacing 1px |
| Date line | 13px, `#8b8fa3` |
| Section title | 11px, font-weight 700, `#6c63ff`, uppercase, letter-spacing 2px, 2px bottom border |
| Body text | 14px, `#374151`, line-height 1.6 |
| Table header | 11px, font-weight 600, `#8b8fa3`, uppercase |
| Table data | 14px, `#374151` |
| Bullet marker | `#6c63ff`, using `&#x25CF;` (filled circle) |
| Footer | 11px, `#9ca3af` |

### Layout Rules

- **Table-based layout** — not flexbox or CSS Grid (email-client compatibility)
- **Max width:** 600px, centered
- **Card:** white background, 8px border-radius, no box-shadow (clients strip it)
- **Section padding:** 24px top, 32px horizontal
- **Use `<table role="presentation">`** for all layout tables
- **Inline every style** — `<style>` blocks and external CSS are unreliable in email

---

## Base Template

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f4f4f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;">
<tr><td align="center" style="padding:20px 0;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;">

<!-- ===== HEADER ===== -->
<tr><td style="background-color:#16162a;padding:24px 32px;">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td><span style="color:#ffffff;font-size:20px;font-weight:700;letter-spacing:1px;">{{TITLE}}</span><br>
    <span style="color:#8b8fa3;font-size:13px;">{{DATE}}</span></td>
    <td align="right" valign="top"><span style="background-color:#6c63ff;color:#fff;padding:4px 12px;border-radius:12px;font-size:11px;font-weight:700;">{{BADGE}}</span></td>
  </tr></table>
</td></tr>

<!-- ===== SUMMARY BOX ===== -->
<tr><td style="padding:24px 32px 0 32px;">
  <div style="background-color:#f0f4ff;border-left:4px solid #6c63ff;padding:16px 20px;border-radius:0 6px 6px 0;font-size:14px;line-height:1.6;color:#374151;">
    {{SUMMARY_TEXT}}
  </div>
</td></tr>

<!-- ===== CONTENT SECTION (repeat for each) ===== -->
<tr><td style="padding:24px 32px 0 32px;">
  <div style="font-size:11px;font-weight:700;color:#6c63ff;letter-spacing:2px;text-transform:uppercase;border-bottom:2px solid #6c63ff;padding-bottom:8px;margin-bottom:16px;">{{SECTION_TITLE}}</div>
  {{SECTION_CONTENT}}
</td></tr>

<!-- ===== FOOTER ===== -->
<tr><td style="padding:24px 32px;border-top:1px solid #e8e8ed;">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="font-size:11px;color:#9ca3af;">{{FOOTER_LEFT}}</td>
    <td align="right" style="font-size:11px;color:#9ca3af;">{{FOOTER_RIGHT}}</td>
  </tr></table>
</td></tr>

</table>
</td></tr></table>
</body></html>
```

---

## Component Library

### Data Table

```html
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;">
  <tr>
    <td style="padding:8px 0;color:#8b8fa3;font-size:11px;font-weight:600;text-transform:uppercase;border-bottom:1px solid #e8e8ed;">Item</td>
    <td align="right" style="padding:8px 0;color:#8b8fa3;font-size:11px;font-weight:600;text-transform:uppercase;border-bottom:1px solid #e8e8ed;">Value</td>
    <td align="right" style="padding:8px 0;color:#8b8fa3;font-size:11px;font-weight:600;text-transform:uppercase;border-bottom:1px solid #e8e8ed;">Change</td>
  </tr>
  <!-- Use color:#10b981 for positive, #ef4444 for negative in the change column -->
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f0f0f5;font-weight:600;">Row label</td>
    <td align="right" style="padding:10px 0;border-bottom:1px solid #f0f0f5;">1,234</td>
    <td align="right" style="padding:10px 0;border-bottom:1px solid #f0f0f5;color:#10b981;font-weight:600;">+0.93%</td>
  </tr>
</table>
```

### Metric Row (label + value)

```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f0f0f5;font-size:14px;color:#6b7280;">{{LABEL}}</td>
    <td align="right" style="padding:10px 0;border-bottom:1px solid #f0f0f5;font-size:14px;font-weight:600;color:#1f2937;">{{VALUE}}</td>
  </tr>
</table>
```

### Severity Badge

```html
<!-- CRITICAL -->
<span style="display:inline-block;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700;background:#fef2f2;color:#dc2626;">CRITICAL</span>
<!-- HIGH -->
<span style="display:inline-block;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700;background:#fff7ed;color:#ea580c;">HIGH</span>
<!-- MEDIUM -->
<span style="display:inline-block;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700;background:#fefce8;color:#ca8a04;">MEDIUM</span>
<!-- LOW -->
<span style="display:inline-block;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700;background:#f0fdf4;color:#16a34a;">LOW</span>
```

### Callout Box (key alert, highlighted note)

```html
<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:14px 18px;margin:12px 0;">
  <div style="font-size:12px;font-weight:700;color:#1e40af;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">{{CALLOUT_TITLE}}</div>
  <div style="font-size:14px;color:#1e3a5f;line-height:1.6;">{{CALLOUT_CONTENT}}</div>
</div>
```

### Bullet List

```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr><td style="padding:6px 0;font-size:14px;color:#374151;line-height:1.6;">
    <span style="color:#6c63ff;margin-right:8px;">&#x25CF;</span> {{ITEM_TEXT}}
  </td></tr>
  <tr><td style="padding:6px 0;font-size:14px;color:#374151;line-height:1.6;">
    <span style="color:#6c63ff;margin-right:8px;">&#x25CF;</span> {{ITEM_TEXT}}
  </td></tr>
</table>
```

### Comparison Table (value vs. prior period)

```html
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;">
  <tr>
    <td style="padding:8px 0;color:#8b8fa3;font-size:11px;font-weight:600;text-transform:uppercase;border-bottom:1px solid #e8e8ed;">Metric</td>
    <td align="right" style="padding:8px 0;color:#8b8fa3;font-size:11px;font-weight:600;text-transform:uppercase;border-bottom:1px solid #e8e8ed;">Value</td>
    <td align="right" style="padding:8px 0;color:#8b8fa3;font-size:11px;font-weight:600;text-transform:uppercase;border-bottom:1px solid #e8e8ed;">vs. Prior</td>
  </tr>
  <!-- Use color:#10b981 for positive delta, #ef4444 for negative -->
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f0f0f5;">Row label</td>
    <td align="right" style="padding:10px 0;border-bottom:1px solid #f0f0f5;">1,234</td>
    <td align="right" style="padding:10px 0;border-bottom:1px solid #f0f0f5;color:#10b981;font-weight:600;">+5.4%</td>
  </tr>
</table>
```

### Indicator (big number + label)

```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="padding:10px 0;font-size:14px;color:#6b7280;">{{INDICATOR_LABEL}}</td>
    <td align="right" style="padding:10px 0;">
      <span style="font-size:20px;font-weight:700;color:#ef4444;">{{VALUE}}</span>
      <span style="font-size:12px;color:#6b7280;margin-left:4px;">{{VALUE_LABEL}}</span>
    </td>
  </tr>
</table>
```

### Checklist Item (action items, TODOs)

```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr><td style="padding:6px 0;font-size:14px;color:#374151;line-height:1.6;">
    <span style="color:#d1d5db;margin-right:8px;">&#x25A1;</span> {{ACTION_ITEM}}
  </td></tr>
</table>
```

---

## Example Section Layouts

These show how the components combine into common email types. Each is a sequence of
content sections inside the base template.

### Daily / Status Brief
1. Summary box — overview of the period
2. **KEY DEVELOPMENTS** — bullet list with severity badges
3. **METRICS** — data table or metric rows
4. **SCHEDULE / NEXT** — bullet list of upcoming items
5. **PRIORITIES** — numbered bullet list

### Digest (consolidated multi-topic email)
1. Summary box — executive summary
2. One content section per topic — each a section title plus the relevant
   components (data table, bullet list, callout box)
3. **WATCH ITEMS** — callout box for things needing follow-up
4. Footer — source attribution, generation timestamp

### Weekly Review
1. Summary box — week overview
2. **WINS** — bullet list on green-tinted background (`#f0fdf4`)
3. **LESSONS** — bullet list on amber-tinted background (`#fffbeb`)
4. **ACTION ITEMS** — checklist items
5. **NEXT WEEK** — bullet list

### Report Delivery
1. Summary box — what the attached/embedded report covers
2. **TOP FINDINGS** — numbered list with severity badges
3. **PERFORMANCE** — comparison table
4. **RECOMMENDATIONS** — callout box

---

## How to Use with an AI Assistant

Ask an AI assistant to assemble an email from this spec — for example: *"Build an HTML
email using this design system. Header title 'Weekly Review', a summary box, a WINS
section and a LESSONS section as bullet lists, and an ACTION ITEMS checklist. Inline all
styles."* Provide the content; the assistant slots it into the base template and
components. Always test the result in your target email client before sending — email
rendering varies, and the table-based patterns here are chosen for maximum compatibility.
