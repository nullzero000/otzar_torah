from src.logic.text_normalization import clean_corpus

def search_in_corpus(corpus: dict[str, str], query: str, kq_mode: str = "ketiv", keep_maqaf: bool = False) -> list[dict]:
    results = []
    if not query.strip():
        return results

    # Normalizar el query con las mismas reglas exactas que el corpus
    clean_query = clean_corpus(query, kq_mode=kq_mode, keep_maqaf=keep_maqaf).strip()
    if not clean_query:
        return results

    for ref, raw_text in corpus.items():
        clean_text = clean_corpus(raw_text, kq_mode=kq_mode, keep_maqaf=keep_maqaf)
        if clean_query in clean_text:
            results.append({
                "reference": ref,
                "count": clean_text.count(clean_query),
                "text": clean_text
            })
            
    return results
