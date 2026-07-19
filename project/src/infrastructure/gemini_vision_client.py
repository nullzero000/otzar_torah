import json
from pathlib import Path
from dataclasses import dataclass
from typing import List
from google import genai
from google.genai import types
from src.infrastructure.http_retry import with_backoff

@dataclass
class PageResult:
    page_number: int
    texto_transcrito: str
    caracteres_ilegibles_count: int
    notas_ambiguedad: List[str]
    error: str = ""

@with_backoff()
def transcribe_page(image_path: str | Path, page_number: int) -> PageResult:
    """Transcribes a manuscript page using Gemini Vision, strictly returning JSON."""
    client = genai.Client()
    
    prompt = (
        "Actúa como transcriptor de manuscritos, no como experto en Torá. "
        "Reportá EXACTAMENTE los caracteres hebreos visibles en la imagen, "
        "preservando nikud y te'amim. REGLA ABSOLUTA: no uses tu conocimiento "
        "de ediciones estándar de la Torá para completar texto — si un carácter "
        "es ilegible o ambiguo, marcalo como [ILEGIBLE] o [AMBIGUO: X/Y], nunca "
        "lo reemplaces por la lectura tradicional esperada. Respondé en JSON con "
        "las claves: texto_transcrito (string), caracteres_ilegibles_count (int), "
        "notas_ambiguedad (lista de strings)."
    )
    
    image_file = client.files.upload(file=str(image_path))
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=[prompt, image_file],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )
    
    try:
        data = json.loads(response.text)
        return PageResult(
            page_number=page_number,
            texto_transcrito=data.get("texto_transcrito", ""),
            caracteres_ilegibles_count=data.get("caracteres_ilegibles_count", 0),
            notas_ambiguedad=data.get("notas_ambiguedad", [])
        )
    except json.JSONDecodeError as e:
        return PageResult(page_number, "", 0, [], error=str(e))
