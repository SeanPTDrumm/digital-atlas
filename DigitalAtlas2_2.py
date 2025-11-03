
import streamlit as st
import pandas as pd
import difflib

@st.cache_data
def load_data():
    df = pd.read_csv("AtlasEngineUnified.csv")
    df.columns = df.columns.str.strip()
    return df

def clean_text(text):
    return str(text).strip().lower()

def compute_score(row, search_term):
    try:
        text_parts = [row["Hiscox_COB"], row.get("Input_Term", ""), row.get("Full_Industry_Code", "")]
        combined_text = " ".join(text_parts).lower()
        return difflib.SequenceMatcher(None, search_term.lower(), combined_text).ratio()
    except Exception:
        return 0

def search_top_match(search_term, df):
    df["match_score"] = df.apply(lambda row: compute_score(row, search_term), axis=1)
    best_row = df.loc[df["match_score"].idxmax()]
    return best_row

def summarize_appetite(row):
    yes_flags = [lob for lob in ["PL", "GL", "BOP", "Cyber"] if row.get(lob, "").strip().lower() == "yes"]
    if len(yes_flags) >= 2:
        return "In Appetite"
    elif len(yes_flags) == 1:
        return f"{yes_flags[0]} Only"
    else:
        return "Out of Appetite"

# UI
st.set_page_config(page_title="Digital Atlas 2.2", layout="centered")
st.title("🔎 Digital Atlas 2.2")
st.markdown("Search for a business type or NAICS term below:")

df_engine = load_data()

search_input = st.text_input("Enter description:")
if search_input:
    result = search_top_match(search_input, df_engine)
    st.markdown(f"### 🧭 Matched COB: `{result['Hiscox_COB']}`")
    st.markdown(f"**Full Industry Code**: {result.get('Full_Industry_Code', '')}")
    st.markdown(f"**Appetite Summary**: `{summarize_appetite(result)}`")
    st.markdown("---")
    st.markdown(f"- PL: {result['PL']}  
- GL: {result['GL']}  
- BOP: {result['BOP']}  
- Cyber: {result['Cyber']}")
