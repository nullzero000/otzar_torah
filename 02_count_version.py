import requests
import urllib.parse
import json
import re
import argparse
from collections import Counter

BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

SOFIT_TO_REGULAR = {
    '\u05DA': '\u05DB',
    '\u05DD': '\u05DE',
    '\u05DF': '\u05E0',
    '\u05E3': '\u05E4',
    '\u05E5': '\u05E6'
}

def flatten_text(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, list):
        return "".join(flatten_text(item) for item in data)
    elif isinstance(data, dict):
        return flatten_text(data.get("text", ""))
    return ""

def process_version(version_title):
    print(f"Procesando versión: {version_title}")
    encoded_title = urllib.parse.quote(version_title)
    
    purge_pattern = re.compile(r'[\u0591-\u05BD\u05BF-\u05C7]')
    section_pattern = re.compile(r'\{[פס]\}')
    sofit_trans = str.maketrans(SOFIT_TO_REGULAR)
    global_counts = Counter()
    
    for book in BOOKS:
        url = f"https://www.sefaria.org/api/v3/texts/{book}?version=hebrew|{encoded_title}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        versions = data.get("versions", [])
        raw_text = flatten_text(versions[0]["text"]) if versions else ""
        
        if not raw_text:
            print(f"  ADVERTENCIA: {book} devolvió texto vacío. Revisar título de versión.")
        
        raw_text = section_pattern.sub('', raw_text)
        
        clean_text = purge_pattern.sub('', raw_text)
        unified_text = clean_text.translate(sofit_trans)
        base_letters = [char for char in unified_text if '\u05D0' <= char <= '\u05EA']
        
        book_counts = Counter(base_letters)
        global_counts.update(book_counts)
        print(f"  - {book}: {sum(book_counts.values())} letras")

    output_file = f"counts_{version_title.replace(' ', '_').replace('/', '-')}.json"
    
    result_payload = {
        "version": version_title,
        "total": sum(global_counts.values()),
        "distribution": dict(global_counts)
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, ensure_ascii=False, indent=4)
        
    print(f"\nConteo finalizado. Total: {result_payload['total']}. Guardado en {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conteo crudo por versión de Sefaria")
    parser.add_argument("--version", required=True, help="Título exacto de la versión (ej: 'Tanach with Ta\\'amei Hamikra')")
    args = parser.parse_args()
    process_version(args.version)
