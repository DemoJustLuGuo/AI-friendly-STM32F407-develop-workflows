#!/usr/bin/env python3
"""Extract text and render page evidence from MCU datasheets/app notes.

Dependencies:
  pip install pymupdf pillow

The script is intentionally small and JSON-friendly so Codex can use it as a
repeatable PDF intake step instead of rewriting one-off extraction snippets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def require_fitz():
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "PyMuPDF is required. Install with: python -m pip install pymupdf"
        ) from exc
    return fitz


def parse_pages(spec: str, page_count: int) -> list[int]:
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            start = int(left)
            end = int(right)
            if start > end:
                start, end = end, start
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    bad = [p for p in pages if p < 1 or p > page_count]
    if bad:
        raise SystemExit(f"Page(s) out of range 1..{page_count}: {bad}")
    return sorted(pages)


def open_doc(path: Path):
    fitz = require_fitz()
    if not path.exists():
        raise SystemExit(f"PDF not found: {path}")
    return fitz.open(path)


def cmd_info(args: argparse.Namespace) -> dict:
    doc = open_doc(Path(args.pdf))
    per_page = []
    total_chars = 0
    low_text_pages = []
    for idx, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        chars = len(text)
        total_chars += chars
        per_page.append({"page": idx, "chars": chars})
        if chars < args.low_text_threshold:
            low_text_pages.append(idx)
    return {
        "status": "ok",
        "action": "info",
        "pdf": str(Path(args.pdf).resolve()),
        "page_count": doc.page_count,
        "total_text_chars": total_chars,
        "low_text_threshold": args.low_text_threshold,
        "low_text_pages": low_text_pages,
        "per_page": per_page if args.per_page else None,
    }


def cmd_extract(args: argparse.Namespace) -> dict:
    pdf = Path(args.pdf)
    doc = open_doc(pdf)
    out = Path(args.output) if args.output else pdf.with_suffix(".pymupdf.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for idx, page in enumerate(doc, start=1):
            f.write(f"\n\n===== Page {idx} =====\n\n")
            f.write(page.get_text("text") or "")
    return {
        "status": "ok",
        "action": "extract",
        "pdf": str(pdf.resolve()),
        "output": str(out.resolve()),
        "page_count": doc.page_count,
        "chars": out.stat().st_size,
    }


def cmd_render(args: argparse.Namespace) -> dict:
    fitz = require_fitz()
    pdf = Path(args.pdf)
    doc = open_doc(pdf)
    pages = parse_pages(args.pages, doc.page_count)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scale = args.dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    outputs = []
    for p in pages:
        pix = doc[p - 1].get_pixmap(matrix=matrix, alpha=False)
        out = out_dir / f"page_{p:03d}.png"
        pix.save(str(out))
        outputs.append(str(out.resolve()))
    return {
        "status": "ok",
        "action": "render",
        "pdf": str(pdf.resolve()),
        "pages": pages,
        "output_dir": str(out_dir.resolve()),
        "outputs": outputs,
    }


def cmd_contact(args: argparse.Namespace) -> dict:
    try:
        from PIL import Image, ImageDraw, ImageOps  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise SystemExit("Pillow is required. Install with: python -m pip install pillow") from exc

    fitz = require_fitz()
    pdf = Path(args.pdf)
    doc = open_doc(pdf)
    pages = parse_pages(args.pages, doc.page_count)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    scale = args.dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    thumbs = []
    for p in pages:
        pix = doc[p - 1].get_pixmap(matrix=matrix, alpha=False)
        mode = "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        ratio = args.thumb_width / img.width
        img = img.resize((args.thumb_width, int(img.height * ratio)))
        canvas = ImageOps.expand(img, border=(0, 38, 0, 0), fill="white")
        draw = ImageDraw.Draw(canvas)
        draw.text((10, 10), f"Page {p}", fill="black")
        thumbs.append(canvas)

    cols = max(1, args.columns)
    row_heights = []
    for start in range(0, len(thumbs), cols):
        row_heights.append(max(img.height for img in thumbs[start : start + cols]))
    width = cols * args.thumb_width
    height = sum(row_heights)
    sheet = Image.new("RGB", (width, height), "white")
    y = 0
    for row_idx, start in enumerate(range(0, len(thumbs), cols)):
        row = thumbs[start : start + cols]
        for col_idx, img in enumerate(row):
            sheet.paste(img, (col_idx * args.thumb_width, y))
        y += row_heights[row_idx]
    sheet.save(out, quality=88)
    return {
        "status": "ok",
        "action": "contact",
        "pdf": str(pdf.resolve()),
        "pages": pages,
        "output": str(out.resolve()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PDF evidence extraction for embedded manuals")
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="show page count and text coverage")
    info.add_argument("pdf")
    info.add_argument("--low-text-threshold", type=int, default=80)
    info.add_argument("--per-page", action="store_true")
    info.set_defaults(func=cmd_info)

    extract = sub.add_parser("extract", help="extract all text")
    extract.add_argument("pdf")
    extract.add_argument("--output")
    extract.set_defaults(func=cmd_extract)

    render = sub.add_parser("render", help="render selected pages as PNG")
    render.add_argument("pdf")
    render.add_argument("--pages", required=True, help="1-based pages, e.g. 1-3,8,10")
    render.add_argument("--output-dir", required=True)
    render.add_argument("--dpi", type=int, default=144)
    render.set_defaults(func=cmd_render)

    contact = sub.add_parser("contact", help="render selected pages into a contact sheet")
    contact.add_argument("pdf")
    contact.add_argument("--pages", required=True)
    contact.add_argument("--output", required=True)
    contact.add_argument("--dpi", type=int, default=144)
    contact.add_argument("--thumb-width", type=int, default=900)
    contact.add_argument("--columns", type=int, default=2)
    contact.set_defaults(func=cmd_contact)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

