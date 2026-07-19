import time
import re
import requests
from bs4 import BeautifulSoup
from src.data.reference_corpora import MECHON_MAMRE_BOOK_CODES, TORAH_BOOKS
from src.infrastructure.http_retry import with_backoff

MECHON_MAMRE_BASE_URL = "https://mechon-mamre.org/p/pt"
PARASHA_MARKERS = {"{\u05e4}", "{\u05e1}"}
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
MIN_HEBREW_LETTERS_PER_CHAPTER = 50

def _hebrew_letter_count(text: str) -> int:
    return sum(1 for ch in text if "\u05d0" <= ch <= "\u05ea")

def _strip_verse_marker_and_parasha_tags(hebrew_cell) -> str:
    cell_copy = BeautifulSoup(str(hebrew_cell), "html.parser")
    for qere_span in cell_copy.find_all("span", class_="qri"):
        qere_span.replace_with(f" [{qere_span.get_text(strip=True)}]")
        
    first_bold = cell_copy.find("b")
    if first_bold is not None:
        first_bold.decompose()
        
    for anchor in cell_copy.find_all("a"):
        if anchor.get_text(strip=True) in PARASHA_MARKERS:
            anchor.decompose()
            
    text = cell_copy.get_text(separator=" ", strip=True)
    return re.sub(r"\{[רש]\}", "", text)

@with_backoff()
def fetch_chapter_verses(book: str, chapter: int) -> dict[str, str]:
    book_code = MECHON_MAMRE_BOOK_CODES[book]
    url = f"{MECHON_MAMRE_BASE_URL}/pt{book_code:02d}{chapter:02d}.htm"
    response = requests.get(url, headers=BROWSER_HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    verses: dict[str, str] = {}
    verse_index = 0
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        hebrew_cell = cells[0]
        if hebrew_cell.find("b") is None:
            continue
        text = _strip_verse_marker_and_parasha_tags(hebrew_cell)
        if not text:
            continue
        verse_index += 1
        verses[f"{book}:{chapter}:{verse_index}"] = text
    
    total_letters = _hebrew_letter_count("".join(verses.values()))
    if total_letters < MIN_HEBREW_LETTERS_PER_CHAPTER:
        raise ValueError(f"{book} {chapter}: solo {total_letters} letras hebreas extraídas.")
    return verses

def fetch_full_torah_verses(throttle_seconds: float = 1.0) -> dict[str, str]:
    all_verses: dict[str, str] = {}
    for book, chapter_count in TORAH_BOOKS.items():
        for chapter in range(1, chapter_count + 1):
            all_verses.update(fetch_chapter_verses(book, chapter))
            time.sleep(throttle_seconds)
    return all_verses
