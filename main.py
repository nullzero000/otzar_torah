from fastapi import FastAPI, Query
from typing import Optional
import json
from torah_engine import TorahEngine

app = FastAPI()

with open("corpus.json", "r", encoding="utf-8") as f:
    raw_corpus = json.load(f)

engine = TorahEngine(
    raw_corpus=raw_corpus, 
    reading_tradition="pragmatic_search",
    consonantal_purity="distinguish_shin_sin"
)

@app.get("/search/")
def search_torah(q: str, exact: bool = False):
    return engine.search(query=q, exact=exact)

@app.get("/count/")
def count_gematria(book: str, chapter: str, verse: str):
    try:
        raw_text = raw_corpus[book][chapter][verse]
        count = engine.count_letters(raw_text)
        return {
            "reference": f"{book} {chapter}:{verse}",
            "raw": raw_text,
            "mathematical_length": count
        }
    except KeyError:
        return {"error": "Versículo no encontrado."}

@app.get("/frequency/")
def letter_frequency(
    book: Optional[str] = None, 
    chapter: Optional[str] = None, 
    verse: Optional[str] = None
):
    """
    Histograma de caracteres. Soporta agregación a nivel Torá, Libro, Capítulo o Versículo.
    """
    text_blocks = []
    
    try:
        if book and chapter and verse:
            text_blocks.append(raw_corpus[book][chapter][verse])
        elif book and chapter:
            text_blocks.extend(raw_corpus[book][chapter].values())
        elif book:
            for c in raw_corpus[book].values():
                text_blocks.extend(c.values())
        else:
            for b in raw_corpus.values():
                for c in b.values():
                    text_blocks.extend(c.values())
    except KeyError:
        return {"error": "Coordenada estructural no encontrada en el corpus."}

    # Concatenamos todo el bloque resultante asegurando un espacio entre versículos
    full_aggregated_text = " ".join(text_blocks)
    
    freq_dist = engine.get_frequency_distribution(full_aggregated_text)
    
    # Proveemos traducciones amigables para los caracteres de control
    if " " in freq_dist:
        freq_dist["ESPACIO"] = freq_dist.pop(" ")
    if "־" in freq_dist:
        freq_dist["MAQAF"] = freq_dist.pop("־")

    return {
        "scope": {
            "book": book or "All",
            "chapter": chapter or "All",
            "verse": verse or "All"
        },
        "total_characters_counted": sum(freq_dist.values()),
        "distribution": freq_dist
    }
