import streamlit as st
import pandas as pd

# 1. Design der Webseite einstellen
st.set_page_config(page_title="Adressregister Biel", page_icon="🇨🇭", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel('Biel_Adressregister_Final.xlsx', sheet_name='Adress-Verzeichnis')
    df = df.fillna("")
    return df

# NEU: Der Übersetzer für normale Menschen
def mach_schoen(text):
    if not text: return ""
    # Wenn ein Schrägstrich drin ist, machen wir eine saubere Liste draus
    teile = str(text).split(' / ')
    if len(teile) == 1:
        return teile[0]
    else:
        return "\n".join([f"- {teil.strip()}" for teil in teile])

st.title("🏛️ Immobilien-Suchmaschine: Stadt Biel")
st.markdown("Tippe eine Strasse oder Hausnummer ein, um die Eigentumsverhältnisse und Flächen auf einen Blick zu sehen.")

try:
    df = load_data()
    
    search_query = st.text_input("🔍 Suche (z.B. 'Südstrasse', 'Schlössli' oder '48'):", "")
    
    if search_query:
        mask = df['Adresse'].str.contains(search_query, case=False, na=False)
        results = df[mask]
        
        if len(results) == 0:
            st.warning("Keine Adresse gefunden. Versuch es mit einem anderen Begriff.")
        else:
            st.success(f"**{len(results)} Treffer gefunden:**")
            
            for index, row in results.iterrows():
                with st.expander(f"📍 {row['Adresse']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Eigentumsverhältnis**")
                        st.markdown(mach_schoen(row['Eigentumsverhältnis']))
                    with col2:
                        st.markdown("**Grundstücksnummer**")
                        st.markdown(mach_schoen(row['Grundstücksnummer(n)']))
                    with col3:
                        st.markdown("**Fläche**")
                        st.markdown(mach_schoen(row['Fläche(n)']))
                        
    else:
        st.info("👈 Bitte gib oben eine Adresse ein, um die Suche zu starten.")
        
except Exception as e:
    st.error(f"Ein Fehler ist aufgetreten: {e}")
