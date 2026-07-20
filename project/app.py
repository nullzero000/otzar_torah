import streamlit as st
import pandas as pd
import json
from pathlib import Path
from st_click_detector import click_detector

from src.logic.verse_diff import find_letter_discrepant_verses
from src.logic.review_state import load_review_state, save_review_decision
from src.logic.letter_frequency import count_letter_frequency
from src.logic.text_normalization import clean_corpus
from src.logic.comparison import build_frequency_matrix
from src.logic.miluy import analyze_miluy_levels
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

if "search_query_state" not in st.session_state:
    st.session_state.search_query_state = ""

tab_calc, tab_audit = st.tabs(["Calculadora y Explorador", "Auditoría de Discrepancias"])

with tab_calc:
    st.header("Explorador de Texto e Inspector Interactivo")
    if "sefaria_mam" in state:
        source_data = state["sefaria_mam"]
        
        ctrl_col1, ctrl_col2 = st.columns(2)
        kq_mode_calc = ctrl_col1.radio("Filtro K/Q", ["ketiv", "qere"], key="kq_calc", horizontal=True)
        count_spaces_maqaf = ctrl_col2.checkbox("Incluir Espacios y Maqaf (־) en conteos")
        
        st.divider()
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
                selected_verse = col3.selectbox("Versículo", ["Todos"] + verses_sorted)
                if selected_verse == "Todos":
                    target_keys = [k for k in source_data.keys() if k.startswith(f"{selected_book}:{selected_chapter}:")]
                else:
                    target_keys = [f"{selected_book}:{selected_chapter}:{selected_verse}"]
            
        raw_text_concat = " ".join(source_data[k] for k in target_keys if k in source_data)
        clean_text_concat = clean_corpus(raw_text_concat, kq_mode=kq_mode_calc, keep_maqaf=count_spaces_maqaf)
        
        # ====================================================
        # INICIO DEL TEXTO INTERACTIVO
        # ====================================================
        st.subheader("Hebreo Interactivo (Haz clic en cualquier palabra)")
        words = clean_text_concat.split()
        
        # Construir HTML interactivo
        html_css = """
        <style>
        .heb-word { 
            text-decoration: none; color: var(--text-color); padding: 4px 8px; margin: 2px;
            border-radius: 4px; transition: all 0.2s; display: inline-block; cursor: pointer;
        }
        .heb-word:hover { background-color: var(--primary-color); color: white; transform: scale(1.05); }
        </style>
        """
        html_content = f"{html_css}<div style='direction: rtl; text-align: right; font-size: 28px; line-height: 2; font-family: serif; padding: 15px; border: 1px solid rgba(128,128,128,0.2); border-radius: 8px; background: var(--secondary-background-color); max-height: 300px; overflow-y: auto;'>"
        for i, w in enumerate(words):
            html_content += f"<a href='#' id='w_{i}' class='heb-word'>{w}</a> "
        html_content += "</div>"
        
        clicked_id = click_detector(html_content, key="click_detector")
        
        if clicked_id:
            word_idx = int(clicked_id.split('_')[1])
            selected_word = words[word_idx]
            
            st.markdown(f"### 🔍 Inspección: <span style='color: var(--primary-color);'>{selected_word}</span>", unsafe_allow_html=True)
            w_gadol = calculate_mispar_gadol(selected_word)
            w_siduri = calculate_mispar_siduri(selected_word)
            w_katan = reduce_to_single_digit(w_gadol)
            
            w_col1, w_col2, w_col3 = st.columns(3)
            w_col1.metric("Gadol (Raíz)", w_gadol)
            w_col2.metric("Siduri (Ordinal)", w_siduri)
            w_col3.metric("Katan (1 Dígito)", w_katan)
            
            st.markdown("#### Expansión Miluy Automática")
            miluy_sys = st.selectbox("Sistema para esta palabra", ["AB", "SAG", "MAH", "BAN"], key="miluy_word_sys")
            miluy_data = analyze_miluy_levels(selected_word, miluy_sys, levels=5)
            
            df_miluy = pd.DataFrame(miluy_data)
            st.dataframe(
                df_miluy[["level", "word_count", "letter_count", "gematria", "gematria_katan", "text"]],
                use_container_width=True,
                column_config={
                    "level": "Nivel",
                    "word_count": "Palabras",
                    "letter_count": "Letras",
                    "gematria": "Gadol",
                    "gematria_katan": "Katan",
                    "text": st.column_config.TextColumn("Texto Expandido")
                }
            )
            
            if st.button("Enviar al Buscador Global"):
                st.session_state.search_query_state = selected_word
                st.rerun()
            st.divider()

        # ====================================================
        # MÉTRICAS GLOBALES DEL TEXTO
        # ====================================================
        st.subheader("Métricas Globales de la Selección")
        m_gadol = calculate_mispar_gadol(clean_text_concat)
        m_siduri = calculate_mispar_siduri(clean_text_concat)
        m_katan = reduce_to_single_digit(m_gadol)
        freq = count_letter_frequency(clean_text_concat, count_spaces_maqaf=count_spaces_maqaf)
        word_count = len(words)
        
        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; background-color: var(--secondary-background-color); padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid rgba(128,128,128,0.2);'>
            <div><p style='color: var(--text-color); opacity: 0.7; font-size: 14px; margin: 0;'>Mispar Gadol</p><h2 style='margin: 0; color: var(--primary-color);'>{m_gadol:,}</h2></div>
            <div><p style='color: var(--text-color); opacity: 0.7; font-size: 14px; margin: 0;'>Mispar Siduri</p><h2 style='margin: 0; color: var(--primary-color);'>{m_siduri:,}</h2></div>
            <div><p style='color: var(--text-color); opacity: 0.7; font-size: 14px; margin: 0;'>Un Dígito (Katan)</p><h2 style='margin: 0; color: var(--primary-color);'>{m_katan}</h2></div>
            <div><p style='color: var(--text-color); opacity: 0.7; font-size: 14px; margin: 0;'>Palabras</p><h2 style='margin: 0; color: var(--primary-color);'>{word_count:,}</h2></div>
            <div><p style='color: var(--text-color); opacity: 0.7; font-size: 14px; margin: 0;'>Caracteres</p><h2 style='margin: 0; color: var(--primary-color);'>{sum(freq.values()):,}</h2></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Ver Frecuencias de Letras"):
            df_freq = pd.DataFrame.from_dict(freq, orient='index', columns=['Frecuencia'])
            df_freq.index.name = 'Letra/Carácter'
            df_freq = df_freq[df_freq['Frecuencia'] > 0].sort_values(by='Frecuencia', ascending=False)
            st.dataframe(df_freq, use_container_width=True)
        
        
        # ====================================================
        # MOTOR MILUY GLOBAL (TODO EL TEXTO)
        # ====================================================
        st.divider()
        st.subheader("Motor de Expansión Miluy Global (5 Niveles)")
        miluy_sys_global = st.selectbox("Sistema Luriánico para la selección completa", ["AB", "SAG", "MAH", "BAN"], key="miluy_global_sys")
        
        if st.button(f"Ejecutar Expansión Global en {miluy_sys_global}"):
            if len(clean_text_concat.replace(" ", "")) > 5000:
                st.warning("Texto masivo (>5000 caracteres). El crecimiento exponencial en Nivel 5 colapsará el navegador. Limítalo a un capítulo a la vez.")
            else:
                miluy_data_global = analyze_miluy_levels(clean_text_concat, miluy_sys_global, levels=5)
                
                df_export = pd.DataFrame([{k: v for k, v in d.items() if k != 'frequencies'} for d in miluy_data_global])
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(label="Descargar CSV con Textos Expandidos", data=csv, file_name=f"miluy_global_{miluy_sys_global}.csv", mime="text/csv")
                
                for lvl in miluy_data_global:
                    with st.expander(f"Nivel {lvl['level']} | Palabras: {lvl['word_count']} | Letras: {lvl['letter_count']} | Gadol: {lvl['gematria']} | Katan: {lvl['gematria_katan']}"):
                        d_col1, d_col2 = st.columns([1, 2])
                        with d_col1:
                            df_lvl_freq = pd.DataFrame.from_dict(lvl['frequencies'], orient='index', columns=['Frecuencia'])
                            df_lvl_freq = df_lvl_freq[df_lvl_freq['Frecuencia'] > 0].sort_values(by='Frecuencia', ascending=False)
                            st.dataframe(df_lvl_freq, use_container_width=True)
                        with d_col2:
                            st.text_area("Texto Oculto", lvl['text'], height=150, disabled=True, key=f"txt_global_{lvl['level']}")
        
        # --- Buscador ---
        st.divider()
        st.subheader("Buscador de Palabras")
        search_query = st.text_input("Ingresa la palabra o frase a buscar (Hebreo):", key="search_query_state")
        if search_query:
            search_results = search_in_corpus(source_data, search_query, kq_mode=kq_mode_calc, keep_maqaf=count_spaces_maqaf)
            if search_results:
                st.success(f"Encontrado en {len(search_results)} versículos. Ocurrencias totales: {sum(r['count'] for r in search_results)}")
                st.dataframe(pd.DataFrame(search_results))
            else:
                st.warning("No se encontraron coincidencias.")
    else:
        st.warning("Fuente Sefaria MAM no encontrada en el checkpoint.")

