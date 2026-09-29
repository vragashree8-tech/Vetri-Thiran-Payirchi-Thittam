from fpdf import FPDF
from pathlib import Path
from app.services.images import ROOT

EXPORT_DIR = ROOT / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _pdf_text(value: str) -> str:
    # Built-in PDF fonts cover Latin-1; replace other symbols to avoid runtime encoding failures.
    return str(value).encode("latin-1", "replace").decode("latin-1")


def save_pdf(comic: dict) -> Path:
    path = EXPORT_DIR / f"comic-{comic['id']}.pdf"
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    for panel in comic["panels"]:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 19)
        pdf.multi_cell(180, 12, _pdf_text(f"{comic['title']} - Panel {panel['number']}"))
        pdf.ln(3)
        image_path = ROOT / panel["image_url"].lstrip("/")
        pdf.image(str(image_path), x=15, y=pdf.get_y(), w=180, h=110)
        pdf.ln(114)
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(180, 9, _pdf_text(panel["title"]))
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(180, 7, _pdf_text(panel["scene_description"]))
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(180, 7, _pdf_text(panel["narration"]))
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(180, 7, _pdf_text(panel["dialogue"]))
    pdf.output(str(path))
    return path

