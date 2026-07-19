import streamlit as st
import pandas as pd
import json
from torah_engine import TorahEngine

# CORRECCIÓN: Nomenclatura del Proyecto
st.set_page_config(page_title="Otzar Torah", layout="wide")

@st.cache_resource
def load_engine():
    with open("corpus.json", "r", encoding="utf-8") as f:
        corpus = json.load(f)
    return TorahEngine(corpus)

engine = load_engine()
corpus = engine.raw_corpus

st.title("Otzar Torah: Analytics")

# --- BARRA LATERAL: SELECTORES EN CASCADA ---
st.sidebar.header("Navegación Estructural")

books = list(corpus.keys())
selected_book = st.sidebar.selectbox("Libro", ["Todos"] + books)

selected_chapter = "Todos"
if selected_book != "Todos":
    chapters = list(corpus[selected_book].keys())
    selected_chapter = st.sidebar.selectbox("Capítulo", ["Todos"] + chapters)

selected_verse = "Todos"
if selected_chapter != "Todos":
    verses = list(corpus[selected_book][selected_chapter].keys())
    selected_verse = st.sidebar.selectbox("Versículo", ["Todos"] + verses)

# --- LÓGICA DE EXTRACCIÓN ---
text_blocks = []
if selected_book == "Todos":
    for b in corpus.values():
        for c in b.values():
            text_blocks.extend(c.values())
elif selected_chapter == "Todos":
    for c in corpus[selected_book].values():
        text_blocks.extend(c.values())
elif selected_verse == "Todos":
    text_blocks.extend(corpus[selected_book][selected_chapter].values())
else:
    text_blocks.append(corpus[selected_book][selected_chapter][selected_verse])

full_text = " ".join(text_blocks)

# --- PESTAÑAS DE VISUALIZACIÓN ---
tab1, tab2 = st.tabs(["Frecuencias y Tablas", "Buscador de Raíces"])

with tab1:
    st.subheader(f"Distribución Matemática: {selected_book} {selected_chapter}:{selected_verse}")
    
    freq_dist = engine.get_frequency_distribution(full_text)
    if " " in freq_dist:
        freq_dist["Espacio"] = freq_dist.pop(" ")
    if "־" in freq_dist:
        freq_dist["Maqaf"] = freq_dist.pop("־")
    
    df = pd.DataFrame(list(freq_dist.items()), columns=["Caracter", "Apariciones"])
    df.index += 1 
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total de Caracteres (Puro)", sum(freq_dist.values()))
    with col2:
        st.dataframe(df, use_container_width=True)
        
    if selected_verse != "Todos":
        st.markdown("### Texto Crudo")
        st.markdown(f"<div dir='rtl' style='font-size:24px;'>{full_text}</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("Motor de Búsqueda Simétrico")
    
    col_search, col_mode = st.columns([2, 1])
    
    with col_search:
        query = st.text_input("Ingresa raíz en hebreo (Ej. אלהים)", "")
    
    with col_mode:
        # CORRECCIÓN: Exposición explícita de la arquitectura de búsqueda
        search_strategy = st.radio(
            "Estrategia de Intersección",
            options=["Búsqueda Relajada (Subcadenas)", "Match Exacto (Palabra Aislada)"],
            help="Relajada: Ignora prefijos gramaticales. Exacta: Exige coincidencia 1:1 con la palabra indexada."
        )
    
    exact_mode = search_strategy == "Match Exacto (Palabra Aislada)"
    
    if query:
        results = engine.search(query, exact_mode)
        st.success(f"Se encontraron {results['total_verses']} versículos.")
        
        for r in results['results']:
            raw_v = r["raw_verse"]
            spans = sorted(r["spans"], key=lambda x: x[0], reverse=True)
            
            highlighted = raw_v
            for start, end in spans:
                highlighted = highlighted[:start] + f"<mark style='background-color: #ffeb3b;'>{highlighted[start:end]}</mark>" + highlighted[end:]
            
            st.markdown(f"**{r['reference']}**")
            st.markdown(f"<div dir='rtl' style='font-size:22px;'>{highlighted}</div>", unsafe_allow_html=True)
            st.divider()