with tab_audit:
    st.sidebar.title("Filtros de Auditoría")
    selected_letter = st.sidebar.selectbox("Letra a auditar", ["Todas"] + BASE_LETTERS)
    top_n = st.sidebar.slider("Versículos a mostrar", 10, 100, 50)
    frequencies = {"canon_zonana": CANON_ZONANA, "tanach_text_only": TANACH_TEXT_ONLY}
    for label in ["sefaria_mam", "sefaria_taamei", "mechon_mamre"]:
        if label in state:
            text = " ".join(state[label].values())
            frequencies[label] = count_letter_frequency(clean_corpus(text, kq_mode="ketiv"))
    st.subheader("Conteo Absoluto de Fuentes (Global)")
    st.dataframe(build_frequency_matrix(frequencies))
    
    sources_for_diff = {k: state[k] for k in ["sefaria_mam", "sefaria_taamei", "mechon_mamre"] if k in state}
    discrepancies = find_letter_discrepant_verses(sources_for_diff, selected_letter, kq_mode="ketiv", top_n=top_n) if selected_letter != "Todas" else []
    
    for item in discrepancies:
        ref = item["verse_ref"]
        status = review_state.get(ref, {}).get("status", "pending")
        with st.expander(f"{ref} (Spread: {item['spread']}) - {status.upper()}"):
            cols = st.columns(len(item["raw_texts"]))
            for i, (src, text) in enumerate(item["raw_texts"].items()):
                cols[i].text_area(src, text, height=150, disabled=True)
