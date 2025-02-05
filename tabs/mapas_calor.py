import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

def tab_mapas_calor(df_filtrado):
    # Ajustar o layout para melhor distribuição
    st.markdown("""
        <style>
            .stColumns {
                gap: 2rem;
            }
            .map-container {
                margin: 1rem 0;
            }
            .map-title {
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 1rem;
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

    # Criar layout com duas colunas de tamanho igual
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<p class="map-title">Sinistros com Motocicletas (2021-2023)</p>', unsafe_allow_html=True)
        
        # Filtrar dados e criar mapa de motos
        df_moto = df_filtrado[
            (df_filtrado["Motocicleta envolvida"] > 0) & 
            df_filtrado["latitude"].notna() & 
            df_filtrado["longitude"].notna()
        ].copy()
        
        df_moto["latitude"] = df_moto["latitude"].astype(str).str.replace(",", ".").astype(float)
        df_moto["longitude"] = df_moto["longitude"].astype(str).str.replace(",", ".").astype(float)
        df_moto["count"] = df_moto.groupby(["latitude", "longitude"])["latitude"].transform("count")
        
        mapa_calor_motos = folium.Map(
            location=[df_moto["latitude"].mean(), df_moto["longitude"].mean()],
            zoom_start=12,
            width=650,
            height=500
        )
        
        heat_data_moto = list(zip(df_moto["latitude"], df_moto["longitude"], df_moto["count"]))
        HeatMap(
            heat_data_moto,
            radius=15,
            blur=20,
            min_opacity=0.5,
            max_zoom=15
        ).add_to(mapa_calor_motos)
        
        for _, row in df_moto.drop_duplicates(subset=["latitude", "longitude"]).iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                icon=folium.DivIcon(html=f'<b style="font-size: 10pt; color: red;">{int(row["count"])}</b>')
            ).add_to(mapa_calor_motos)
        
        folium_static(mapa_calor_motos, width=650, height=500)

    with col2:
        st.markdown('<p class="map-title">Todos os Sinistros (2021-2023)</p>', unsafe_allow_html=True)
        
        df_mapa = df_filtrado.dropna(subset=["latitude", "longitude"]).copy()
        df_mapa["latitude"] = df_mapa["latitude"].astype(str).str.replace(",", ".").astype(float)
        df_mapa["longitude"] = df_mapa["longitude"].astype(str).str.replace(",", ".").astype(float)
        df_mapa["count"] = df_mapa.groupby(["latitude", "longitude"])["latitude"].transform("count")
        
        mapa_calor = folium.Map(
            location=[df_mapa["latitude"].mean(), df_mapa["longitude"].mean()],
            zoom_start=12,
            width=650,
            height=500
        )
        
        heat_data = list(zip(df_mapa["latitude"], df_mapa["longitude"], df_mapa["count"]))
        HeatMap(heat_data, radius=10, blur=15).add_to(mapa_calor)
        
        for _, row in df_mapa.drop_duplicates(subset=["latitude", "longitude"]).iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                icon=folium.DivIcon(html=f'<b style="font-size: 10pt; color: black;">{int(row["count"])}</b>')
            ).add_to(mapa_calor)
        
        folium_static(mapa_calor, width=650, height=500)