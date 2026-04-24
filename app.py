import streamlit as st
import pandas as pd

# 1. Design der Webseite einstellen
st.set_page_config(page_title="Adressregister Biel", page_icon="🇨🇭", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel('Biel_Adressregister_Final.xlsx', sheet_name='Adress-Verzeichnis')
    df = df.fillna("")
    return df

# --- NEU: Der Text-Generator (Macht aus Daten verständliche Sätze) ---
def generiere_besitz_text(besitz_string):
    if not besitz_string:
        return "Die genauen Eigentumsverhältnisse sind leider unbekannt."

    # Hilfsfunktion, um die Codes in schöne Namen zu übersetzen
    def name_finden(text):
        if "01" in text: return "der Stadt Biel"
        if "02" in text: return "dem Bund, dem Kanton oder einer anderen öffentlichen Institution"
        if "03" in text: return "einer Privatperson oder einer privaten Firma"
        return "einem unbekannten Eigentümer"

    # Ist es ein Baurecht? (Schrägstrich vorhanden)
    if "/" in besitz_string:
        teile = besitz_string.split(" / ")
        boden_besitzer = name_finden(teile[0])
        haus_besitzer = name_finden(teile[1])
        
        return f"🏢 **Besondere Situation (Baurecht):** Der Grund und Boden dieser Parzelle gehört **{boden_besitzer}**. Das Gebäude darauf gehört rechtlich jedoch **{haus_besitzer}**."
    
    # Kein Baurecht (Normalfall)
    else:
        besitzer = name_finden(besitz_string)
        return f"🏡 **Vollständiges Eigentum:** Sowohl der Boden als auch das Gebäude gehören vollumfänglich **{besitzer}**."

# ----------------------------------------------------------------------

st.title("🏛️ Immobilien-Register der Stadt Biel")

# --- NEU: Tabs für verschiedene Funktionen ---
tab1, tab2 = st.tabs(["🔍 Einfache Adress-Suche", "📊 Stadt-Portfolio (Entdecken)"])

try:
    df = load_data()
    
    # ==========================================
    # TAB 1: DIE SUCHE
    # ==========================================
    with tab1:
        st.markdown("Tippe eine Strasse oder Hausnummer ein, um die Eigentumsverhältnisse sofort im Klartext zu sehen.")
        search_query = st.text_input("Suchen (z.B. 'Südstrasse', 'Schlössli' oder '48'):", "", key="search")
        
        if search_query:
            mask = df['Adresse'].str.contains(search_query, case=False, na=False)
            results = df[mask]
            
            if len(results) == 0:
                st.warning("Keine Adresse gefunden. Versuch es mit einem anderen Begriff.")
            else:
                st.success(f"**{len(results)} Treffer gefunden**")
                
                for index, row in results.iterrows():
                    with st.expander(f"📍 {row['Adresse']}", expanded=True):
                        # Unser neuer, schöner Fliesstext!
                        st.write(generiere_besitz_text(row['Eigentumsverhältnis']))
                        
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption("Grundstücksnummer(n)")
                            st.write(str(row['Grundstücksnummer(n)']).replace(" / ", "\n\n"))
                        with col2:
                            st.caption("Fläche(n)")
                            st.write(str(row['Fläche(n)']).replace(" / ", "\n\n"))
        else:
            st.info("👈 Bitte gib oben eine Adresse ein.")

    # ==========================================
    # TAB 2: DIE SPIELEREIEN (Stadt-Portfolio)
    # ==========================================
    with tab2:
        st.header("Was gehört eigentlich der Stadt?")
        st.markdown("Hier kannst du das Immobilien-Portfolio der Einwohnergemeinde Biel durchstöbern.")
        
        # Wir filtern alle Adressen, bei denen "01" (Stadt) vorkommt
        stadt_mask = df['Eigentumsverhältnis'].str.contains("01", na=False)
        stadt_df = df[stadt_mask].copy()
        
        # Ein paar coole Statistiken für die Nutzer
        st.metric(label="Anzahl gefundener Adressen mit städtischer Beteiligung", value=len(stadt_df))
        
        st.markdown("### Alle städtischen Adressen auf einen Blick:")
        # Eine interaktive Tabelle anzeigen
        st.dataframe(
            stadt_df[['Adresse', 'Eigentumsverhältnis', 'Fläche(n)']], 
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Ein Fehler ist aufgetreten: {e}")
