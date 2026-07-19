from pathlib import Path
from typing import List, Optional
import fitz
from PIL import Image
import io

def extract_native_page_image(doc: fitz.Document, page_index: int) -> Optional[Image.Image]:
    """Extracts the largest embedded image from a PDF page, fallback to render."""
    page = doc[page_index]
    images = page.get_images(full=True)
    if images:
        largest_img = max(images, key=lambda img: img[2] * img[3])
        xref = largest_img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        return Image.open(io.BytesIO(image_bytes))
    
    pix = page.get_pixmap(dpi=400)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

def render_all_pages(pdf_path: str | Path, output_dir: str | Path) -> List[Path]:
    """Renders all pages of a PDF to PNG files."""
    doc = fitz.open(str(pdf_path))
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    for i in range(len(doc)):
        img = extract_native_page_image(doc, i)
        if img:
            out_path = out_dir / f"page_{i+1:04d}.png"
            img.save(out_path, format="PNG")
            saved_paths.append(out_path)
            
    return saved_paths
