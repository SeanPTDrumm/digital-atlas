
import pandas as pd
import streamlit as st
import difflib
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

st.set_page_config(page_title="Digital Atlas 2.0", layout="centered")

@st.cache_data
def load_engine():
    return pd.read_csv("AtlasEngineUnified.csv")

@st.cache_data
def load_partner_terms():
    return pd.read_csv("PartnerOverrides.csv")

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

engine_df = load_engine()
partner_df = load_partner_terms()
model = load_model()

def summarize_appetite_logic(row):
    flags = [row["PL"], row["GL"], row["BOP"], row["Cyber"]]
    labels = ["PL", "GL", "BOP", "Cyber"]
    yes_flags = [label for flag, label in zip(flags, labels) if flag.lower() == "yes"]
    if len(yes_flags) >= 2:
        return "In Appetite", "green-btn"
    elif len(yes_flags) == 1:
        return f"{yes_flags[0]} Only", "green-btn"
    else:
        return "Out of Appetite", "red-btn"

def search_top_match(input_text, naics_mode=False):
    input_text = input_text.strip().lower()
    input_vec = model.encode([input_text])

    # Score each row using semantic similarity, keyword, partner, and NAICS match
    def compute_score(row):
        text_parts = [row["Hiscox_COB"], row["NAICS_Description"], row["NAICS_Title"]]
        combined_text = " ".join(str(t).lower() for t in text_parts)
        row_vec = model.encode([combined_text])
        sem_score = cosine_similarity(input_vec, row_vec)[0][0]

        keyword_score = difflib.SequenceMatcher(None, input_text, str(row["Hiscox_COB"]).lower()).ratio()

        naics_score = 0.0
        if not naics_mode:
            naics_score = difflib.SequenceMatcher(None, input_text, str(row["NAICS_Description"]).lower()).ratio()

        partner_boost = 0.0
        for pt in partner_df["Partner_Description"].dropna().str.lower():
            if pt in input_text:
                partner_boost = 0.15
                break

        if naics_mode:
            total = 0.2 * keyword_score + 0.3 * sem_score + 0.5 * naics_score
        else:
            total = 0.25 * keyword_score + 0.3 * sem_score + 0.2 * naics_score + partner_boost

        return total

    engine_df["match_score"] = engine_df.apply(compute_score, axis=1)
    top_row = engine_df.sort_values("match_score", ascending=False).iloc[0]
    appetite_label, appetite_class = summarize_appetite_logic(top_row)

    return {
        "Input": input_text,
        "Hiscox_COB": top_row["Hiscox_COB"],
        "full_industry_code": top_row["full_industry_code"],
        "Appetite": appetite_label,
        "AppetiteClass": appetite_class,
        "LOB_Details": {
            "PL": top_row["PL"],
            "GL": top_row["GL"],
            "BOP": top_row["BOP"],
            "Cyber": top_row["Cyber"]
        }
    }

# UI
st.title("📊 Hiscox Digital Atlas 2.0")

tab1, tab2 = st.tabs(["🔍 Search", "📁 Batch Upload"])

with tab1:
    use_naics = st.checkbox("Use NAICS-based Matching Only")
    search_input = st.text_input("Search for a business description or 6-digit NAICS code")
    if search_input:
        result = search_top_match(search_input, naics_mode=use_naics)
        st.markdown(f"### 🔎 Match: **{result['Hiscox_COB']}**")
        st.markdown(f"**Industry Code:** `{result['full_industry_code']}`")
        st.markdown(f"""
            <div class="appetite-button {result['AppetiteClass']}">
                {result['Appetite']}
            </div>
        """, unsafe_allow_html=True)
        st.markdown("**Availability:**")
        st.write(result["LOB_Details"])

with tab2:
    use_naics_batch = st.checkbox("Use NAICS-based Matching Only (Batch)")
    uploaded_file = st.file_uploader("Upload spreadsheet with business descriptions", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df_in = pd.read_csv(uploaded_file)
        else:
            df_in = pd.read_excel(uploaded_file)

        col_candidates = [col for col in df_in.columns if df_in[col].dtype == "object"]
        selected_col = st.selectbox("Select input column", col_candidates)

        if st.button("Run Matching"):
            results = []
            for desc in df_in[selected_col].dropna():
                r = search_top_match(desc, naics_mode=use_naics_batch)
                row = {
                    "Input_Description": desc,
                    "Hiscox_COB": r["Hiscox_COB"],
                    "full_industry_code": r["full_industry_code"],
                    "PL": r["LOB_Details"]["PL"],
                    "GL": r["LOB_Details"]["GL"],
                    "BOP": r["LOB_Details"]["BOP"],
                    "Cyber": r["LOB_Details"]["Cyber"]
                }

                if all(val.lower() == "no" for val in row.values()[-4:]):
                    row.update({k: "" for k in row.keys()})  # blank if OOA
                    row["Input_Description"] = desc

                results.append(row)

            df_out = pd.DataFrame(results)
            st.dataframe(df_out)
            st.download_button("Download Results", df_out.to_csv(index=False), file_name="AtlasBatchResults.csv", mime="text/csv")
