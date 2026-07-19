import json
import glob
import argparse

CANON = {
    'א': 27057, 'ב': 16344, 'ג': 2109, 'ד': 7032, 'ה': 28052,
    'ו': 30509, 'ז': 2198, 'ח': 7187, 'ט': 1802, 'י': 31522,
    'כ': 11960, 'ל': 21570, 'מ': 25078, 'נ': 14107, 'ס': 1833,
    'ע': 11244, 'פ': 4805, 'צ': 4052, 'ק': 4694, 'ר': 18109,
    'ש': 15592, 'ת': 17949
}

CANON_TOTAL = sum(CANON.values())
HEBREW_ORDER = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת']

def compare_versions():
    files = glob.glob("counts_*.json")
    if not files:
        print("No se encontraron archivos counts_*.json en el directorio.")
        return

    results = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            dist = data.get("distribution", {})
            total = data.get("total", 0)
            delta_total = total - CANON_TOTAL
            
            letter_deltas = {}
            for letter in HEBREW_ORDER:
                letter_deltas[letter] = dist.get(letter, 0) - CANON[letter]
                
            results.append({
                "version": data["version"],
                "total": total,
                "delta_total": delta_total,
                "abs_delta": abs(delta_total),
                "letter_deltas": letter_deltas
            })

    results.sort(key=lambda x: x["abs_delta"])

    print(f"{'VERSIÓN':<45} | {'TOTAL':<8} | {'DELTA GLOBAL'}")
    print("-" * 75)
    for r in results:
        sign = "+" if r['delta_total'] > 0 else ""
        print(f"{r['version']:<45} | {r['total']:<8} | {sign}{r['delta_total']}")
    
    print("\n" + "="*75 + "\nDETALLE LETRA POR LETRA (Ordenado por Delta Absoluto)\n" + "="*75)
    
    for r in results:
        print(f"\nVersión: {r['version']}")
        print(f"Total: {r['total']} (Delta: {r['delta_total']})")
        print("-" * 50)
        
        deltas_str = []
        for letter in HEBREW_ORDER:
            d = r['letter_deltas'][letter]
            if d != 0:
                sign = "+" if d > 0 else ""
                deltas_str.append(f"{letter}: {sign}{d}")
                
        if not deltas_str:
            print("  ¡Sin desviaciones! Coincidencia exacta con el Canon.")
        else:
            for i in range(0, len(deltas_str), 5):
                print("  " + ", ".join(deltas_str[i:i+5]))

if __name__ == "__main__":
    compare_versions()
