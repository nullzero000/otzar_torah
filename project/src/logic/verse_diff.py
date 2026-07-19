from src.logic.text_normalization import clean_corpus

KNOWN_VERSIFICATION_SHIFT_ZONES = ("Exodus:20", "Deuteronomy:5")

def _is_known_shift_zone(verse_ref: str) -> bool:
    return verse_ref.startswith(KNOWN_VERSIFICATION_SHIFT_ZONES)

def find_letter_discrepant_verses(
    sources: dict[str, dict[str, str]],
    letter: str,
    kq_mode: str = "ketiv",
    top_n: int = 50,
) -> list[dict]:
    all_refs = set()
    for verse_map in sources.values():
        all_refs.update(verse_map.keys())

    rows = []
    for verse_ref in sorted(all_refs):
        counts = {}
        raw_texts = {}
        for label, verse_map in sources.items():
            raw_text = verse_map.get(verse_ref)
            if raw_text is None:
                continue
            cleaned = clean_corpus(raw_text, kq_mode=kq_mode)
            counts[label] = cleaned.count(letter)
            raw_texts[label] = raw_text

        if len(counts) < 2:
            continue
        spread = max(counts.values()) - min(counts.values())
        if spread == 0:
            continue

        rows.append({
            "verse_ref": verse_ref,
            "counts": counts,
            "raw_texts": raw_texts,
            "spread": spread,
            "known_shift_zone": _is_known_shift_zone(verse_ref),
        })

    return sorted(rows, key=lambda r: r["spread"], reverse=True)[:top_n]
