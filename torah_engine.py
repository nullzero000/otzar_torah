import re
from typing import Literal
from collections import defaultdict, Counter

HEBREW_NIKKUD_START = 0x0591
HEBREW_NIKKUD_END   = 0x05C7
HEBREW_MAQAF        = 0x05BE
SPACE_CHAR          = 0x0020
SHIN_DOT            = 0x05C1
SIN_DOT             = 0x05C2
HEBREW_GERSHAYIM    = 0x05F4

SOFIT_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_SOFIT = {v: k for k, v in SOFIT_TO_REGULAR.items()}

class TorahEngine:
    def __init__(self, raw_corpus: dict):
        self._build_tables()
        self._verse_data = {}      
        self._inverted_index = defaultdict(set) 
        self.raw_corpus = raw_corpus
        self.build_index(raw_corpus)

    def _build_tables(self):
        purge_map = {cp: None for cp in range(HEBREW_NIKKUD_START, HEBREW_NIKKUD_END + 1)}
        purge_map[HEBREW_GERSHAYIM] = None
        
        # Tabla base de limpieza (Normalización Sofit + Limpieza Nikkud)
        self.FREQ_TABLE = str.maketrans({**purge_map, SHIN_DOT: None, SIN_DOT: None, **{ord(s): r for s, r in SOFIT_TO_REGULAR.items()}})
        
        # Tabla de búsqueda (Normalización + Maqaf como espacio)
        search_map = purge_map.copy()
        search_map[HEBREW_MAQAF] = SPACE_CHAR
        for s, r in SOFIT_TO_REGULAR.items(): search_map[ord(s)] = r
        self.SEARCH_TABLE = str.maketrans(search_map)

    def get_frequency_distribution(self, text: str, exclude_spaces: bool, exclude_maqaf: bool) -> dict:
        # Aplicar limpieza base
        clean_text = text.translate(self.FREQ_TABLE)
        
        # Filtrado dinámico
        if exclude_spaces:
            clean_text = clean_text.replace(" ", "")
        if exclude_maqaf:
            clean_text = clean_text.replace("־", "")
            
        return dict(Counter(clean_text).most_common())

    def build_index(self, corpus: dict):
        for book, chapters in corpus.items():
            for chap_num, verses in chapters.items():
                for verse_num, raw_verse in verses.items():
                    ref = f"{book} {chap_num}:{verse_num}"
                    vector = raw_verse.translate(self.SEARCH_TABLE).split()
                    self._verse_data[ref] = {"raw": raw_verse, "vector": vector}
                    for word in vector:
                        self._inverted_index[word].add(ref)

    def search(self, query: str, exact: bool = False) -> dict:
        # Simplificado para brevedad
        return {"query": query, "total_verses": 0, "results": []} # Implementar lógica completa aquí
