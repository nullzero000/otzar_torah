import streamlit as st
import pandas as pd
import json
from pathlib import Path

from src.logic.verse_diff import find_letter_discrepant_verses
from src.logic.review_state import load_review_state, save_review_decision
from src.logic.letter_frequency import count_letter_frequency
from src.logic.text_normalization import clean_corpus
from src.logic.comparison import build_frequency_matrix
from src.logic.gematria import calculate_mispar_gadol, reduce_to_single_digit, calculate_mispar_siduri
from src.logic.search import search_in_corpus
from src.data.reference_corpora import BASE_LETTERS, CANON_ZONANA, TANACH_TEXT_ONLY

st.set_page_config(layout="wide", page_title="Otzar Torah Analyzer")
checkpoint_path = Path(__file__).parent / "output/pipeline_checkpoint.json"
review_path = Path(__file__).parent / "output/review_state.json"

if not checkpoint_path.exists():
    st.error("Pipeline no ejecutado. Corre `python3 main.py` primero.")
    st.stop()

state = json.loads(checkpoint_path.read_text(encoding="utf-8"))
review_state = load_review_state(review_path)

tab_calc, tab_audit = st.tabs(["Calculadora y Explorador", "Auditoría de Discrepancias"])

# ==========================================
# TAB 1: CALCULADORA ORIGINAL (Gematria, Conteos y Búsqueda)
# ==========================================
with tab_calc:
    st.header("Explorador de Texto y Gematria")
    
    if "sefaria_mam" in state:
        source_data = state["sefaria_mam"]
        
        # --- Controles Adicionales ---
        ctrl_col1, ctrl_col2 = st.columns(2)
        kq_mode_calc = ctrl_col1.radio("Filtro K/Q (Para toda la pestaña)", ["ketiv", "qere"], key="kq_calc", horizontal=True)
        count_spaces_maqaf = ctrl_col2.checkbox("Incluir Espacios y Maqaf (־) en conteos")
        
        st.divider()
        
        # --- Explorador de Jerarquía ---
        st.subheader("Filtro de Corpus")
        col1, col2, col3 = st.columns(3)
        
        books_options = ["Toda la Torá"] + list(dict.fromkeys(k.split(":")[0] for k in source_data.keys()))
        selected_book = col1.selectbox("Libro", books_options)
        
        if selected_book == "Toda la Torá":
            target_keys = list(source_data.keys())
            col2.selectbox("Capítulo", ["Todos"], disabled=True)
            col3.selectbox("Versículo", ["Todos"], disabled=True)
        else:
            chapters = list(dict.fromkeys(k.split(":")[1] for k in source_data.keys() if k.startswith(f"{selected_book}:")))
            selected_chapter = col2.selectbox("Capítulo", ["Todos"] + sorted(chapters, key=int))
            
            if selected_chapter == "Todos":
                target_keys = [k for k in source_data.keys() if k.startswith(f"{selected_book}:")]
                col3.selectbox("Versículo", ["Todos"], disabled=True)
            else:
                verses = list(dict.fromkeys(k.split(":")[2] for k in source_data.keys() if k.startswith(f"{selected_book}:{selected_chapter}:")))
                verses_sorted = sorted(verses, key=int)
                verse_options = ["Todos"] + verses_sorted
                selected_verse = col3.selectbox("Versículo", verse_options)
                
                if selected_verse == "Todos":
                    target_keys = [k for k in source_data.keys() if k.startswith(f"{selected_book}:{selected_chapter}:")]
                else:
                    target_keys = [f"{selected_book}:{selected_chapter}:{selected_verse}"]
            
        raw_text_concat = " ".join(source_data[k] for k in target_keys if k in source_data)
        clean_text_concat = clean_corpus(raw_text_concat, kq_mode=kq_mode_calc, keep_maqaf=count_spaces_maqaf)
        
        # UI de Texto
        st.text_area("Hebreo Limpio (Procesado)", clean_text_concat, height=100, disabled=True)
        
        # UI de Métricas Matemáticas
        st.subheader("Gematria y Conteos")
        m_gadol = calculate_mispar_gadol(clean_text_concat)
        m_siduri = calculate_mispar_siduri(clean_text_concat)
        m_katan = reduce_to_single_digit(m_gadol)
        freq = count_letter_frequency(clean_text_concat, count_spaces_maqaf=count_spaces_maqaf)
        word_count = len(clean_text_concat.split())
        
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        m_col1.metric("Mispar Gadol (Estándar)", f"{m_gadol:,}")
        m_col2.metric("Mispar Siduri (Ordinal)", f"{m_siduri:,}")
        m_col3.metric("Un Dígito (Katan)", m_katan)
        m_col4.metric("Palabras", f"{word_count:,}")
        m_col5.metric("Caracteres", f"{sum(freq.values()):,}")
        
        # Tabla vertical ordenada de mayor a menor
        df_freq = pd.DataFrame.from_dict(freq, orient='index', columns=['Frecuencia'])
        df_freq.index.name = 'Letra/Carácter'
        df_freq = df_freq.sort_values(by='Frecuencia', ascending=False)
        st.dataframe(df_freq, use_container_width=True)
        
        # --- Buscador ---
        st.divider()
        st.subheader("Buscador de Palabras")
        search_query = st.text_input("Ingresa la palabra o frase a buscar (Hebreo):")
        if search_query:
            search_results = search_in_corpus(source_data, search_query, kq_mode=kq_mode_calc, keep_maqaf=count_spaces_maqaf)
            if search_results:
                st.success(f"Encontrado en {len(search_results)} versículos. Ocurrencias totales: {sum(r['count'] for r in search_results)}")
                st.dataframe(pd.DataFrame(search_results))
            else:
                st.warning("No se encontraron coincidencias.")
    else:
        st.warning("Fuente Sefaria MAM no encontrada en el checkpoint.")


