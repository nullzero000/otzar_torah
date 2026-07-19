from typing import Dict
from collections import Counter
from src.data.reference_corpora import BASE_LETTERS

def count_letter_frequency(text: str, count_spaces_maqaf: bool = False) -> Dict[str, int]:
    counts = Counter(text)
    keys_to_count = list(BASE_LETTERS)
    
    if count_spaces_maqaf:
        keys_to_count.extend([' ', '\u05BE'])

    return {
        char: counts.get(char, 0)
        for char in keys_to_count
    }
