import streamlit as st

def configurar_pagina():
    # Configurar a página
    st.set_page_config(
        page_title="Dashboard de Sinistros",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Remover padding padrão
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
            .element-container {
                margin-bottom: 1rem;
            }
            .fonte-info {
                background-color: #262730;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                border-left: 4px solid #1E88E5;
            }
            .filtro-info {
                background-color: #262730;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                border-left: 4px solid #28a745;
            }
            .css-10trblm {
                margin-bottom: 0;
                color: white;
            }
            .css-10trblm {
                font-size: 2rem !important;
            }
            .subtitle {
                font-size: 1.1rem;
                color: #9e9e9e;
                font-style: italic;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # Cabeçalho
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Dashboard de Sinistros")
        st.markdown('<p class="subtitle">Análise de Sinistros de Trânsito 2021-2023</p>', unsafe_allow_html=True)
        
        # Informação sobre fonte de dados
        st.info("""
        **📊 Fonte dos Dados:**
        InfoSiga SP - Sistema de Informações Gerenciais de Acidentes de Trânsito do Estado de São Paulo
        """)
        
        # Informação sobre filtros
        st.success("""
        **🔍 Filtros Aplicados:**
        Dados filtrados para ocorrências na Rodovia Raposo Tavares e variações relacionadas:
        • Acesso Rodovia Raposo Tavares
        • Marginal Rodovia Raposo Tavares
        • Raposo Shopping / Jardim Olympia
        • Rodovia Raposo Tavares
        • Rodovia SP 270 Raposo Tavares
        • Retorno Rodovia Raposo Tavares
        • Viaduto Raposo Tavares
        """)

    st.markdown("<br>", unsafe_allow_html=True)