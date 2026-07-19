import streamlit as st
import pandas as pd
import json
from torah_engine import TorahEngine

st.set_page_config(page_title="Otzar Torah", layout="wide")

@st.cache_resource
def load_engine():
    with open("corpus.json", "r", encoding="utf-8") as f:
        corpus = json.load(f)
    return TorahEngine(corpus)

engine = load_engine()
corpus = engine.raw_corpus

st.title("Otzar Torah: Analytics")

# --- BARRA LATERAL ---
st.sidebar.header("Control de Filtros")
ex_space = st.sidebar.checkbox("Excluir Espacios", value=False)
ex_maqaf = st.sidebar.checkbox("Excluir Maqaf", value=False)

st.sidebar.divider()

st.sidebar.header("Navegación Estructural")
books = list(corpus.keys())
selected_book = st.sidebar.selectbox("Libro", ["Todos"] + books)

selected_chapter = "Todos"
if selected_book != "Todos":
    chapters = list(corpus[selected_book].keys())
    selected_chapter = st.sidebar.selectbox("Capítulo", ["Todos"] + chapters)

selected_verses = ["Todos"]
if selected_chapter != "Todos":
    verses = list(corpus[selected_book][selected_chapter].keys())
    selected_verses = st.sidebar.multiselect(
        "Versículo(s)", 
        ["Todos"] + verses, 
        default=["Todos"]
    )

# --- LÓGICA DE EXTRACCIÓN ---
text_blocks = []
if selected_book == "Todos":
    for b in corpus.values():
        for c in b.values():
            text_blocks.extend(c.values())
elif selected_chapter == "Todos":
    for c in corpus[selected_book].values():
        text_blocks.extend(c.values())
elif "Todos" in selected_verses or not selected_verses:
    text_blocks.extend(corpus[selected_book][selected_chapter].values())
else:
    for v in selected_verses:
        text_blocks.append(corpus[selected_book][selected_chapter][v])

full_text = " ".join(text_blocks)

# --- PESTAÑAS DE VISUALIZACIÓN ---
tab1, tab2 = st.tabs(["Frecuencias y Tablas", "Buscador de Raíces"])

with tab1:
    v_title = "Todos" if "Todos" in selected_verses else ", ".join(selected_verses)
    st.subheader(f"Distribución Matemática: {selected_book} {selected_chapter}:{v_title}")
    
    freq_dist = engine.get_frequency_distribution(full_text, exclude_spaces=ex_space, exclude_maqaf=ex_maqaf)
    
    if " " in freq_dist:
        freq_dist["Espacio"] = freq_dist.pop(" ")
    if "־" in freq_dist:
        freq_dist["Maqaf"] = freq_dist.pop("־")
    
    df = pd.DataFrame(list(freq_dist.items()), columns=["Caracter", "Apariciones"])
    df.index += 1 
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total de Caracteres", sum(freq_dist.values()))
    with col2:
        st.dataframe(df, use_container_width=True)
        
    if "Todos" not in selected_verses:
        st.markdown("### Texto Crudo")
        st.markdown(f"<div dir='rtl' style='font-size:24px;'>{full_text}</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("Motor de Búsqueda Simétrico")
    
    col_search, col_mode = st.columns([2, 1])
    
    with col_search:
        query = st.text_input("Ingresa raíz en hebreo (Ej. אלהים)", "")
    
    with col_mode:
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
