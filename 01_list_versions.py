import requests
import json

def list_hebrew_versions():
    url = "https://www.sefaria.org/api/texts/versions/Genesis"
    response = requests.get(url)
    response.raise_for_status()
    versions = response.json()
    
    hebrew_versions = [v for v in versions if v.get("language") == "he"]
    
    print(f"Encontradas {len(hebrew_versions)} versiones en hebreo para Genesis:\n")
    print(f"{'VERSIÓN (versionTitle)':<45} | {'AÑO/INFO'}")
    print("-" * 75)
    
    for v in hebrew_versions:
        title = v.get("versionTitle", "N/A")
        year = v.get("versionTitleInHebrew", "")
        source = v.get("versionSource", "N/A")
        notes = str(v.get("versionNotes", ""))[:50].replace("\n", " ")
        info = f"{source} | {notes}"
        print(f"{title:<45} | {info}")

if __name__ == "__main__":
    list_hebrew_versions()
