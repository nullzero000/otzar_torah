import os
from pathlib import Path
from typing import Dict

from src.infrastructure.pdf_ingestion import render_all_pages
from src.infrastructure.gemini_vision_client import transcribe_page
from src.infrastructure.sefaria_client import fetch_full_torah_verses_sefaria
from src.infrastructure.mechon_mamre_client import fetch_full_torah_verses
from src.infrastructure.colab_io import ensure_output_dir
from src.logic.text_normalization import clean_corpus
from src.logic.letter_frequency import count_letter_frequency
from src.logic.comparison import build_delta_table
from src.logic.checkpoint import load_checkpoint, save_checkpoint
from src.reporting.delta_chart import render_delta_chart
from src.data.reference_corpora import CANON_ZONANA

BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

def run_pipeline() -> None:
    out_dir = ensure_output_dir()
    checkpoint_file = out_dir / "pipeline_checkpoint.json"
    
    state = load_checkpoint(checkpoint_file)
    frequencies: Dict[str, Dict[str, int]] = {"canon_zonana": CANON_ZONANA}
    
    if "manuscript_pages" not in state:
        pdf_path = Path("data/manuscript.pdf")
        if pdf_path.exists():
            png_paths = render_all_pages(pdf_path, out_dir / "pages")
            transcripts = []
            for i, path in enumerate(png_paths):
                res = transcribe_page(path, i+1)
                transcripts.append(res.__dict__)
            state["manuscript_pages"] = transcripts
            save_checkpoint(checkpoint_file, state)
            
            raw_manuscript = " ".join(p["texto_transcrito"] for p in transcripts)
            clean_manuscript = clean_corpus(raw_manuscript)
            frequencies["manuscript_ocr"] = count_letter_frequency(clean_manuscript)
    
    if "sefaria_mam" not in state or isinstance(state["sefaria_mam"], str):
        state["sefaria_mam"] = fetch_full_torah_verses_sefaria("Miqra according to the Masorah")
        save_checkpoint(checkpoint_file, state)
    mam_text = " ".join(state["sefaria_mam"].values())
    frequencies["sefaria_mam"] = count_letter_frequency(clean_corpus(mam_text))
    
    if "sefaria_taamei" not in state or isinstance(state["sefaria_taamei"], str):
        state["sefaria_taamei"] = fetch_full_torah_verses_sefaria("Tanach with Ta'amei Hamikra")
        save_checkpoint(checkpoint_file, state)
    taamei_text = " ".join(state["sefaria_taamei"].values())
    frequencies["sefaria_taamei"] = count_letter_frequency(clean_corpus(taamei_text))
    
    if "mechon_mamre" not in state or isinstance(state["mechon_mamre"], str):
        state["mechon_mamre"] = fetch_full_torah_verses()
        save_checkpoint(checkpoint_file, state)
    mm_text = " ".join(state["mechon_mamre"].values())
    frequencies["mechon_mamre"] = count_letter_frequency(clean_corpus(mm_text))

    delta_table = build_delta_table(frequencies, reference_label="canon_zonana")
    print(delta_table)
    render_delta_chart(delta_table, out_dir / "deltas_vs_canon.png")
    
if __name__ == "__main__":
    run_pipeline()
