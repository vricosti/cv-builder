#!/usr/bin/env python3
"""Build CV outputs from a YAML source.

Usage:
    ./build.py                  # build from cv.yaml -> output/cv.{html,pdf,docx}
    ./build.py cv-en.yaml       # build from cv-en.yaml -> output/cv-en.{html,pdf,docx}
    ./build.py --format pdf     # only generate the PDF
    ./build.py --format html    # only generate the HTML (fastest, useful while editing)

Requires: PyYAML, Jinja2 (see requirements.txt).
External tools (auto-detected):
    - Chromium / Chrome (headless) for PDF rendering
    - LibreOffice (--headless) for DOCX conversion
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, ChainableUndefined

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "output"


def render_html(yaml_path: Path, template_name: str = "cv.html.j2") -> tuple[Path, str]:
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        undefined=ChainableUndefined,
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template(template_name)
    html = tpl.render(**data)
    out = OUTPUT / f"{yaml_path.stem}.html"
    out.write_text(html, encoding="utf-8")
    return out, html


def find_chromium() -> str | None:
    for candidate in ("google-chrome", "chromium", "chromium-browser"):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def render_pdf(html_path: Path) -> Path:
    chrome = find_chromium()
    if not chrome:
        raise RuntimeError("Chromium/Chrome introuvable - impossible de générer le PDF")
    pdf_path = html_path.with_suffix(".pdf")
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        "--virtual-time-budget=10000",
        html_path.resolve().as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(f"chromium a échoué : {result.stderr}")
    return pdf_path


def render_docx(html_path: Path) -> Path:
    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not libreoffice:
        raise RuntimeError("LibreOffice introuvable - impossible de générer le DOCX")
    cmd = [
        libreoffice,
        "--headless",
        "--convert-to", "docx:MS Word 2007 XML",
        "--outdir", str(OUTPUT),
        str(html_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    docx_path = html_path.with_suffix(".docx")
    if result.returncode != 0 or not docx_path.exists():
        raise RuntimeError(f"libreoffice a échoué : {result.stderr or result.stdout}")
    return docx_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", default="cv.yaml", help="fichier YAML source (défaut: cv.yaml)")
    parser.add_argument(
        "--format",
        choices=["all", "html", "pdf", "docx"],
        default="all",
        help="format de sortie (défaut: all)",
    )
    args = parser.parse_args()

    yaml_path = Path(args.source)
    if not yaml_path.is_absolute():
        yaml_path = ROOT / yaml_path
    if not yaml_path.exists():
        print(f"erreur: fichier introuvable: {yaml_path}", file=sys.stderr)
        return 1

    OUTPUT.mkdir(exist_ok=True)

    print(f"→ rendu HTML depuis {yaml_path.name}")
    html_path, _ = render_html(yaml_path)
    print(f"  ✓ {html_path.relative_to(ROOT)}")

    if args.format in ("all", "pdf"):
        print("→ rendu PDF (Chromium headless)")
        pdf_path = render_pdf(html_path)
        print(f"  ✓ {pdf_path.relative_to(ROOT)}")

    if args.format in ("all", "docx"):
        print("→ rendu DOCX (LibreOffice)")
        docx_path = render_docx(html_path)
        print(f"  ✓ {docx_path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
