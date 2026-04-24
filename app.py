import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Immo-Portal Biel", page_icon="🇨🇭", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel('Biel_Adressregister_GPS.xlsx')
    return df.fillna("")

def generiere_besitz_text(besitz_string):
    def name_finden(text):
        if "01" in text: return "der Stadt Biel"
        if "03" in text: return "einer Privatperson"
        return "einer Institution"
    
    if "/" in str(besitz_string):
        teile = str(besitz_string).split(" / ")
        return f"🏢 **Baurecht:** Boden gehört **{name_finden(teile[0])}**, Gebäude gehört **{name_finden(teile[1])}**."
    return f"🏡 **Volleigentum:** Boden und Gebäude gehören **{name_finden(str(besitz_string))}**."

try:
    df = load_data()
    st.title("🏛️ Interaktives Immobilien-Register Biel")
    
    tab1, tab2 = st.tabs(["🔍 Suche & Karte", "📊 Stadt-Portfolio"])

    with tab1:
        search_query = st.text_input("Adresse suchen:", "")
        
        if search_query:
            results = df[df['Adresse'].str.contains(search_query, case=False, na=False)]
            if not results.empty:
                # Karte für das gefundene Gebäude
                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=pdk.ViewState(latitude=results.iloc[0]['lat'], longitude=results.iloc[0]['lon'], zoom=17, pitch=45),
                    layers=[pdk.Layer('ScatterplotLayer', data=results, get_position='[lon, lat]', get_color='[200, 30, 0, 160]', get_radius=10)]
                ))
                for _, row in results.iterrows():
                    with st.expander(f"📍 {row['Adresse']}", expanded=True):
                        st.write(generiere_besitz_text(row['Eigentumsverhältnis']))
        else:
            # Übersichtskarte von ganz Biel
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(latitude=47.1367, longitude=7.2468, zoom=12),
                layers=[pdk.Layer('HexagonLayer', data=df, get_position='[lon, lat]', radius=100, elevation_scale=4, elevation_range=[0, 1000], pickable=True, extinct=True)]
            ))

    with tab2:
        stadt_df = df[df['Eigentumsverhältnis'].str.contains("01", na=False)]
        st.metric("Gebäude im Stadtbesitz", len(stadt_df))
        
        # Karte aller städtischen Gebäude
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v9',
            initial_view_state=pdk.ViewState(latitude=47.1367, longitude=7.2468, zoom=13),
            layers=[pdk.Layer('ScatterplotLayer', data=stadt_df, get_position='[lon, lat]', get_color='[0, 255, 100, 200]', get_radius=20)]
        ))
        st.dataframe(stadt_df[['Adresse', 'Fläche(n)']], use_container_width=True)

except Exception as e:
    st.error(f"Fehler: {e}")
