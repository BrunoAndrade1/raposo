import streamlit as st
import folium
from folium.plugins import HeatMap
import pandas as pd
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# Configurar a página com tema mais moderno
st.set_page_config(
    page_title="Dashboard de Acidentes",
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
    st.title("Dashboard de Acidentes")
    st.markdown("*Análise de Acidentes de Trânsito 2021-2023*")

# Carregar os dados
@st.cache_data
def load_data():
    file_path = "C:/Users/Bruno/Desktop/vs code/chatbot/katia/raposo_nao_fatal.xlsx"
    df = pd.read_excel(file_path, sheet_name="Planilha1")
    df["Data do Sinistro"] = pd.to_datetime(df["Data do Sinistro"], errors="coerce")
    return df

df = load_data()

# Filtrar os dados
df_filtrado = df[(df["Data do Sinistro"].dt.year >= 2021) & (df["Data do Sinistro"].dt.year <= 2023)]

# Criar abas para os diferentes tipos de visualização
tab1, tab2 = st.tabs(["Mapas de Calor", "Análise Temporal"])

with tab1:
    # Organizar mapas em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Acidentes com Motocicletas")
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
        st.subheader("Todos os Acidentes")
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

with tab2:
    # Criar layout com colunas para os gráficos
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de Sinistros por KM
        if "Numero/KM" in df_filtrado.columns:
            st.subheader("KM com Mais Acidentes")
            sinistros_por_km_filtrado = df_filtrado["Numero/KM"].value_counts().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(
                sinistros_por_km_filtrado.index.astype(str),
                sinistros_por_km_filtrado.values,
                color="#1E88E5"
            )
            for bar in bars:
                yval = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2,
                    yval,
                    int(yval),
                    ha='center',
                    va='bottom'
                )
            ax.set_xlabel("KM")
            ax.set_ylabel("Quantidade")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Gráfico de Sinistros por Ano
        st.subheader("Sinistros por Ano")
        sinistros_por_ano_filtrado = df_filtrado["Data do Sinistro"].dt.year.value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(
            sinistros_por_ano_filtrado.index,
            sinistros_por_ano_filtrado.values,
            color="#1E88E5"
        )
        for bar in bars:
            yval = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                yval,
                int(yval),
                ha='center',
                va='bottom'
            )
        ax.set_xlabel("Ano")
        ax.set_ylabel("Quantidade")
        st.pyplot(fig)

    with col2:
        # Gráfico de Sinistros por Mês (Agrupado)
        st.subheader("Total de Sinistros por Mês")
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
            ax.text(
                bar.get_x() + bar.get_width()/2,
                yval,
                int(yval),
                ha='center',
                va='bottom'
            )
        ax.set_xlabel("Mês")
        ax.set_ylabel("Quantidade")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Gráfico de Sinistros por Mês (Detalhado)
        st.subheader("Sinistros por Mês (Detalhado)")
        df_filtrado["Ano/Mês"] = df_filtrado["Data do Sinistro"].dt.to_period("M")
        sinistros_por_mes_filtrado = df_filtrado["Ano/Mês"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(
            sinistros_por_mes_filtrado.index.astype(str),
            sinistros_por_mes_filtrado.values,
            color="#1E88E5"
        )
        for bar in bars:
            yval = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                yval,
                int(yval),
                ha='center',
                va='bottom',
                fontsize=8
            )
        ax.set_xlabel("Ano/Mês")
        ax.set_ylabel("Quantidade")
        plt.xticks(rotation=90)
        st.pyplot(fig)

# Adicionar métricas importantes no rodapé
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    total_acidentes = len(df_filtrado)
    st.metric("Total de Acidentes", f"{total_acidentes:,}")

with col2:
    total_motos = df_filtrado["Motocicleta envolvida"].sum()
    st.metric("Acidentes com Motos", f"{int(total_motos):,}")

with col3:
    media_por_mes = total_acidentes / (len(df_filtrado["Ano/Mês"].unique()))
    st.metric("Média Mensal", f"{media_por_mes:.1f}")