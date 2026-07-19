import re
import unicodedata
from typing import Literal
from src.data.reference_corpora import FINAL_TO_BASE, NIKUD_TEAMIM_RANGE, BASE_LETTERS

SECTION_MARKER_LETTERS = "\u05e4\u05e1"
MAQAF = "\u05BE"

def purge_nikud_teamim(text: str, keep_maqaf: bool = False) -> str:
    low, high = NIKUD_TEAMIM_RANGE
    # Se exceptúa el Maqaf de la purga si keep_maqaf es True
    return "".join(ch for ch in text if not (low <= ord(ch) <= high) or (keep_maqaf and ch == MAQAF))

def strip_section_markers(text: str) -> str:
    text = re.sub(rf"[\{{\(\[<][{SECTION_MARKER_LETTERS}][\}}\)\]>]", "", text)
    text = re.sub(rf"(?<!\S)[{SECTION_MARKER_LETTERS}](?!\S)", "", text)
    return text

def normalize_finals(text: str) -> str:
    return text.translate(str.maketrans(FINAL_TO_BASE))

def resolve_ketiv_qere(text: str, mode: Literal["ketiv", "qere"] = "ketiv") -> str:
    if mode == "ketiv":
        return re.sub(r'(\S+)\s*\[([^\]]+)\]', r'\1', text)
    else:
        return re.sub(r'(\S+)\s*\[([^\]]+)\]', r'\2', text)

def restrict_to_letters_spaces_maqaf(text: str, keep_maqaf: bool = False) -> str:
    allowed = set(BASE_LETTERS)
    if keep_maqaf:
        allowed.add(MAQAF)
    return "".join(ch for ch in text if ch in allowed or ch.isspace())

def clean_corpus(text: str, kq_mode: Literal["ketiv", "qere"] = "ketiv", keep_maqaf: bool = False) -> str:
    resolved_kq = resolve_ketiv_qere(text, mode=kq_mode)
    decomposed = unicodedata.normalize("NFKD", resolved_kq)
    without_nikud = purge_nikud_teamim(decomposed, keep_maqaf)
    without_markers = strip_section_markers(without_nikud)
    normalized = normalize_finals(without_markers)
    return restrict_to_letters_spaces_maqaf(normalized, keep_maqaf)
