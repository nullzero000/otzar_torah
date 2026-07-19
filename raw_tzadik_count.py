import requests

BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

def flatten_hebrew_texts(data):
    """Extrae todos los strings recursivamente de la estructura de Sefaria."""
    if isinstance(data, str):
        return data
    elif isinstance(data, list):
        return "".join(flatten_hebrew_texts(item) for item in data)
    return ""

def raw_tzadik_count():
    total_regular = 0
    total_sofit = 0
    
    for book in BOOKS:
        url = f"https://www.sefaria.org/api/texts/{book}?context=0&pad=0"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        hebrew_text = flatten_hebrew_texts(data.get("he", []))
        
        # \u05E6 = צ (Tzadik)
        # \u05E5 = ץ (Tzadik Sofit)
        count_reg = hebrew_text.count('\u05E6')
        count_sof = hebrew_text.count('\u05E5')
        
        total_regular += count_reg
        total_sofit += count_sof
        
        print(f"{book} -> צ: {count_reg}, ץ: {count_sof}")

    print("-" * 30)
    print(f"TOTAL CRUDO TZADIK (צ): {total_regular}")
    print(f"TOTAL CRUDO SOFIT (ץ): {total_sofit}")
    print(f"GRAN TOTAL TZADIK: {total_regular + total_sofit}")

if __name__ == "__main__":
    raw_tzadik_count()
