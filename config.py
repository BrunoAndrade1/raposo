import streamlit as st

def configurar_pagina():
    # Configurar a página
    st.set_page_config(
        page_title="Dashboard de Sinistros",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown("""
        <style>
            /* Remove o cabeçalho e o rodapé do Streamlit */
            header, footer {
                visibility: hidden;
                height: 0;
            }

            /* Fundo geral da página */
            .stApp {
                background-color: #0e1117;
                color: white;
            }

            /* Ajustando cores de texto e outros elementos */
            .block-container {
                color: white;
            }

            .stButton > button {
                background-color: #1E88E5;
                color: white;
                border-radius: 8px;
            }

            .stSelectbox {
                background-color: #262730;
                color: white;
            }

            /* Links e outros elementos interativos */
            a {
                color: #1E88E5;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }

            /* Ajustando as caixas de mensagens (st.info, st.success) */
            .fonte-info {
                background-color: #262730 !important;
                border-left: 4px solid #1E88E5 !important;
            }
            .filtro-info {
                background-color: #262730 !important;
                border-left: 4px solid #28a745 !important;
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
        📊 Fonte dos Dados:
        InfoSiga SP - Sistema de Informações Gerenciais de Acidentes de Trânsito do Estado de São Paulo
        """)

        # Informação sobre filtros
        st.success("""
        🔍 Filtros Aplicados:
        Dados filtrados para ocorrências na Rodovia Raposo Tavares e variações relacionadas:
        • Acesso Rodovia Raposo Tavares
        • Marginal Rodovia Raposo Tavares
        • Raposo Shopping / Jardim Olympia
        • Rodovia Raposo Tavares
        • Rodovia SP 270 Raposo Tavares
        • Retorno Rodovia Raposo Tavares
        • Viaduto Raposo Tavares
        """)

    # Rodapé com link de contato
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem;">
            <p>Desenvolvido por <strong>Bruno Andrade de Luna</strong></p>
            <a href="https://www.linkedin.com/in/bruno-andrade-de-luna/" target="_blank" style="color: #0A66C2; text-decoration: none;">
                <strong>📧 Entre em contato no LinkedIn</strong>
            </a>
        </div>
        """, unsafe_allow_html=True
    )
