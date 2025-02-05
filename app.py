import streamlit as st
from config import configurar_pagina
from data import load_data, VEICULOS, preparar_dados_veiculos
from tabs.mapas_calor import tab_mapas_calor
from tabs.analise_temporal import tab_analise_temporal, criar_grafico_temporal
from tabs.analise_horario import tab_analise_horario, criar_grafico_horario
from tabs.analise_local import tab_analise_local, criar_grafico_local
from tabs.analise_veiculos import tab_analise_veiculos, criar_grafico_veiculos
from tabs.chat_bot import tab_chat_bot

# Configuração inicial
configurar_pagina()

# Carregar dados
df = load_data()
df_filtrado = df[(df["Data do Sinistro"].dt.year >= 2021) & (df["Data do Sinistro"].dt.year <= 2023)]

# Preparar dados para gráficos de veículos
relacao_logradouro_veiculos_sorted = preparar_dados_veiculos(df_filtrado)

# Criar abas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Mapas de Calor", 
    "Análise Temporal", 
    "Análise por Horário", 
    "Análise por Local",
    "Análise de Veículos",
    "Chat Bot"
])

# Renderizar cada tab
with tab1:
    tab_mapas_calor(df_filtrado)

with tab2:
    tab_analise_temporal(df_filtrado)

with tab3:
    tab_analise_horario(df_filtrado)

with tab4:
    tab_analise_local(df_filtrado, VEICULOS, relacao_logradouro_veiculos_sorted)

with tab5:
    tab_analise_veiculos(df_filtrado, VEICULOS, relacao_logradouro_veiculos_sorted)

with tab6:
    tab_chat_bot(
        df_filtrado, 
        df,  # Dataset completo
        relacao_logradouro_veiculos_sorted,
        {
            'criar_grafico_temporal': criar_grafico_temporal,
            'criar_grafico_horario': criar_grafico_horario,
            'criar_grafico_local': criar_grafico_local,
            'criar_grafico_veiculos': criar_grafico_veiculos
        }
    )