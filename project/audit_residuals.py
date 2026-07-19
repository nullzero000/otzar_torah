import json
import re
import sys
import os
from collections import Counter, defaultdict
sys.path.append(os.path.abspath('.'))
from src.data.reference_corpora import BASE_LETTERS

def residual_character_report(text: str, samples_per_char: int = 3, context_chars: int = 15) -> dict:
    allowed = set(BASE_LETTERS)
    counts = Counter(ch for ch in text if ch not in allowed and not ch.isspace())
    samples: dict[str, list[str]] = defaultdict(list)
    
    for match in re.finditer(r".", text):
        ch = match.group()
        if ch in counts and len(samples[ch]) < samples_per_char:
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            samples[ch].append(text[start:end].replace("\n", " "))
            
    return {"counts": counts.most_common(), "samples": dict(samples)}

def main():
    try:
        with open("output/pipeline_checkpoint.json", "r", encoding="utf-8") as f:
            state = json.load(f)
    except FileNotFoundError:
        print("Falta el checkpoint. Ejecuta main.py primero.")
        return

    for src in ["sefaria_mam", "sefaria_taamei", "mechon_mamre"]:
        if src in state:
            print(f"\n{'='*75}\nREPORTE DE RESIDUALES CRUDOS: {src}\n{'='*75}")
            raw_text = " ".join(state[src].values())
            report = residual_character_report(raw_text)
            
            if not report["counts"]:
                print("  Ningún carácter residual. (Texto 100% compuesto por BASE_LETTERS y espacios).")
                continue
                
            for char, count in report["counts"]:
                print(f"[{repr(char):<5}] Frecuencia: {count}")
                for samp in report["samples"][char]:
                    print(f"    Contexto: {repr(samp)}")

if __name__ == "__main__":
    main()
