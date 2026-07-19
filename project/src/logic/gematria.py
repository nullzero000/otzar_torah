from src.data.reference_corpora import BASE_LETTERS

GEMATRIA_VALUES = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
    'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
}

def calculate_mispar_gadol(text: str) -> int:
    """Suma tradicional de valores (Gematria estándar / Mispar Gadol)."""
    return sum(GEMATRIA_VALUES.get(char, 0) for char in text)

def reduce_to_single_digit(n: int) -> int:
    """Reducción teosófica a un solo dígito (Raíz digital)."""
    if n == 0:
        return 0
    return 9 if n % 9 == 0 else n % 9

def calculate_mispar_katan(text: str) -> int:
    """
    Suma los valores reducidos de cada letra y reduce el resultado final a un dígito.
    """
    total = sum(reduce_to_single_digit(GEMATRIA_VALUES.get(char, 0)) for char in text if char in GEMATRIA_VALUES)
    return reduce_to_single_digit(total)
