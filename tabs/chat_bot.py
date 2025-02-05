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
    st.subheader("Chat Bot de Análise de Sinistros")
    
    # Aplicar estilos CSS personalizados
    st.markdown("""
        <style>
            .categoria {
                margin-top: 15px;
                margin-bottom: 8px;
                color: #ffffff;
                font-weight: bold;
                padding: 5px 0;
            }
            .pergunta-exemplo {
                padding: 3px 0 3px 20px;
                color: #e0e0e0;
                margin: 3px 0;
            }
            .chat-container {
                margin: 20px 0;
                padding: 15px;
                border-radius: 5px;
                background-color: #1E1E1E;
            }
            .section-divider {
                margin: 25px 0;
                border: none;
                border-top: 1px solid #333;
            }
            .stTextInput>div>div>input {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333;
                padding: 15px;
                font-size: 16px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Configurar API key
    api_key = st.secrets["openai"]["api_key"]
    os.environ["OPENAI_API_KEY"] = api_key

    # Template para o chatbot
    TEMPLATE = """Você é um assistente especializado em análise de dados de sinistros de trânsito.
    Analise os dados disponíveis e responda de forma clara e objetiva.

    Dados disponíveis:
    {context}

    Histórico da conversa:
    {chat_history}

    Pergunta: {question}
    
    Resposta:"""

    # Funções para criar gráficos
    def criar_grafico_temporal(df):
        sinistros_por_ano = df["Data do Sinistro"].dt.year.value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(sinistros_por_ano.index, sinistros_por_ano.values, color="#1E88E5")
        ax.set_xlabel("Ano")
        ax.set_ylabel("Quantidade")
        for i, v in enumerate(sinistros_por_ano.values):
            ax.text(sinistros_por_ano.index[i], v, str(v), ha='center', va='bottom')
        plt.tight_layout()
        return fig

    def criar_grafico_horario(df):
        sinistros_por_hora = df["Hora do Sinistro"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(sinistros_por_hora.index, sinistros_por_hora.values, marker='o')
        ax.set_xlabel("Hora do Dia")
        ax.set_ylabel("Quantidade")
        ax.set_xticks(range(24))
        plt.tight_layout()
        return fig

    def criar_grafico_local(df, top_n=10):
        top_locais = df["Logradouro"].value_counts().head(top_n)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(top_locais.index, top_locais.values, color="#1E88E5")
        ax.set_xlabel("Quantidade")
        ax.set_ylabel("Logradouro")
        plt.tight_layout()
        return fig

    def criar_grafico_veiculos(df, veiculos):
        total_por_tipo = df[veiculos].sum().sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(total_por_tipo)), total_por_tipo.values, color="#1E88E5")
        ax.set_yticks(range(len(total_por_tipo)))
        ax.set_yticklabels(total_por_tipo.index)
        plt.tight_layout()
        return fig

    # Criar colunas para os exemplos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class="categoria">📊 Análise Temporal</div>
            <div class="pergunta-exemplo">• Como evoluiu o número de sinistros entre 2021 e 2023?</div>
            <div class="pergunta-exemplo">• Qual é o mês com mais registros?</div>
            <div class="pergunta-exemplo">• Qual a média mensal de sinistros?</div>

            <div class="categoria">🗺️ Análise Espacial</div>
            <div class="pergunta-exemplo">• Onde se concentram os sinistros na cidade?</div>
            <div class="pergunta-exemplo">• Qual a distribuição geográfica dos acidentes com motos?</div>
            <div class="pergunta-exemplo">• Mostre o mapa de calor dos sinistros</div>

            <div class="categoria">🕒 Análise por Horário</div>
            <div class="pergunta-exemplo">• Quais são os horários mais críticos?</div>
            <div class="pergunta-exemplo">• Como é a distribuição entre dia e noite?</div>
            <div class="pergunta-exemplo">• Tem diferença entre dias úteis e fins de semana?</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="categoria">📍 Análise por Local</div>
            <div class="pergunta-exemplo">• Quais são os locais mais perigosos?</div>
            <div class="pergunta-exemplo">• Qual KM registra mais ocorrências?</div>
            <div class="pergunta-exemplo">• Como é a distribuição geográfica dos sinistros?</div>

            <div class="categoria">🚗 Análise de Veículos</div>
            <div class="pergunta-exemplo">• Qual tipo de veículo se envolve mais?</div>
            <div class="pergunta-exemplo">• Como se comparam carros e motos?</div>
            <div class="pergunta-exemplo">• Qual a proporção de cada tipo de veículo?</div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

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

    # Aqui vamos manter apenas a última pergunta e resposta
    if prompt := st.chat_input("💭 Digite sua pergunta sobre os sinistros..."):
        # Limpar mensagens anteriores
        st.session_state.messages = []
        
        # Adicionar apenas a nova pergunta
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
                            # Mapa de calor específico para motos
                            st.subheader("Mapa de Calor - Sinistros com Motocicletas")
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
                            folium_static(mapa_calor_motos, width=700)
                        else:
                            # Mapa de calor geral
                            st.subheader("Mapa de Calor - Todos os Sinistros")
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
                            folium_static(mapa_calor, width=700)
                    
                    # Demais visualizações existentes
                    elif any(palavra in prompt.lower() for palavra in ["hora", "horário", "período"]):
                        fig = criar_grafico_horario(df_filtrado)
                        st.pyplot(fig)
                    
                    elif any(palavra in prompt.lower() for palavra in ["local", "logradouro", "lugar"]):
                        fig = criar_grafico_local(df_filtrado)
                        st.pyplot(fig)
                    
                    elif any(palavra in prompt.lower() for palavra in ["ano", "anual", "evolução"]):
                        fig = criar_grafico_temporal(df_filtrado)
                        st.pyplot(fig)
                    
                    elif any(palavra in prompt.lower() for palavra in ["veículo", "carro", "moto"]):
                        veiculos = [
                            "Automóvel envolvido",
                            "Motocicleta envolvida",
                            "Bicicleta envolvida",
                            "Caminhão envolvido",
                            "Ônibus  envolvido",
                            "Outros veículos envolvidos"
                        ]
                        fig = criar_grafico_veiculos(df_filtrado, veiculos)
                        st.pyplot(fig)  # Adicionar o parênteses fechando aqui

        st.session_state.messages.append({"role": "assistant", "content": resposta["answer"]})