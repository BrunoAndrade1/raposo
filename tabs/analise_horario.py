import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def criar_grafico_horario(df):
    """Função para criar gráfico horário que pode ser reutilizada"""
    sinistros_por_hora = df["Hora do Sinistro"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sinistros_por_hora.index, sinistros_por_hora.values, marker='o')
    ax.set_xlabel("Hora do Dia")
    ax.set_ylabel("Quantidade")
    ax.set_xticks(range(24))
    plt.tight_layout()
    return fig

def tab_analise_horario(df_filtrado):
    # Criar uma cópia do DataFrame para evitar warnings
    df_analysis = df_filtrado.copy()
    
    # Define lista de veículos
    veiculos = [
        "Automóvel envolvido",
        "Motocicleta envolvida",
        "Bicicleta envolvida",
        "Caminhão envolvido",
        "Ônibus  envolvido",
        "Outros veículos envolvidos",
        "Veículo envolvido não disponível"
    ]

    # Primeira linha de gráficos
    col1, col2 = st.columns([0.48, 0.48], gap="large")

    with col1:
        # Gráfico de sinistros por hora
        st.subheader("Horários com Mais Sinistros (2021-2023)")
        sinistros_por_hora = df_analysis["Hora do Sinistro"].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(6, 3))
        plt.plot(sinistros_por_hora.index, sinistros_por_hora.values, 
                marker="o", linestyle="-", label="Todos os Dias", color="green")
        
        for i in sinistros_por_hora.index:
            plt.text(i, sinistros_por_hora[i], str(int(sinistros_por_hora[i])), 
                    ha='center', va='bottom', fontsize=7, color="green")
        
        plt.xlabel("Hora do Dia", fontsize=8)
        plt.ylabel("Quantidade", fontsize=8)
        plt.xticks(range(0, 24), fontsize=7)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    with col2:
        # Relação entre Horário e Tipo de Veículo
        st.subheader("Relação entre Horário e Veículos (2021-2023)")
        df_veiculo_horario = df_analysis.groupby("Hora do Sinistro")[veiculos].sum()
        
        fig, ax = plt.subplots(figsize=(6, 3))
        cores = plt.cm.tab10(np.linspace(0, 1, len(veiculos)))
        
        for veiculo, cor in zip(veiculos, cores):
            plt.plot(df_veiculo_horario.index, df_veiculo_horario[veiculo], 
                    marker="o", linestyle="-", label=veiculo, color=cor, markersize=3)
            
            for hora in df_veiculo_horario.index:
                valor = df_veiculo_horario[veiculo][hora]
                if valor > 0:
                    plt.text(hora, valor, str(int(valor)), 
                            ha='center', va='bottom', fontsize=6, color=cor)
        
        plt.xlabel("Hora do Dia", fontsize=8)
        plt.ylabel("Quantidade", fontsize=8)
        plt.xticks(range(0, 24), fontsize=7)
        plt.legend(fontsize=6, bbox_to_anchor=(1.05, 1))
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    st.markdown("---")
    
    # Terceira linha com gráfico de comparação dias úteis vs fins de semana
    st.subheader("Dias Úteis vs. Fins de Semana por Horário (2021-2023)")
    
    # Criar colunas para análise de dias da semana
    df_analysis.loc[:, "Dia da Semana"] = df_analysis["Data do Sinistro"].dt.day_name()
    df_analysis.loc[:, "É Fim de Semana"] = df_analysis["Dia da Semana"].isin(["Saturday", "Sunday"])

    # Separar os dados
    df_fim_de_semana = df_analysis[df_analysis["É Fim de Semana"] == True]
    df_dias_uteis = df_analysis[df_analysis["É Fim de Semana"] == False]

    # Contar sinistros por hora
    sinistros_por_hora_fds = df_fim_de_semana["Hora do Sinistro"].value_counts().sort_index()
    sinistros_por_hora_uteis = df_dias_uteis["Hora do Sinistro"].value_counts().sort_index()

    # Criar gráfico
    fig, ax = plt.subplots(figsize=(12, 4))
    plt.plot(sinistros_por_hora_fds.index, sinistros_por_hora_fds.values, 
            marker="o", linestyle="-", label="Fins de Semana", color="red", markersize=3)
    plt.plot(sinistros_por_hora_uteis.index, sinistros_por_hora_uteis.values, 
            marker="o", linestyle="-", label="Dias Úteis", color="blue", markersize=3)

    # Adicionar rótulos
    for i in sinistros_por_hora_fds.index:
        plt.text(i, sinistros_por_hora_fds[i], str(int(sinistros_por_hora_fds[i])), 
                ha='center', va='bottom', fontsize=7, color="red")

    for i in sinistros_por_hora_uteis.index:
        plt.text(i, sinistros_por_hora_uteis[i], str(int(sinistros_por_hora_uteis[i])), 
                ha='center', va='bottom', fontsize=7, color="blue")

    plt.xlabel("Hora do Dia", fontsize=8)
    plt.ylabel("Quantidade de Sinistros", fontsize=8)
    plt.xticks(range(0, 24), fontsize=7)
    plt.legend(fontsize=8)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)    
    
    # Segunda linha de gráficos
    col3, col4 = st.columns([0.48, 0.48], gap="large")

    with col3:
        # Comparação Automóveis vs Motocicletas
        st.subheader("Automóveis vs. Motocicletas por Horário (2021-2023)")
        df_veiculos_horario = df_analysis.groupby("Hora do Sinistro")[
            ["Automóvel envolvido", "Motocicleta envolvida"]].sum()
        
        fig, ax = plt.subplots(figsize=(6, 3))
        plt.plot(df_veiculos_horario.index, df_veiculos_horario["Automóvel envolvido"], 
                marker="o", linestyle="-", label="Automóveis", color="blue", markersize=3)
        plt.plot(df_veiculos_horario.index, df_veiculos_horario["Motocicleta envolvida"], 
                marker="o", linestyle="-", label="Motocicletas", color="red", markersize=3)
        
        for i in df_veiculos_horario.index:
            plt.text(i, df_veiculos_horario["Automóvel envolvido"][i], 
                    str(int(df_veiculos_horario["Automóvel envolvido"][i])), 
                    ha='center', va='bottom', fontsize=7, color="blue")
            plt.text(i, df_veiculos_horario["Motocicleta envolvida"][i], 
                    str(int(df_veiculos_horario["Motocicleta envolvida"][i])), 
                    ha='center', va='bottom', fontsize=7, color="red")
        
        plt.xlabel("Hora do Dia", fontsize=8)
        plt.ylabel("Quantidade", fontsize=8)
        plt.xticks(range(0, 24), fontsize=7)
        plt.legend(fontsize=7)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    with col4:
        # Gráfico Diurno vs Noturno
        st.subheader("Sinistros por Período (2021-2023)")
        df_analysis.loc[:, "Período do Dia"] = df_analysis["Hora do Sinistro"].apply(
            lambda x: "Noturno" if x < 6 or x >= 18 else "Diurno"
        )
        sinistros_por_periodo = df_analysis["Período do Dia"].value_counts()
        
        fig, ax = plt.subplots(figsize=(6, 3))
        bars = ax.bar(sinistros_por_periodo.index, sinistros_por_periodo.values, 
                     color=["gold", "darkblue"])
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), 
                   ha='center', va='bottom', fontsize=8)
        
        ax.set_xlabel("Período do Dia", fontsize=8)
        ax.set_ylabel("Quantidade", fontsize=8)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)