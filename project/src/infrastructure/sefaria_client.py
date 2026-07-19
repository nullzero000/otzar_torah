import time
import requests
from bs4 import BeautifulSoup
from src.data.reference_corpora import TORAH_BOOKS
from src.infrastructure.http_retry import with_backoff

SEFARIA_BASE_URL = "https://www.sefaria.org/api/v3/texts"

def _clean_sefaria_html(raw_text: str) -> str:
    soup = BeautifulSoup(raw_text, "html.parser")
    for footnote_marker in soup.find_all("sup", class_="footnote-marker"):
        footnote_marker.decompose()
    for footnote in soup.find_all("i", class_="footnote"):
        footnote.decompose()
    return soup.get_text(separator=" ", strip=True)

@with_backoff()
def fetch_book_verses(book: str, version_title: str, language: str = "hebrew") -> dict[str, str]:
    url = f"{SEFARIA_BASE_URL}/{book}"
    params = {"version": f"{language}|{version_title}", "context": 0, "commentary": 0}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    versions = payload.get("versions", [])
    if not versions:
        raise ValueError(f"Sefaria no devolvió versiones para {book} / {version_title}")
    
    chapters = versions[0].get("text", [])
    verses: dict[str, str] = {}
    
    for chapter_index, chapter_verses in enumerate(chapters, start=1):
        if not isinstance(chapter_verses, list):
            continue
        for verse_index, verse_text in enumerate(chapter_verses, start=1):
            if verse_text:
                verses[f"{book}:{chapter_index}:{verse_index}"] = _clean_sefaria_html(verse_text)
                
    return verses

def fetch_full_torah_verses_sefaria(version_title: str, language: str = "hebrew", throttle_seconds: float = 1.0) -> dict[str, str]:
    all_verses: dict[str, str] = {}
    for book in TORAH_BOOKS:
        all_verses.update(fetch_book_verses(book, version_title, language))
        time.sleep(throttle_seconds)
    return all_verses
