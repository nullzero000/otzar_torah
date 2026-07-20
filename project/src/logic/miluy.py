from typing import Literal, List, Dict
from src.data.reference_corpora import FINAL_TO_BASE
from src.logic.gematria import calculate_mispar_gadol

MiluySystem = Literal['AB', 'SAG', 'MAH', 'BAN']

MILUY_EXPANSIONS = {
    'י': {'AB': 'יוד', 'SAG': 'יוד', 'MAH': 'יוד', 'BAN': 'יוד'},
    'ה': {'AB': 'הי', 'SAG': 'הי', 'MAH': 'הא', 'BAN': 'הה'},
    'ו': {'AB': 'ויו', 'SAG': 'ואו', 'MAH': 'ואו', 'BAN': 'וו'},
    'א': {'AB': 'אלף', 'SAG': 'אלף', 'MAH': 'אלף', 'BAN': 'אלף'},
    'ב': {'AB': 'בית', 'SAG': 'בית', 'MAH': 'בית', 'BAN': 'בית'},
    'ג': {'AB': 'גימל', 'SAG': 'גימל', 'MAH': 'גימל', 'BAN': 'גימל'},
    'ד': {'AB': 'דלת', 'SAG': 'דלת', 'MAH': 'דלת', 'BAN': 'דלת'},
    'ז': {'AB': 'זין', 'SAG': 'זין', 'MAH': 'זין', 'BAN': 'זין'},
    'ח': {'AB': 'חית', 'SAG': 'חית', 'MAH': 'חית', 'BAN': 'חית'},
    'ט': {'AB': 'טית', 'SAG': 'טית', 'MAH': 'טית', 'BAN': 'טית'},
    'כ': {'AB': 'כף', 'SAG': 'כף', 'MAH': 'כף', 'BAN': 'כף'},
    'ל': {'AB': 'למד', 'SAG': 'למד', 'MAH': 'למד', 'BAN': 'למד'},
    'מ': {'AB': 'מם', 'SAG': 'מם', 'MAH': 'מם', 'BAN': 'מם'},
    'נ': {'AB': 'נון', 'SAG': 'נון', 'MAH': 'נון', 'BAN': 'נון'},
    'ס': {'AB': 'סמך', 'SAG': 'סמך', 'MAH': 'סמך', 'BAN': 'סמך'},
    'ע': {'AB': 'עין', 'SAG': 'עין', 'MAH': 'עין', 'BAN': 'עין'},
    'פ': {'AB': 'פא', 'SAG': 'פא', 'MAH': 'פא', 'BAN': 'פא'},
    'צ': {'AB': 'צדי', 'SAG': 'צדי', 'MAH': 'צדי', 'BAN': 'צדי'},
    'ק': {'AB': 'קוף', 'SAG': 'קוף', 'MAH': 'קוף', 'BAN': 'קוף'},
    'ר': {'AB': 'ריש', 'SAG': 'ריש', 'MAH': 'ריש', 'BAN': 'ריש'},
    'ש': {'AB': 'שין', 'SAG': 'שין', 'MAH': 'שין', 'BAN': 'שין'},
    'ת': {'AB': 'תו', 'SAG': 'תו', 'MAH': 'תו', 'BAN': 'תו'}
}

def expand_word(text: str, system: MiluySystem, orthography: str = 'plene') -> str:
    expanded = []
    for char in text:
        if char.isspace() or char == '\u05BE':  # Ignorar espacios y maqaf
            expanded.append(char)
            continue
            
        base_char = FINAL_TO_BASE.get(char, char)
        
        if base_char == 'ג' and orthography == 'defective':
            expanded.append('גמל')
            continue
            
        expanded.append(MILUY_EXPANSIONS.get(base_char, {}).get(system, base_char))
        
    return " ".join(expanded).replace("   ", "  ") # Preservar separaciones

def expand_multiple_levels(text: str, system: MiluySystem, levels: int = 5, orthography: str = 'plene') -> List[str]:
    results = [text]
    current = text
    for _ in range(levels):
        current = expand_word(current.replace(" ", ""), system, orthography)
        results.append(current)
    return results

def analyze_miluy_levels(text: str, system: MiluySystem, levels: int = 5, orthography: str = 'plene') -> List[Dict]:
    expansions = expand_multiple_levels(text, system, levels, orthography)
    
    analysis = []
    for level, expansion in enumerate(expansions):
        clean_expansion = expansion.replace(" ", "")
        analysis.append({
            "level": level,
            "text": expansion,
            "letter_count": len(clean_expansion),
            "gematria": calculate_mispar_gadol(clean_expansion)
        })
    return analysis
