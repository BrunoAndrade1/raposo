# main.py
import streamlit as st
import folium
from folium.plugins import HeatMap
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import folium_static

# Importa as configurações definidas no config.py
from config import (
    MAP_ZOOM,
    MOTOCYCLIST_HEATMAP_CONFIG,
    GENERAL_HEATMAP_CONFIG,
    FIGURE_SIZE_BAR_CHART,
    BAR_COLOR,
)

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard de Acidentes", layout="wide")
st.title("Dashboard de Acidentes")

# Função para carregar os dados
@st.cache_data
def load_data():
    file_path = "C:/Users/Bruno/Desktop/vs code/chatbot/katia/raposo_nao_fatal.xlsx"
    df = pd.read_excel(file_path, sheet_name="Planilha1")
    df["Data do Sinistro"] = pd.to_datetime(df["Data do Sinistro"], errors="coerce")
    return df

df = load_data()

# Filtrar os dados para o período de 2021 a 2023
df_filtrado = df[(df["Data do Sinistro"].dt.year >= 2021) & (df["Data do Sinistro"].dt.year <= 2023)]

# === Mapa de Calor de Acidentes Envolvendo Motocicletas ===
st.header("Mapa de Calor de Acidentes Envolvendo Motocicletas (2021-2023)")
df_moto = df_filtrado[
    (df_filtrado["Motocicleta envolvida"] > 0) &
    df_filtrado["latitude"].notna() &
    df_filtrado["longitude"].notna()
]
if not df_moto.empty:
    mapa_calor_motos = folium.Map(
        location=[df_moto["latitude"].mean(), df_moto["longitude"].mean()],
        zoom_start=MAP_ZOOM
    )
    heat_data_moto = list(zip(
        df_moto["latitude"],
        df_moto["longitude"],
        df_moto["Motocicleta envolvida"]
    ))
    HeatMap(heat_data_moto, **MOTOCYCLIST_HEATMAP_CONFIG).add_to(mapa_calor_motos)
    folium_static(mapa_calor_motos)
    st.write("Este mapa interativo mostra a distribuição de acidentes envolvendo motocicletas no período de 2021 a 2023.")
else:
    st.warning("Não há dados disponíveis para acidentes envolvendo motocicletas.")

# === Mapa de Calor de Acidentes Gerais ===
st.header("Mapa de Calor de Acidentes Gerais (2021-2023)")
df_mapa = df_filtrado.dropna(subset=["latitude", "longitude"])
if not df_mapa.empty:
    mapa_calor = folium.Map(
        location=[df_mapa["latitude"].mean(), df_mapa["longitude"].mean()],
        zoom_start=MAP_ZOOM
    )
    # Aqui usamos o ano do sinistro como peso, mas você pode ajustar conforme necessário
    heat_data = list(zip(
        df_mapa["latitude"],
        df_mapa["longitude"],
        df_mapa["Data do Sinistro"].dt.year
    ))
    HeatMap(heat_data, **GENERAL_HEATMAP_CONFIG).add_to(mapa_calor)
    folium_static(mapa_calor)
    st.write("Este mapa interativo mostra a distribuição geral de acidentes no período de 2021 a 2023.")
else:
    st.warning("Não há dados suficientes para gerar o mapa de calor geral.")

# === Gráfico de Sinistros por KM ===
if "Numero/KM" in df_filtrado.columns:
    sinistros_por_km = df_filtrado["Numero/KM"].value_counts().sort_values(ascending=False).head(10)
    st.header("KM com Mais Acidentes (2021-2023)")
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_BAR_CHART)
    bars = ax.bar(sinistros_por_km.index.astype(str), sinistros_por_km.values, color=BAR_COLOR)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
    ax.set_xlabel("KM")
    ax.set_ylabel("Quantidade de Sinistros")
    ax.set_title("KM com Mais Acidentes (2021-2023)")
    st.pyplot(fig)

# === Gráfico de Sinistros por Ano ===
st.header("Quantidade de Sinistros por Ano (2021-2023)")
sinistros_por_ano = df_filtrado["Data do Sinistro"].dt.year.value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(sinistros_por_ano.index, sinistros_por_ano.values, color=BAR_COLOR)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
ax.set_xlabel("Ano")
ax.set_ylabel("Quantidade de Sinistros")
ax.set_title("Quantidade de Sinistros por Ano (2021-2023)")
st.pyplot(fig)

# === Gráfico de Sinistros por Mês (Ano/Mês) ===
st.header("Quantidade de Sinistros por Mês (2021-2023)")
df_filtrado["Ano/Mês"] = df_filtrado["Data do Sinistro"].dt.to_period("M")
sinistros_por_mes = df_filtrado["Ano/Mês"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(sinistros_por_mes.index.astype(str), sinistros_por_mes.values, color=BAR_COLOR)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom', fontsize=8)
ax.set_xlabel("Ano/Mês")
ax.set_ylabel("Quantidade de Sinistros")
ax.set_title("Quantidade de Sinistros por Mês (2021-2023)")
ax.tick_params(axis='x', rotation=90)
st.pyplot(fig)

# === Gráfico de Sinistros por Mês (Agrupado) ===
st.header("Total de Sinistros por Mês (2021-2023)")
df_filtrado["Mês"] = df_filtrado["Data do Sinistro"].dt.month
sinistros_por_mes_agrupado = df_filtrado["Mês"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10, 5))
tick_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
bars = ax.bar(sinistros_por_mes_agrupado.index, sinistros_por_mes_agrupado.values, tick_label=tick_labels)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
ax.set_xlabel("Mês")
ax.set_ylabel("Quantidade de Sinistros")
ax.set_title("Total de Sinistros por Mês (2021-2023)")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)
