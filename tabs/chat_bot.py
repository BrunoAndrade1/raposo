import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate


def tab_chat_bot(df_filtrado, df_completo, relacao_logradouro_veiculos_sorted, funcoes_graficos):
    # Aplicar estilos CSS personalizados
    st.markdown("""
        <style>
            /* Estilo específico para o título do chat bot */
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
            h1, h2, h3, h4, .st-emotion-cache-10trblm {
                color: #FFFFFF !important;
                font-weight: 600 !important;
                letter-spacing: 0.5px !important;
            }
            
            /* Força a cor branca no título */
            .st-emotion-cache-10trblm {
                color: #FFFFFF !important;
            }

            /* Outros estilos permanecem os mesmos ... */
        </style>
    """, unsafe_allow_html=True)


    st.subheader("Chat Bot de Análise de Sinistros")
    
    # Configurar API key
    api_key = st.secrets["openai"]["api_key"]
    os.environ["OPENAI_API_KEY"] = api_key

    # Template para o chatbot
    TEMPLATE = """Você é um assistente especializado em análise de dados de sinistros de trânsito, focado em analisar acidentes na Rodovia Raposo Tavares e regiões relacionadas entre 2021 e 2023.

    Instruções específicas:
    1. Ao analisar dados temporais:
       - Compare a evolução ano a ano
       - Identifique padrões mensais
       - Destaque tendências importantes

    2. Ao analisar localização:
       - Indique os pontos mais críticos
       - Mencione KMs específicos quando relevante
       - Relacione com características da via

    3. Ao analisar horários:
       - Compare períodos do dia
       - Diferencie dias úteis e fins de semana
       - Identifique horários de pico

    4. Ao analisar tipos de veículos:
       - Compare diferentes categorias
       - Destaque os mais frequentes
       - Relacione com horários ou locais quando relevante

    5. Para cada análise:
       - Forneça números específicos
       - Explique o significado dos dados
       - Sugira insights relevantes

    Dados disponíveis:
    {context}

    Histórico da conversa:
    {chat_history}

    Pergunta: {question}
    
    Responda de forma clara e direta, usando dados específicos para suportar suas análises. Se necessário, sugira a visualização de gráficos ou mapas relevantes.
    
    Resposta:"""

    # Criar base de conhecimento
    @st.cache_resource
    def criar_base_conhecimento(df, relacao_veiculos):
        descricao_dashboard = f"""
        Análise do Dataset de Sinistros (2021-2023):

        Estatísticas Gerais:
        - Total de registros: {len(df)}
        - Média diária: {len(df)/df['Data do Sinistro'].dt.date.nunique():.1f} sinistros
        - Horário com mais ocorrências: {df['Hora do Sinistro'].mode().iloc[0]}h
        - Local com mais registros: {df['Logradouro'].mode().iloc[0]}
        - Coordenadas médias: Latitude {df['latitude'].mean():.4f}, Longitude {df['longitude'].mean():.4f}

        Análises Disponíveis:
        1. Temporal:
        - Evolução anual dos sinistros
        - Distribuição mensal
        - Padrões sazonais

        2. Horária:
        - Horários mais críticos
        - Comparação dia vs noite
        - Padrão dias úteis vs fins de semana

        3. Local e Espacial:
        - Ranking de locais mais críticos
        - KMs com mais ocorrências
        - Concentração geográfica
        - Mapas de calor por região
        - Distribuição espacial por tipo de veículo

        4. Veículos:
        - Tipos mais envolvidos
        - Comparativo entre categorias
        - Proporções e distribuições
        """

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200
        )
        documentos = text_splitter.split_text(descricao_dashboard)
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(documentos, embeddings)
        return vectorstore

    # Criar chatbot
    @st.cache_resource
    def criar_chatbot(_vectorstore):
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7
        )
        
        prompt = PromptTemplate(
            template=TEMPLATE,
            input_variables=["context", "chat_history", "question"]
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        chatbot = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=_vectorstore.as_retriever(),
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt}
        )
        
        return chatbot

    # Inicializar chat
    vectorstore = criar_base_conhecimento(df_filtrado, relacao_logradouro_veiculos_sorted)
    chatbot = criar_chatbot(vectorstore)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Único campo de chat (utilizando uma key única)
    if prompt := st.chat_input("💭 Digite sua pergunta sobre os sinistros...", key="chat_input_1"):
        st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner('Analisando sua pergunta...'):
                resposta = chatbot({
                    "question": prompt + "\nConsidere as análises disponíveis no dashboard para responder."
                })
            st.markdown(resposta["answer"])
            
            # Mostrar visualização se necessário
            if any(palavra in prompt.lower() for palavra in 
                  ["gráfico", "visualizar", "mostrar", "comparar", "evolução", "distribuição", 
                   "mapa", "área", "região", "geográfico", "concentração"]):
                with st.expander("📊 Ver Visualização"):
                    # Verifica se é pedido de mapa/análise geográfica
                    if any(palavra in prompt.lower() for palavra in 
                          ["mapa", "região", "área", "localização", "geográfico", "concentração"]):
                        
                        if "moto" in prompt.lower() or "motocicleta" in prompt.lower():
                            # Mapa de calor para motos
                            st.subheader("Mapa de Calor - Sinistros com Motocicletas")
                            df_moto = df_filtrado[
                                (df_filtrado["Motocicleta envolvida"] > 0) & 
                                df_filtrado["latitude"].notna() & 
                                df_filtrado["longitude"].notna()
                            ].copy()
                            df_moto["latitude"] = df_moto["latitude"].astype(str).str.replace(",", ".").astype(float)
                            df_moto["longitude"] = df_moto["longitude"].astype(str).str.replace(",", ".").astype(float)
                            df_moto["count"] = df_moto.groupby(["latitude", "longitude"])["latitude"].transform("count")
                            
                            mapa_calor_motos = folium.Map(
                                location=[df_moto["latitude"].mean(), df_moto["longitude"].mean()],
                                zoom_start=12
                            )
                            
                            heat_data_moto = list(zip(
                                df_moto["latitude"],
                                df_moto["longitude"],
                                df_moto["count"]
                            ))
                            
                            HeatMap(
                                heat_data_moto,
                                radius=15,
                                blur=20,
                                min_opacity=0.5,
                                max_zoom=15
                            ).add_to(mapa_calor_motos)
                            
                            # Adicionar marcadores com números
                            for _, row in df_moto.drop_duplicates(subset=["latitude", "longitude"]).iterrows():
                                folium.Marker(
                                    location=[row["latitude"], row["longitude"]],
                                    icon=folium.DivIcon(html=f'<b style="font-size: 10pt; color: red;">{int(row["count"])}</b>')
                                ).add_to(mapa_calor_motos)
                                
                            folium_static(mapa_calor_motos, width=700)
                            
                        else:
                            # Mapa de calor geral
                            st.subheader("Mapa de Calor - Todos os Sinistros")
                            df_mapa = df_filtrado.dropna(subset=["latitude", "longitude"]).copy()
                            df_mapa["latitude"] = df_mapa["latitude"].astype(str).str.replace(",", ".").astype(float)
                            df_mapa["longitude"] = df_mapa["longitude"].astype(str).str.replace(",", ".").astype(float)
                            df_mapa["count"] = df_mapa.groupby(["latitude", "longitude"])["latitude"].transform("count")
                            
                            mapa_calor = folium.Map(
                                location=[df_mapa["latitude"].mean(), df_mapa["longitude"].mean()],
                                zoom_start=12
                            )
                            
                            heat_data = list(zip(
                                df_mapa["latitude"],
                                df_mapa["longitude"],
                                df_mapa["count"]
                            ))
                            
                            HeatMap(heat_data, radius=10, blur=15).add_to(mapa_calor)
                            
                            # Adicionar marcadores com números
                            for _, row in df_mapa.drop_duplicates(subset=["latitude", "longitude"]).iterrows():
                                folium.Marker(
                                    location=[row["latitude"], row["longitude"]],
                                    icon=folium.DivIcon(html=f'<b style="font-size: 10pt; color: black;">{int(row["count"])}</b>')
                                ).add_to(mapa_calor)
                                
                            folium_static(mapa_calor, width=700)
                    
                    # Usar funções de gráficos passadas como parâmetro
                    elif any(palavra in prompt.lower() for palavra in ["hora", "horário", "período"]):
                        try:
                            fig = funcoes_graficos['criar_grafico_horario'](df_filtrado)
                            st.pyplot(fig)
                        except Exception as e:
                            st.error("Erro ao gerar gráfico de horário: " + str(e))
                    
                    elif any(palavra in prompt.lower() for palavra in ["local", "logradouro", "lugar"]):
                        try:
                            fig = funcoes_graficos['criar_grafico_local'](df_filtrado)
                            st.pyplot(fig)
                        except Exception as e:
                            st.error("Erro ao gerar gráfico de local: " + str(e))
                    
                    elif any(palavra in prompt.lower() for palavra in ["ano", "anual", "evolução"]):
                        try:
                            fig = funcoes_graficos['criar_grafico_temporal'](df_filtrado)
                            st.pyplot(fig)
                        except Exception as e:
                            st.error("Erro ao gerar gráfico temporal: " + str(e))
                    
                    elif any(palavra in prompt.lower() for palavra in ["veículo", "carro", "moto"]):
                        try:
                            veiculos = [
                                "Automóvel envolvido",
                                "Motocicleta envolvida",
                                "Bicicleta envolvida",
                                "Caminhão envolvido",
                                "Ônibus  envolvido",
                                "Outros veículos envolvidos"
                            ]
                            fig = funcoes_graficos['criar_grafico_veiculos'](df_filtrado, veiculos)
                            st.pyplot(fig)
                        except Exception as e:
                            st.error("Erro ao gerar gráfico de veículos: " + str(e))

        st.session_state.messages.append({"role": "assistant", "content": resposta["answer"]})

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Exemplos de perguntas
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="categoria">
                <span>📊</span>
                <span>Análise Temporal</span>
            </div>
            <div class="pergunta-exemplo">• Como evoluiu o número de sinistros entre 2021 e 2023?</div>
            <div class="pergunta-exemplo">• Qual é o mês com mais registros?</div>
            <div class="pergunta-exemplo">• Qual a média mensal de sinistros?</div>

            <div class="categoria">
                <span>🗺️</span>
                <span>Análise Espacial</span>
            </div>
            <div class="pergunta-exemplo">• Onde se concentram os sinistros na cidade?</div>
            <div class="pergunta-exemplo">• Qual a distribuição geográfica dos acidentes com motos?</div>
            <div class="pergunta-exemplo">• Mostre o mapa de calor dos sinistros</div>

            <div class="categoria">
                <span>🕒</span>
                <span>Análise por Horário</span>
            </div>
            <div class="pergunta-exemplo">• Quais são os horários mais críticos?</div>
            <div class="pergunta-exemplo">• Como é a distribuição entre dia e noite?</div>
            <div class="pergunta-exemplo">• Tem diferença entre dias úteis e fins de semana?</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="categoria">
                <span>📍</span>
                <span>Análise por Local</span>
            </div>
            <div class="pergunta-exemplo">• Quais são os locais mais perigosos?</div>
            <div class="pergunta-exemplo">• Qual KM registra mais ocorrências?</div>
            <div class="pergunta-exemplo">• Como é a distribuição geográfica dos sinistros?</div>

            <div class="categoria">
                <span>🚗</span>
                <span>Análise de Veículos</span>
            </div>
            <div class="pergunta-exemplo">• Qual tipo de veículo se envolve mais?</div>
            <div class="pergunta-exemplo">• Como se comparam carros e motos?</div>
            <div class="pergunta-exemplo">• Qual a proporção de cada tipo de veículo?</div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
