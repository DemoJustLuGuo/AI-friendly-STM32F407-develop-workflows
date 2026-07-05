# PDF Datasheet And App Note Workflow

Use this when the firmware task depends on MCU datasheets, register manuals, application notes, touch-key guides, chip command manuals, or screenshots inside PDFs.

## Intake Steps

1. Run `info` to get page count and text coverage.
2. Run `extract` to produce a full text file.
3. Search the text for the feature names, register names, pin names, and section titles.
4. Render the relevant pages as images.
5. Build a contact sheet for section-level visual review.
6. Compare text extraction against images for tables, bit fields, flowcharts, code snippets, and red callouts.

## Script Commands

Info:

```powershell
python <skill_dir>\scripts\pdf_evidence.py info `
  "manual.pdf" --per-page
```

Extract text:

```powershell
python <skill_dir>\scripts\pdf_evidence.py extract `
  "manual.pdf" --output "manual.pymupdf.txt"
```

Render pages:

```powershell
python <skill_dir>\scripts\pdf_evidence.py render `
  "manual.pdf" --pages 44-46,89-91 --output-dir ".pdf_pages"
```

Contact sheet:

```powershell
python <skill_dir>\scripts\pdf_evidence.py contact `
  "manual.pdf" --pages 109-116 --output ".pdf_pages/twi_109_116.jpg"
```

## Evidence Rules

- Do not trust text extraction alone for register bit tables.
- Do not trust a screenshot alone when searchable text names the register differently.
- Preserve page numbers in notes and generated image filenames.
- If a page has little or garbled text, use rendered images as the primary evidence.
- When a PDF is an application guide, inspect code snippets and Keil UI screenshots visually.
- For SinOne/MCU tool manuals, inspect screenshots for required project structure, exported driver folders, Keil options, memory model, linker choice, and add-file instructions. These screenshots can override assumptions from generic architecture rules.
- When a PDF is a datasheet, inspect electrical notes, pin alternate-function tables, reset values, interrupt tables, and timing formulas.

## Windows Unicode Path Note

If a Chinese PDF filename becomes `????.pdf` or raises an invalid-argument error, do not conclude the file is missing. Use Python 3.12/3.11 with UTF-8 mode, enumerate files using `Path.glob('*.pdf')`, or pass an ASCII symlink/copy path to `pdf_evidence.py`.

## Output Pattern

For each peripheral or feature, record:

```text
Manual:
Pages:
Text evidence:
Image evidence:
Registers / bits:
Required init order:
Flags to clear:
Timeout or safety rule:
Firmware files affected:
Open questions:
```
