# Hiscox Digital Atlas 2.0

A business-classification and appetite-matching tool for small commercial underwriting.

## 🔍 What It Does

- Match business descriptions to official Hiscox Classes of Business (COBs)
- View appetite by product line (PL, GL, BOP, Cyber)
- Upload partner files to generate clean mappings
- Optional NAICS-based matching for broader interpretation
- Incorporates trusted partner match data as evidence

## 🚀 How to Run

### Option 1: Local

1. Clone or download this repo
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Launch the app:
   ```
   streamlit run DigitalAtlas2_0.py
   ```

### Option 2: [Streamlit Cloud](https://share.streamlit.io/)

- Create a free Streamlit account
- Connect to this GitHub repo
- Set `DigitalAtlas2_0.py` as the main file

## 📁 Files

| File | Purpose |
|------|---------|
| `DigitalAtlas2_0.py` | Streamlit interface |
| `AtlasEngine1030.csv` | Hiscox NAICS-to-COB map |
| `PartnerOverrides.csv` | Evidence of mapped partner terms |
| `requirements.txt` | Python packages needed to run |

## 💡 Coming Soon

- Partner-specific logic (e.g. Talage sub-descriptions)
- Enhanced batch mode with tuning options
- Admin feedback panel
- Embedded documentation and usage guide

---

Built with ❤️ by Sean Drumm + HUCgpt