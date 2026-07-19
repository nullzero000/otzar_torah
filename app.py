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

st.sidebar.header("Control de Filtros")
ex_space = st.sidebar.checkbox("Excluir Espacios del conteo", value=False)
ex_maqaf = st.sidebar.checkbox("Excluir Maqaf del conteo", value=False)

# Selectores (Lógica previa mantenida)
books = list(corpus.keys())
selected_book = st.sidebar.selectbox("Libro", ["Todos"] + books)
# ... [Lógica de selección de capítulos/versículos igual que antes] ...
# (Para brevedad, asume que aquí extraes text_blocks)

# Cálculo de frecuencias con parámetros
freq_dist = engine.get_frequency_distribution(full_text, exclude_spaces=ex_space, exclude_maqaf=ex_maqaf)

# Visualización
df = pd.DataFrame(list(freq_dist.items()), columns=["Caracter", "Apariciones"])
st.dataframe(df)
