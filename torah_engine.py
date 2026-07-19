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
    def __init__(
        self, 
        raw_corpus: dict, 
        reading_tradition: Literal["pragmatic_search", "masoretic_unity"] = "pragmatic_search",
        consonantal_purity: Literal["distinguish_shin_sin", "full_consonantal"] = "distinguish_shin_sin"
    ):
        self.tradition = reading_tradition
        self.purity = consonantal_purity
        self.GEMATRIA_MAP = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
            'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100, 'ר': 200,
            'ש': 300, 'ת': 400
        }
        self._build_tables()
        self._verse_data = {}      
        self._inverted_index = defaultdict(set) 
        self.raw_corpus = raw_corpus
        self.build_index(raw_corpus)

    def _build_tables(self):
        excluded = {HEBREW_MAQAF}
        if self.purity == "distinguish_shin_sin":
            excluded |= {SHIN_DOT, SIN_DOT}

        purge_map = {
            cp: None 
            for cp in range(HEBREW_NIKKUD_START, HEBREW_NIKKUD_END + 1)
            if cp not in excluded
        }
        purge_map[HEBREW_GERSHAYIM] = None

        no_space_map = purge_map.copy()
        no_space_map[SPACE_CHAR] = None
        no_space_map[HEBREW_MAQAF] = None
        no_space_map[SHIN_DOT] = None 
        no_space_map[SIN_DOT] = None
        self.NO_SPACE_TABLE = str.maketrans(no_space_map)

        freq_map = purge_map.copy()
        freq_map[SHIN_DOT] = None
        freq_map[SIN_DOT] = None
        for sofit, regular in SOFIT_TO_REGULAR.items():
            freq_map[ord(sofit)] = regular
        self.FREQ_TABLE = str.maketrans(freq_map)

        search_map = purge_map.copy()
        if self.tradition == "pragmatic_search":
            search_map[HEBREW_MAQAF] = SPACE_CHAR 
        else:
            search_map[HEBREW_MAQAF] = None       

        for sofit, regular in SOFIT_TO_REGULAR.items():
            search_map[ord(sofit)] = regular
            
        self.SEARCH_TABLE = str.maketrans(search_map)

    def get_frequency_distribution(self, text: str, exclude_spaces: bool = False, exclude_maqaf: bool = False) -> dict:
        clean_text = text.translate(self.FREQ_TABLE)
        if exclude_spaces:
            clean_text = clean_text.replace(chr(SPACE_CHAR), "")
        if exclude_maqaf:
            clean_text = clean_text.replace(chr(HEBREW_MAQAF), "")
        return dict(Counter(clean_text).most_common())

    def get_gematria_metrics(self, text: str) -> dict:
        # Se remueve ruido de fondo para el cómputo matemático
        clean_text = text.translate(self.FREQ_TABLE).replace(chr(SPACE_CHAR), "").replace(chr(HEBREW_MAQAF), "")
        
        # O(N): Extracción de Gematria Absoluta
        total_gematria = sum(self.GEMATRIA_MAP.get(c, 0) for c in clean_text)
        
        # O(N): Mispar Katan (eliminación de magnitud, se extrae el primer dígito del valor numérico)
        katan_sum = sum(int(str(self.GEMATRIA_MAP.get(c, 0))[0]) for c in clean_text if c in self.GEMATRIA_MAP)
        
        return {
            "gematria_absoluta": total_gematria,
            "mispar_katan": katan_sum
        }

    def normalize_for_search(self, text: str) -> str:
        return text.translate(self.SEARCH_TABLE)

    def build_index(self, corpus: dict):
        for book, chapters in corpus.items():
            for chap_num, verses in chapters.items():
                for verse_num, raw_verse in verses.items():
                    ref = f"{book} {chap_num}:{verse_num}"
                    vector = self.normalize_for_search(raw_verse).split()
                    self._verse_data[ref] = {"raw": raw_verse, "vector": vector}
                    for word in vector:
                        self._inverted_index[word].add(ref)

    def _generate_spans(self, normalized_words: list[str], raw_verse: str) -> list[tuple[int, int]]:
        ignore_pattern = r'[\u0591-\u05C0\u05C3-\u05C7\u05BE\u05F4]*'
        spans = []
        if self.tradition == "pragmatic_search":
            boundary_assertion = r'(?=[\s\u05BE]|$)' 
        else:
            boundary_assertion = r'(?=[\s]|$)'       

        for q_word in normalized_words:
            regex_chars = []
            for char in q_word:
                if char in REGULAR_TO_SOFIT:
                    regex_chars.append(f"[{char}{REGULAR_TO_SOFIT[char]}]")
                else:
                    regex_chars.append(char)
            regex_str = ignore_pattern.join(regex_chars) + boundary_assertion
            for match in re.finditer(regex_str, raw_verse):
                spans.append(match.span())
        return spans

    def search(self, query: str, exact: bool = False) -> dict:
        q_vector = self.normalize_for_search(query).split()
        if not q_vector:
            return {"query": query, "total_verses": 0, "results": []}

        matched_refs = set()
        if exact:
            for i, q_word in enumerate(q_vector):
                refs_for_word = self._inverted_index.get(q_word, set())
                if i == 0:
                    matched_refs = refs_for_word.copy()
                else:
                    matched_refs.intersection_update(refs_for_word)
                if not matched_refs: 
                    break
        else:
            for i, q_word in enumerate(q_vector):
                refs_for_word = set()
                for vocab_word, refs in self._inverted_index.items():
                    if vocab_word.endswith(q_word):
                        refs_for_word.update(refs)
                if i == 0:
                    matched_refs = refs_for_word
                else:
                    matched_refs.intersection_update(refs_for_word)
                if not matched_refs: 
                    break

        results = []
        for ref in matched_refs:
            raw = self._verse_data[ref]["raw"]
            spans = self._generate_spans(q_vector, raw)
            results.append({"reference": ref, "raw_verse": raw, "spans": spans})

        return {"query": query, "total_verses": len(results), "results": results}
