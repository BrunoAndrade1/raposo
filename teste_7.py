import streamlit as st
import folium
from folium.plugins import HeatMap
import pandas as pd
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import numpy as np

# Configurar a página com tema mais moderno
st.set_page_config(
    page_title="Dashboard de Sinistros",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilo CSS personalizado
st.markdown("""
    <style>
        .main > div {
            padding: 2rem;
        }
        .stTitle {
            font-size: 2.5rem;
            padding-bottom: 2rem;
            text-align: center;
            color: #1E3D59;
        }
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #f0f2f6;
        }
        .stSubheader {
            color: #1E3D59;
            font-size: 1.5rem;
            padding: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Título da página com container
with st.container():
    st.title("Dashboard de Sinistros")
    st.markdown("*Análise de Sinistros de Trânsito 2021-2023*")

# Carregar os dados
@st.cache_data
def load_data():
    file_path = "raposo_nao_fatal.xlsx"
    df = pd.read_excel(file_path, sheet_name="Planilha1")
    df["Data do Sinistro"] = pd.to_datetime(df["Data do Sinistro"], errors="coerce")
    df["Hora do Sinistro"] = pd.to_datetime(df["Hora do Sinistro"], format='%H:%M:%S', errors="coerce").dt.hour
    return df

# Carregar e preparar os dados
df = load_data()
df_filtrado = df[(df["Data do Sinistro"].dt.year >= 2021) & (df["Data do Sinistro"].dt.year <= 2023)]

# Definir tipos de veículos
veiculos = [
    "Automóvel envolvido",
    "Motocicleta envolvida",
    "Bicicleta envolvida",
    "Caminhão envolvido",
    "Ônibus  envolvido",
    "Outros veículos envolvidos",
    "Veículo envolvido não disponível"
]

# Preparar dados para gráficos de veículos
relacao_logradouro_veiculos = df_filtrado.groupby("Logradouro")[veiculos].sum()
relacao_logradouro_veiculos["Total de Veículos"] = relacao_logradouro_veiculos.sum(axis=1)
relacao_logradouro_veiculos_sorted = relacao_logradouro_veiculos.sort_values(
    by="Total de Veículos", ascending=False
).head(10)

# Criar abas para os diferentes tipos de visualização
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Mapas de Calor", 
    "Análise Temporal", 
    "Análise por Horário", 
    "Análise por Local",
    "Análise de Veículos"
])

# ========================
# Tab 1: Mapas de Calor
# ========================
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sinistros com Motocicletas (2021-2023)")
        df_moto = df_filtrado[
            (df_filtrado["Motocicleta envolvida"] > 0) & 
            df_filtrado["latitude"].notna() & 
            df_filtrado["longitude"].notna()
        ]
        mapa_calor_motos = folium.Map(
            location=[df_moto["latitude"].mean(), df_moto["longitude"].mean()],
            zoom_start=12
        )
        heat_data_moto = list(zip(
            df_moto["latitude"],
            df_moto["longitude"],
            df_moto["Motocicleta envolvida"]
        ))
        HeatMap(
            heat_data_moto,
            radius=15,
            blur=20,
            min_opacity=0.5,
            max_zoom=15
        ).add_to(mapa_calor_motos)
        folium_static(mapa_calor_motos, width=400)

    with col2:
        st.subheader("Todos os Sinistros (2021-2023)")
        df_mapa = df_filtrado.dropna(subset=["latitude", "longitude"])
        mapa_calor = folium.Map(
            location=[df_mapa["latitude"].mean(), df_mapa["longitude"].mean()],
            zoom_start=12
        )
        heat_data = list(zip(
            df_mapa["latitude"],
            df_mapa["longitude"],
            df_mapa["Data do Sinistro"].dt.year
        ))
        HeatMap(heat_data, radius=10, blur=15).add_to(mapa_calor)
        folium_static(mapa_calor, width=400)

# ========================
# Tab 2: Análise Temporal
# ========================
with tab2:
    # Gráfico de Sinistros por Ano
    st.subheader("Quantidade de Sinistros por Ano (2021-2023)")
    sinistros_por_ano_filtrado = df_filtrado["Data do Sinistro"].dt.year.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(sinistros_por_ano_filtrado.index, sinistros_por_ano_filtrado.values, color="#1E88E5")
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
    ax.set_xlabel("Ano")
    ax.set_ylabel("Quantidade de Sinistros")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)

    st.markdown("---")

    # Gráfico de Sinistros por Mês
    st.subheader("Quantidade de Sinistros por Mês (2021-2023)")
    df_filtrado["Ano/Mês"] = df_filtrado["Data do Sinistro"].dt.to_period("M")
    sinistros_por_mes_filtrado = df_filtrado["Ano/Mês"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(
        sinistros_por_mes_filtrado.index.astype(str), 
        sinistros_por_mes_filtrado.values,
        color="#1E88E5"
    )
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom', fontsize=8)
    ax.set_xlabel("Ano/Mês")
    ax.set_ylabel("Quantidade de Sinistros")
    plt.xticks(rotation=90)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de Sinistros por KM
        if "Numero/KM" in df_filtrado.columns:
            st.subheader("KM com Mais Sinistros (2021-2023)")
            sinistros_por_km_filtrado = df_filtrado["Numero/KM"].value_counts().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(
                sinistros_por_km_filtrado.index.astype(str),
                sinistros_por_km_filtrado.values,
                color="#1E88E5"
            )
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
            ax.set_xlabel("KM")
            ax.set_ylabel("Quantidade")
            plt.xticks(rotation=45)
            st.pyplot(fig)

    with col2:
        # Gráfico de Sinistros por Mês (Agrupado)
        st.subheader("Total de Sinistros por Mês (2021-2023)")
        df_filtrado["Mês"] = df_filtrado["Data do Sinistro"].dt.month
        sinistros_por_mes_agrupado = df_filtrado["Mês"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(
            sinistros_por_mes_agrupado.index,
            sinistros_por_mes_agrupado.values,
            color="#1E88E5",
            tick_label=[
                "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                "Jul", "Ago", "Set", "Out", "Nov", "Dez"
            ]
        )
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
        ax.set_xlabel("Mês")
        ax.set_ylabel("Quantidade")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# ============================
# Tab 3: Análise por Horário
# ============================
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de sinistros por hora
        st.subheader("Horários com Mais Sinistros (2021-2023)")
        sinistros_por_hora_filtrado = df_filtrado["Hora do Sinistro"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(sinistros_por_hora_filtrado.index, sinistros_por_hora_filtrado.values, color="#1E88E5")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
        ax.set_xlabel("Hora do Dia")
        ax.set_ylabel("Quantidade")
        ax.set_xticks(range(0, 24))
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)

    with col2:
        # Gráfico de período do dia (Diurno vs Noturno)
        st.subheader("Sinistros por Período (2021-2023)")
        df_filtrado["Período do Dia"] = df_filtrado["Hora do Sinistro"].apply(
            lambda x: "Noturno" if x < 6 or x >= 18 else "Diurno"
        )
        sinistros_por_periodo = df_filtrado["Período do Dia"].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(sinistros_por_periodo.index, sinistros_por_periodo.values, color=["gold", "darkblue"])
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
        ax.set_xlabel("Período do Dia")
        ax.set_ylabel("Quantidade")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)

    st.markdown("---")

    # Comparação entre Automóveis e Motocicletas
    st.subheader("Comparação: Automóveis vs. Motocicletas por Horário (2021-2023)")
    df_veiculos_horario = df_filtrado.groupby("Hora do Sinistro")[["Automóvel envolvido", "Motocicleta envolvida"]].sum()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_veiculos_horario.index, df_veiculos_horario["Automóvel envolvido"], 
            marker="o", linestyle="-", label="Automóveis", color="blue")
    ax.plot(df_veiculos_horario.index, df_veiculos_horario["Motocicleta envolvida"], 
            marker="o", linestyle="-", label="Motocicletas", color="red")
    
    for i in df_veiculos_horario.index:
        ax.text(i, df_veiculos_horario["Automóvel envolvido"][i], 
                str(int(df_veiculos_horario["Automóvel envolvido"][i])), 
                ha='center', va='bottom', fontsize=8, color="blue")
        ax.text(i, df_veiculos_horario["Motocicleta envolvida"][i], 
                str(int(df_veiculos_horario["Motocicleta envolvida"][i])), 
                ha='center', va='bottom', fontsize=8, color="red")
    
    ax.set_xlabel("Hora do Dia")
    ax.set_ylabel("Quantidade")
    ax.set_xticks(range(0, 24))
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend()
    st.pyplot(fig)

# ========================
# Tab 4: Análise por Local
# ========================
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de logradouros com mais sinistros
        st.subheader("Logradouros com Mais Sinistros (2021-2023)")
        logradouro_com_mais_sinistros = df_filtrado["Logradouro"].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(logradouro_com_mais_sinistros.index, logradouro_com_mais_sinistros.values, color="#1E88E5")
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, int(width), va='center')
        ax.set_xlabel("Quantidade")
        ax.set_ylabel("Logradouro")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        st.pyplot(fig)

    with col2:
        # Gráfico de dias úteis vs fins de semana
        st.subheader("Dias Úteis vs Fins de Semana (2021-2023)")
        df_filtrado["Dia da Semana"] = df_filtrado["Data do Sinistro"].dt.day_name()
        df_filtrado["É Fim de Semana"] = df_filtrado["Dia da Semana"].isin(["Saturday", "Sunday"])
        fim_semana_vs_uteis = df_filtrado["É Fim de Semana"].value_counts().rename(
            index={True: "Fim de Semana", False: "Dias Úteis"}
        )
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(fim_semana_vs_uteis.index, fim_semana_vs_uteis.values, color=["orange", "blue"])
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
        ax.set_xlabel("Categoria")
        ax.set_ylabel("Quantidade")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)

    st.markdown("---")

    # Relação entre Logradouros e Veículos
    st.subheader("Relação entre Logradouros e Veículos Envolvidos (2021-2023)")
    fig, ax = plt.subplots(figsize=(12, 6))
    relacao_logradouro_veiculos_sorted[veiculos].plot(
        kind="bar", stacked=True, ax=ax, colormap="viridis"
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", label_type="center", fontsize=8, color="white")
    plt.xlabel("Logradouro")
    plt.ylabel("Quantidade de Veículos Envolvidos")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend(title="Tipos de Veículos", bbox_to_anchor=(1.05, 1))
    plt.tight_layout()
    st.pyplot(fig)

# ============================
# Tab 5: Análise de Veículos
# ============================
with tab5:
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza para o logradouro com mais veículos
        st.subheader("Proporção de Veículos no Logradouro mais Crítico (2021-2023)")
        cores_personalizadas = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
        logradouro_top = relacao_logradouro_veiculos_sorted.index[0]
        dados_top_logradouro = relacao_logradouro_veiculos_sorted.loc[logradouro_top, veiculos]
        
        fig, ax = plt.subplots(figsize=(10, 10))
        plt.pie(
            dados_top_logradouro,
            labels=veiculos,
            autopct="%1.1f%%",
            colors=cores_personalizadas,
            startangle=90,
            wedgeprops={"edgecolor": "black"}
        )
        plt.title(f"Proporção de Veículos no {logradouro_top}")
        plt.axis("equal")
        st.pyplot(fig)
    
    with col2:
        # Gráfico de comparação de veículos por tipo
        st.subheader("Comparação de Veículos por Tipo (2021-2023)")
        total_por_tipo = df_filtrado[veiculos].sum().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.barh(range(len(total_por_tipo)), total_por_tipo.values, color=cores_personalizadas)
        ax.set_yticks(range(len(total_por_tipo)))
        ax.set_yticklabels(total_por_tipo.index)
        
        for i, v in enumerate(total_por_tipo.values):
            ax.text(v, i, f' {int(v)}', va='center')
        
        plt.xlabel("Quantidade")
        plt.ylabel("Tipo de Veículo")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        st.pyplot(fig)
