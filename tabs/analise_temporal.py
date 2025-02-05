import streamlit as st
import matplotlib.pyplot as plt

def criar_grafico_temporal(df):
    """Função para criar gráfico temporal que pode ser reutilizada"""
    sinistros_por_ano = df["Data do Sinistro"].dt.year.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(sinistros_por_ano.index, sinistros_por_ano.values, color="#1E88E5")
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), 
               ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel("Ano", fontsize=10)
    ax.set_ylabel("Quantidade de Sinistros", fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    return fig

def get_stats(df):
    """Função para obter estatísticas que podem ser reutilizadas"""
    return {
        'total_sinistros': len(df),
        'media_mensal': len(df) / df["Data do Sinistro"].dt.month.nunique(),
        'mes_mais_critico': df["Data do Sinistro"].dt.month.mode().iloc[0],
        'ano_mais_critico': df["Data do Sinistro"].dt.year.mode().iloc[0]
    }

def tab_analise_temporal(df_filtrado):
    """Função principal para a aba de análise temporal"""
    # Criar duas colunas para os gráficos principais
    col1, col2 = st.columns([0.48, 0.48], gap="large")
    
    with col1:
        # Gráfico de Sinistros por Ano
        st.subheader("Quantidade de Sinistros por Ano (2021-2023)")
        sinistros_por_ano_filtrado = df_filtrado["Data do Sinistro"].dt.year.value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(5, 3))  # Mantendo o tamanho reduzido para o layout
        bars = ax.bar(sinistros_por_ano_filtrado.index, sinistros_por_ano_filtrado.values, color="royalblue")

        # Adicionar rótulos acima das barras
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

        ax.set_xlabel("Ano", fontsize=8)
        ax.set_ylabel("Quantidade de Sinistros", fontsize=8)
        ax.set_xticks(sinistros_por_ano_filtrado.index)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        
        # Renderizar no Streamlit
        st.pyplot(fig, use_container_width=True)

    with col2:
        # Gráfico de Sinistros por Mês
        st.subheader("Quantidade de Sinistros por Mês (2021-2023)")
        df_analysis = df_filtrado.copy()
        df_analysis["Ano/Mês"] = df_analysis["Data do Sinistro"].dt.to_period("M")
        sinistros_por_mes_filtrado = df_analysis["Ano/Mês"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(5, 3))
        bars = ax.bar(
            sinistros_por_mes_filtrado.index.astype(str), 
            sinistros_por_mes_filtrado.values,
            color="#1E88E5"
        )
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), 
                   ha='center', va='bottom', fontsize=7)
        ax.set_xlabel("Ano/Mês", fontsize=8)
        ax.set_ylabel("Quantidade de Sinistros", fontsize=8)
        plt.xticks(rotation=90, fontsize=7)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    st.markdown("---")
    
    # Usar colunas mais estreitas
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Gráfico de Sinistros por KM
        if "Numero/KM" in df_filtrado.columns:
            st.subheader("KM com Mais Sinistros (2021-2023)")
            sinistros_por_km_filtrado = df_filtrado["Numero/KM"].value_counts().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(5, 3))
            bars = ax.bar(
                sinistros_por_km_filtrado.index.astype(str),
                sinistros_por_km_filtrado.values,
                color="#1E88E5"
            )
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), 
                       ha='center', va='bottom', fontsize=7)
            ax.set_xlabel("KM", fontsize=8)
            ax.set_ylabel("Quantidade", fontsize=8)
            plt.xticks(rotation=45, fontsize=7)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

    with col2:
        # Gráfico de Sinistros por Mês (Agrupado)
        st.subheader("Total de Sinistros por Mês (2021-2023)")
        df_analysis = df_filtrado.copy()
        df_analysis["Mês"] = df_analysis["Data do Sinistro"].dt.month
        sinistros_por_mes_agrupado = df_analysis["Mês"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(5, 3))
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
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), 
                   ha='center', va='bottom', fontsize=7)
        ax.set_xlabel("Mês", fontsize=8)
        ax.set_ylabel("Quantidade", fontsize=8)
        plt.xticks(rotation=45, fontsize=7)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)