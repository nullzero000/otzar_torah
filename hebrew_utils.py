HEBREW_NIKKUD_START = 0x0591
HEBREW_NIKKUD_END   = 0x05C7
HEBREW_MAQAF        = 0x05BE
SPACE_CHAR          = 0x0020
SHIN_DOT            = 0x05C1
SIN_DOT             = 0x05C2
HEBREW_GERSHAYIM    = 0x05F4

SOFIT_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_SOFIT = {v: k for k, v in SOFIT_TO_REGULAR.items()}

GEMATRIA_MAP = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
    'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100, 'ר': 200,
    'ש': 300, 'ת': 400
}
