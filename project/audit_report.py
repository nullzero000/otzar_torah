import json
from pathlib import Path

from src.data.reference_corpora import CANON_ZONANA, TANACH_TEXT_ONLY, LETTER_NAMES
from src.logic.checkpoint import load_checkpoint
from src.logic.comparison import build_frequency_matrix, build_delta_table
from src.logic.letter_frequency import count_letter_frequency
from src.logic.text_normalization import clean_corpus

checkpoint_file = Path("output/pipeline_checkpoint.json")
state = load_checkpoint(checkpoint_file)

frequencies = {
    "canon_zonana": CANON_ZONANA,
    "tanach_text_only": TANACH_TEXT_ONLY,
}
for label in ["sefaria_mam", "sefaria_taamei", "mechon_mamre"]:
    text = " ".join(state[label].values())
    frequencies[label] = count_letter_frequency(clean_corpus(text))

matrix = build_frequency_matrix(frequencies)
print("=" * 75)
print("CONTEO ABSOLUTO, LAS 5 FUENTES, MISMA TABLA")
print("=" * 75)
print(matrix)

delta_zonana = build_delta_table(frequencies, reference_label="canon_zonana")
delta_wlc = build_delta_table(frequencies, reference_label="tanach_text_only")
print("\n" + "=" * 75)
print("DELTA CONTRA canon_zonana")
print("=" * 75)
print(delta_zonana)
print("\n" + "=" * 75)
print("DELTA CONTRA tanach_text_only (WLC)")
print("=" * 75)
print(delta_wlc)
