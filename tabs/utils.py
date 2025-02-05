# tabs/utils.py
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap

def processar_dados_temporais(df):
    """Funções comuns de processamento temporal"""
    return {
        'sinistros_por_ano': df["Data do Sinistro"].dt.year.value_counts().sort_index(),
        'sinistros_por_mes': df["Data do Sinistro"].dt.month.value_counts().sort_index(),
        'media_mensal': len(df)/df['Data do Sinistro'].dt.date.nunique()
    }

def processar_dados_locais(df):
    """Funções comuns de processamento local"""
    return {
        'top_locais': df["Logradouro"].value_counts().head(10),
        'total_por_local': df.groupby("Logradouro").size()
    }

def criar_grafico_temporal(df):
    """Gráfico de evolução temporal"""
    sinistros_por_ano = df["Data do Sinistro"].dt.year.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(sinistros_por_ano.index, sinistros_por_ano.values, color="#1E88E5")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Quantidade")
    for i, v in enumerate(sinistros_por_ano.values):
        ax.text(sinistros_por_ano.index[i], v, str(v), ha='center', va='bottom')
    plt.tight_layout()
    return fig

def criar_grafico_horario(df):
    """Gráfico de distribuição horária"""
    sinistros_por_hora = df["Hora do Sinistro"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sinistros_por_hora.index, sinistros_por_hora.values, marker='o')
    ax.set_xlabel("Hora do Dia")
    ax.set_ylabel("Quantidade")
    ax.set_xticks(range(24))
    plt.tight_layout()
    return fig

def criar_grafico_local(df, top_n=10):
    """Gráfico de locais mais frequentes"""
    top_locais = df["Logradouro"].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_locais.index, top_locais.values, color="#1E88E5")
    ax.set_xlabel("Quantidade")
    ax.set_ylabel("Logradouro")
    plt.tight_layout()
    return fig

def criar_grafico_veiculos(df, veiculos):
    """Gráfico de tipos de veículos"""
    total_por_tipo = df[veiculos].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(total_por_tipo)), total_por_tipo.values, color="#1E88E5")
    ax.set_yticks(range(len(total_por_tipo)))
    ax.set_yticklabels(total_por_tipo.index)
    plt.tight_layout()
    return fig

def criar_mapa_calor(df, tipo='geral'):
    """Criar mapa de calor"""
    if tipo == 'moto':
        df_mapa = df[
            (df["Motocicleta envolvida"] > 0) & 
            df["latitude"].notna() & 
            df["longitude"].notna()
        ]
        valor = df_mapa["Motocicleta envolvida"]
    else:
        df_mapa = df.dropna(subset=["latitude", "longitude"])
        valor = df_mapa["Data do Sinistro"].dt.year

    mapa = folium.Map(
        location=[df_mapa["latitude"].mean(), df_mapa["longitude"].mean()],
        zoom_start=12
    )
    
    heat_data = list(zip(
        df_mapa["latitude"],
        df_mapa["longitude"],
        valor
    ))
    
    HeatMap(
        heat_data,
        radius=15 if tipo == 'moto' else 10,
        blur=20 if tipo == 'moto' else 15,
        min_opacity=0.5 if tipo == 'moto' else None,
        max_zoom=15 if tipo == 'moto' else None
    ).add_to(mapa)
    
    return mapa