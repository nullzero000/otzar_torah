import requests
import re

BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

def extract_sofit_words():
    results = []
    
    for book in BOOKS:
        url = f"https://www.sefaria.org/api/texts/{book}?context=0&pad=0"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        chapters = data.get("he", [])
        
        for c_idx, chapter in enumerate(chapters):
            if isinstance(chapter, str):
                chapter = [chapter]
                
            for v_idx, verse in enumerate(chapter):
                if not isinstance(verse, str):
                    continue
                
                words = verse.split()
                for word in words:
                    if '\u05E5' in word:
                        clean_word = re.sub(r'[^\u05D0-\u05EA\u05E5]', '', word)
                        ref = f"{book} {c_idx + 1}:{v_idx + 1}"
                        results.append((ref, word, clean_word))
                        
    print(f"Total palabras con Tzadik Sofit encontradas: {len(results)}")
    print("Muestra de las primeras 30 ocurrencias:\n")
    print(f"{'REFERENCIA':<20} | {'PALABRA CRUDA':<25} | {'LETRAS (LIMPIO)'}")
    print("-" * 70)
    
    for ref, raw_word, clean_word in results[:30]:
        print(f"{ref:<20} | {raw_word:<25} | {clean_word}")

if __name__ == "__main__":
    extract_sofit_words()
