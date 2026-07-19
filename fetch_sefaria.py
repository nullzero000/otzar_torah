import asyncio
import httpx
import json
import re
import html

BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
BASE_URL = "https://www.sefaria.org/api/texts/"

async def fetch_book(client: httpx.AsyncClient, book: str) -> dict:
    print(f"Descargando y sanitizando {book}...")
    url = f"{BASE_URL}{book}?context=0&pad=0"
    
    response = await client.get(url, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    
    book_dict = {}
    chapters = data.get("he", [])
    
    for chap_idx, verses in enumerate(chapters):
        chapter_num = str(chap_idx + 1)
        book_dict[chapter_num] = {}
        
        for verse_idx, verse_text in enumerate(verses):
            verse_num = str(verse_idx + 1)
            
            # 1. Convertir entidades HTML (ej. &nbsp; -> espacio real)
            clean_verse = html.unescape(verse_text)
            
            # 2. WHITELIST: Conservar SOLO el bloque Unicode Hebreo y espacios.
            # Destruye inglés, números, llaves {}, [], y puntuación occidental.
            clean_verse = re.sub(r'[^\u0590-\u05FF\s]', '', clean_verse)
            
            # 3. Colapsar espacios múltiples generados por la destrucción de letras en 1 solo espacio
            clean_verse = re.sub(r'\s+', ' ', clean_verse).strip()
            
            book_dict[chapter_num][verse_num] = clean_verse
            
    return book_dict

async def build_corpus():
    corpus = {}
    async with httpx.AsyncClient() as client:
        tasks = [fetch_book(client, book) for book in BOOKS]
        results = await asyncio.gather(*tasks)
        
        for book_name, book_data in zip(BOOKS, results):
            hebrew_names = {
                "Genesis": "Bereshit",
                "Exodus": "Shemot",
                "Leviticus": "Vayikra",
                "Numbers": "Bamidbar",
                "Deuteronomy": "Devarim"
            }
            corpus[hebrew_names[book_name]] = book_data

    print("Guardando corpus.json purificado...")
    with open("corpus.json", "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    print("¡Data Lake purgado con éxito!")

if __name__ == "__main__":
    asyncio.run(build_corpus())
