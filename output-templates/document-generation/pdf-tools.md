# PDF Tools

## Purpose
Create, read, fill, extract, merge, split, and manipulate PDF documents with an AI
assistant. Covers form filling, data extraction to CSV, bulk operations, watermarking,
and PDF generation from other formats.

## What you need
Most current AI assistants can work with PDFs directly, either through a PDF tool/skill
or by using libraries such as `pypdf`, `pdfplumber`, or `reportlab`. Capabilities
generally include reading and extracting text, listing and filling form fields,
extracting tables to CSV, batch-filling from a CSV, validating structure, and generating
new PDFs. Describe what you need done and let the assistant choose the mechanism
available to it.

## Workflows

### Read & Extract
1. Locate the PDF
2. Extract text content
3. Inspect form fields if it is a fillable form
4. Extract structured tables to CSV

### Fill Forms
1. List the form field names
2. Fill the fields with field/value pairs
3. For a reusable fill, save a profile of common values and reapply it
4. For many copies, batch-fill from a CSV — one row per output document

### Create a PDF
- **From Word:** create the `.docx` first, then export to PDF
- **From PowerPoint:** create the `.pptx` first, then export to PDF
- **From HTML:** generate the HTML page, then print or render it to PDF
- **Direct:** generate a simple PDF straight from content

## Common Use Cases
- **Report PDF export** — author in Word, export to PDF for distribution
- **Form filling** — regulatory forms, applications, compliance checklists
- **Data extraction** — pull tables out of regulatory filings and reports
- **Batch processing** — fill many copies, each with different data from a CSV
- **Archiving** — convert documents to PDF for record-keeping
