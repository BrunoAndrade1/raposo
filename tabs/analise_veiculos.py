import streamlit as st
import matplotlib.pyplot as plt

def criar_grafico_veiculos(df, veiculos):
    """Função para criar gráfico de veículos que pode ser reutilizada"""
    total_por_tipo = df[veiculos].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(total_por_tipo)), total_por_tipo.values, color="#1E88E5")
    ax.set_yticks(range(len(total_por_tipo)))
    ax.set_yticklabels(total_por_tipo.index)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, int(width), 
               ha='left', va='center')
    
    plt.xlabel("Quantidade")
    plt.ylabel("Tipo de Veículo")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    return fig

def tab_analise_veiculos(df_filtrado, veiculos, relacao_logradouro_veiculos_sorted):
    df_analysis = df_filtrado.copy()
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
        fig = criar_grafico_veiculos(df_analysis, veiculos)
        st.pyplot(fig)