# ==========================================
# TAB 2: AUDITORÍA (Diff y Revisión)
# ==========================================
with tab_audit:
    st.sidebar.title("Filtros de Auditoría")
    selected_letter = st.sidebar.selectbox("Letra a auditar", ["Todas"] + BASE_LETTERS)
    top_n = st.sidebar.slider("Versículos a mostrar", 10, 100, 50)

    frequencies = {"canon_zonana": CANON_ZONANA, "tanach_text_only": TANACH_TEXT_ONLY}
    for label in ["sefaria_mam", "sefaria_taamei", "mechon_mamre"]:
        if label in state:
            text = " ".join(state[label].values())
            # La auditoría no incluye espacios/maqaf para que coincida con el canon base.
            frequencies[label] = count_letter_frequency(clean_corpus(text, kq_mode=kq_mode_calc))

    st.subheader("Conteo Absoluto de Fuentes (Global)")
    st.dataframe(build_frequency_matrix(frequencies))
    st.info("Nota: Sefaria y Mechon Mamre se comparan por versículo más abajo. Zonana y WLC no aplican al diff.")

    st.subheader("Análisis de Discrepancia por Versículo")
    sources_for_diff = {k: state[k] for k in ["sefaria_mam", "sefaria_taamei", "mechon_mamre"] if k in state}

    discrepancies = find_letter_discrepant_verses(sources_for_diff, selected_letter, kq_mode=kq_mode_calc, top_n=top_n) if selected_letter != "Todas" else []

    for item in discrepancies:
        ref = item["verse_ref"]
        status = review_state.get(ref, {}).get("status", "pending")
        
        with st.expander(f"{ref} (Spread: {item['spread']}) - {status.upper()}"):
            if item["known_shift_zone"]:
                st.warning("⚠️ Zona de re-versificación conocida (Decálogo)")
                
            cols = st.columns(len(item["raw_texts"]))
            for i, (src, text) in enumerate(item["raw_texts"].items()):
                cols[i].text_area(src, text, height=150, disabled=True)
                
            c1, c2, c3 = st.columns(3)
            if c1.button("Confirmar anomalía", key=f"c_{ref}"):
                save_review_decision(review_path, ref, "confirmed_anomaly")
                st.rerun()
            if c2.button("Artefacto conocido", key=f"a_{ref}"):
                save_review_decision(review_path, ref, "known_artifact")
                st.rerun()
            if c3.button("Dejar pendiente", key=f"p_{ref}"):
                save_review_decision(review_path, ref, "pending")
                st.rerun()

    if st.button("Exportar CSV Auditoría"):
        df_export = pd.DataFrame(discrepancies)
        st.download_button("Descargar CSV", df_export.to_csv(), "reporte_anomalias.csv", "text/csv")
