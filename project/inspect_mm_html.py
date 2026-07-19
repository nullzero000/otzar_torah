import requests
from bs4 import BeautifulSoup

def inspect_exodus_37_8():
    url = "https://mechon-mamre.org/p/pt/pt0237.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    verse_index = 0
    
    print(f"\n{'='*75}\nRAW HTML - MECHON MAMRE (EXODUS 37:8)\n{'='*75}")
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        hebrew_cell = cells[0]
        if hebrew_cell.find("b") is None:
            continue
            
        verse_index += 1
        if verse_index == 8:
            print(hebrew_cell.prettify())
            break

if __name__ == "__main__":
    inspect_exodus_37_8()
