import streamlit as st

def configurar_pagina():
    # Configurar a página
    st.set_page_config(
        page_title="Dashboard de Sinistros",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
            /* Títulos e textos principais */
            h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
            .stMarkdown p, p, .title, .subtitle {
                color: #333333 !important;
            }
            
            /* Subtítulo específico */
            .subtitle {
                font-style: italic;
                color: #666666 !important;
            }
            
            /* Estilos para texto das categorias */
            .categoria {
                margin-top: 15px;
                margin-bottom: 8px;
                color: #1e88e5 !important;
                font-weight: bold;
                padding: 5px 0;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            /* Estilos para perguntas exemplo */
            .pergunta-exemplo {
                color: #333333 !important;
                padding: 3px 0 3px 20px;
                margin: 3px 0;
            }
            
            /* Links e rodapé */
            a, a:visited {
                color: #1e88e5 !important;
            }
            
            /* Alertas e notificações */
            .stAlert > div {
                color: #333333 !important;
            }
            
            /* Divisor de seções */
            .section-divider {
                border-top: 1px solid #e0e0e0;
                margin: 25px 0;
            }
            
            /* Ajuste do título da página */
            .st-emotion-cache-10trblm {
                color: #333333 !important;
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
            <p style="color: #333333;">Desenvolvido por <strong>Bruno Andrade de Luna</strong></p>
            <a href="https://www.linkedin.com/in/bruno-andrade-de-luna/" target="_blank" style="color: #1e88e5;">
                <strong>📧 Entre em contato no LinkedIn</strong>
            </a>
        </div>
        """, unsafe_allow_html=True
    )
