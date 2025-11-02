# core/pdf/pdf_to_image_converter.py
import fitz  # PyMuPDF
from pathlib import Path

def pdf_to_image(pdf_path: str | Path, output_dir: str | Path) -> Path:
    """Convert PDF to image using PyMuPDF."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf = fitz.open(pdf_path)  # ✅ Open directly from file path
    page = pdf.load_page(0)
    pix = page.get_pixmap()
    image_path = output_dir / f"{pdf_path.stem}_page1.png"
    pix.save(image_path)
    pdf.close()

    return image_path
