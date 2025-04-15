import streamlit as st
import pandas as pd
import numpy as np
import dateparser

st.set_page_config(layout="wide")

st.title("Análise de Viagens Realizadas e Planejamento")

# Upload dos arquivos
arquivo_csv = st.file_uploader("Envie o arquivo de realizado (.csv)", type=["csv"])
arquivo_excel = st.file_uploader("Envie o arquivo de planejamento (.xlsx)", type=["xlsx"])

if arquivo_csv and arquivo_excel:
    try:
        # Leitura do arquivo CSV com detecção automática de delimitador
        df_realizado = pd.read_csv(arquivo_csv, sep=None, engine='python')

        # Conversão de data com dateparser
        df_realizado['Início da viagem'] = df_realizado['Início da viagem'].apply(
            lambda x: dateparser.parse(x)
        )

        # Criação da faixa horária
        def faixa_horaria(hora):
            if hora < 3:
                return "00h-03h"
            elif hora < 6:
                return "03h-06h"
            elif hora < 9:
                return "06h-09h"
            elif hora < 12:
                return "09h-12h"
            elif hora < 15:
                return "12h-15h"
            elif hora < 18:
                return "15h-18h"
            elif hora < 21:
                return "18h-21h"
            else:
                return "21h-24h"

        df_realizado['Hora'] = df_realizado['Início da viagem'].dt.hour
        df_realizado['Faixa Horária'] = df_realizado['Hora'].apply(faixa_horaria)

        # Cálculo de km por serviço e faixa horária
        resumo_realizado = df_realizado.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()
        resumo_pivot = resumo_realizado.pivot(index='Serviço', columns='Faixa Horária', values='distancia_planejada').fillna(0)

        # Exibição do realizado
        st.subheader("Quilometragem Realizada por Faixa Horária")
        st.dataframe(resumo_pivot.style.format('{:,.2f}'))

        # Leitura do planejamento
        df_planejamento = pd.read_excel(arquivo_excel)

        # Exibição do planejamento
        st.subheader("Planejamento Original")
        st.dataframe(df_planejamento)

    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {e}")
