import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def criar_grafico_local(df):
    """Função para criar gráfico de locais que pode ser reutilizada"""
    logradouro_com_mais_sinistros = df["Logradouro"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(logradouro_com_mais_sinistros.index, logradouro_com_mais_sinistros.values, color="#1E88E5")
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, int(width), va='center')
    
    ax.set_xlabel("Quantidade")
    ax.set_ylabel("Logradouro")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    return fig

def tab_analise_local(df_filtrado, veiculos, relacao_logradouro_veiculos_sorted):
    # Criar uma cópia do DataFrame no início da função
    df_analysis = df_filtrado.copy()
    
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de logradouros com mais sinistros
        st.subheader("Logradouros com Mais Sinistros (2021-2023)")
        fig = criar_grafico_local(df_analysis)  # Usando a função criar_grafico_local
        st.pyplot(fig)

    with col2:
        # Gráfico de dias úteis vs fins de semana
        st.subheader("Dias Úteis vs Fins de Semana (2021-2023)")
        df_analysis.loc[:, "Dia da Semana"] = df_analysis["Data do Sinistro"].dt.day_name()
        df_analysis.loc[:, "É Fim de Semana"] = df_analysis["Dia da Semana"].isin(["Saturday", "Sunday"])
        fim_semana_vs_uteis = df_analysis["É Fim de Semana"].value_counts().rename(
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