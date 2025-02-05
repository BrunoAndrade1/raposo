import streamlit as st
import folium
from folium.plugins import HeatMap
import pandas as pd
from streamlit_folium import folium_static

# Carregar os dados
@st.cache_data
def load_data():
    file_path = "C:/Users/Bruno\Desktop/vs code/chatbot/katia/raposo_nao_fatal.xlsx"
    df = pd.read_excel(file_path, sheet_name="Planilha1")
    df["Data do Sinistro"] = pd.to_datetime(df["Data do Sinistro"], errors="coerce")
    return df

df = load_data()

# Filtrar os dados para o período de 2021 a 2023
df_filtrado = df[(df["Data do Sinistro"].dt.year >= 2021) & (df["Data do Sinistro"].dt.year <= 2023)]

# Criar mapa de calor para motocicletas
df_moto = df_filtrado[(df_filtrado["Motocicleta envolvida"] > 0) & df_filtrado["latitude"].notna() & df_filtrado["longitude"].notna()]

# Criar app no Streamlit
st.set_page_config(page_title="Dashboard de Acidentes", layout="wide")
st.title("Dashboard de Acidentes")

st.header("Mapa de Calor de Acidentes Envolvendo Motocicletas (2021-2023)")

# Criar mapa interativo para motocicletas
mapa_calor_motos = folium.Map(location=[df_moto["latitude"].mean(), df_moto["longitude"].mean()], zoom_start=12)
heat_data_moto = list(zip(df_moto["latitude"], df_moto["longitude"], df_moto["Motocicleta envolvida"]))
HeatMap(heat_data_moto, radius=15, blur=20, min_opacity=0.5, max_zoom=15).add_to(mapa_calor_motos)

# Exibir o mapa no Streamlit
folium_static(mapa_calor_motos)

st.write("Este mapa interativo mostra a distribuição de acidentes envolvendo motocicletas no período de 2021 a 2023.")

st.header("Mapa de Calor de Acidentes Gerais (2021-2023)")

# Criar mapa de calor para todos os acidentes
df_mapa = df_filtrado.dropna(subset=["latitude", "longitude"])
mapa_calor = folium.Map(location=[df_mapa["latitude"].mean(), df_mapa["longitude"].mean()], zoom_start=12)
heat_data = list(zip(df_mapa["latitude"], df_mapa["longitude"], df_mapa["Data do Sinistro"].dt.year))
HeatMap(heat_data, radius=10, blur=15).add_to(mapa_calor)

# Exibir o mapa geral no Streamlit
folium_static(mapa_calor)

st.write("Este mapa interativo mostra a distribuição geral de acidentes no período de 2021 a 2023.")

# Espaço para incluir outros gráficos ou tabelas
st.header("Outros Gráficos e Tabelas")
st.write("Adicione aqui outros gráficos ou análises que desejar.")
