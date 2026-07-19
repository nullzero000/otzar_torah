import json
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath('.'))

from src.logic.verse_diff import find_letter_discrepant_verses

def main():
    checkpoint_path = Path("output/pipeline_checkpoint.json")
    if not checkpoint_path.exists():
        print("ERROR: No se encontró output/pipeline_checkpoint.json")
        return
        
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
        
    sources = {}
    for src in ["sefaria_mam", "sefaria_taamei", "mechon_mamre"]:
        if src in state:
            if isinstance(state[src], dict):
                sources[src] = state[src]
            else:
                print(f"ERROR DE TIPO: {src} es un {type(state[src]).__name__}, se requiere un dict[str, str] indexado por versículo.")
        else:
            print(f"ADVERTENCIA: {src} no está presente en el checkpoint.")

    if len(sources) < 3:
        print("\nABORTO: Se requieren las 3 fuentes en formato de diccionario para aislar discrepancias.")
        return

    for letter, name in [('צ', 'Tzadik'), ('ר', 'Resh')]:
        print(f"\n{'='*75}\nVERSÍCULOS DISCREPANTES PARA {name} ({letter})\n{'='*75}")
        results = find_letter_discrepant_verses(sources, letter, top_n=10)
        
        if not results:
            print(f"  > Ninguna discrepancia encontrada. Las 3 fuentes coinciden perfectamente en el conteo de {name} a nivel versículo.")
        else:
            for res in results:
                print(f"\n{res['reference']} | Conteos: {res['counts']}")
                for src, text in res['texts'].items():
                    print(f"  [{src:<15}]: {text}")

if __name__ == "__main__":
    main()
