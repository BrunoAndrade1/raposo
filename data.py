import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    file_path = "raposo_nao_fatal.xlsx"    
    df = pd.read_excel(file_path, sheet_name="Planilha1")
    df.head(3)
    df["Data do Sinistro"] = pd.to_datetime(df["Data do Sinistro"], errors="coerce")
    df["Hora do Sinistro"] = pd.to_datetime(df["Hora do Sinistro"], format='%H:%M:%S', errors="coerce").dt.hour
    return df

# Constantes
VEICULOS = [
    "Automóvel envolvido",
    "Motocicleta envolvida",
    "Bicicleta envolvida",
    "Caminhão envolvido",
    "Ônibus  envolvido",
    "Outros veículos envolvidos",
    "Veículo envolvido não disponível"
]

def preparar_dados_veiculos(df_filtrado):
    # Preparar dados para gráficos de veículos
    relacao_logradouro_veiculos = df_filtrado.groupby("Logradouro")[VEICULOS].sum()
    relacao_logradouro_veiculos["Total de Veículos"] = relacao_logradouro_veiculos.sum(axis=1)
    return relacao_logradouro_veiculos.sort_values(by="Total de Veículos", ascending=False).head(10)