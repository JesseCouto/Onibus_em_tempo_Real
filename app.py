import streamlit as st
import pandas as pd
import csv
from datetime import datetime

st.title("Análise de Quilometragem por Faixa Horária")

# Função para detectar separador do CSV
def detectar_separador(file):
    sample = file.read(2048).decode('utf-8')
    file.seek(0)
    sniffer = csv.Sniffer()
    return sniffer.sniff(sample).delimiter

# Função para determinar faixa horária
def faixa_horaria(horario):
    hora = horario.hour
    if 0 <= hora < 3:
        return "00h-03h"
    elif 3 <= hora < 6:
        return "03h-06h"
    elif 6 <= hora < 9:
        return "06h-09h"
    elif 9 <= hora < 12:
        return "09h-12h"
    elif 12 <= hora < 15:
        return "12h-15h"
    elif 15 <= hora < 18:
        return "15h-18h"
    elif 18 <= hora < 21:
        return "18h-21h"
    else:
        return "21h-24h"

# Upload do arquivo CSV de realizado
csv_file = st.file_uploader("Envie o arquivo .CSV do realizado", type="csv")

# Upload do arquivo XLSX do planejamento
xlsx_file = st.file_uploader("Envie o arquivo .XLSX do planejamento", type="xlsx")

if csv_file:
    try:
        # Detecta separador automaticamente
        separador = detectar_separador(csv_file)
        st.info(f"Separador detectado: `{separador}`")

        # Lê o arquivo CSV com o separador detectado
        df_realizado = pd.read_csv(csv_file, delimiter=separador)

        # Verifica se a coluna 'Início da viagem' existe
        if 'Início da viagem' not in df_realizado.columns:
            st.error("A coluna 'Início da viagem' não foi encontrada no CSV.")
        else:
            # Converte para datetime
            df_realizado['Início da viagem'] = pd.to_datetime(df_realizado['Início da viagem'], errors='coerce')

            # Remove linhas com data inválida
            df_realizado = df_realizado.dropna(subset=['Início da viagem'])

            # Aplica a faixa horária
            df_realizado['Faixa Horária'] = df_realizado['Início da viagem'].apply(faixa_horaria)

            # Agrupa por Serviço e Faixa Horária
            km_por_faixa = df_realizado.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()

            # Pivot para facilitar comparação
            km_pivot = km_por_faixa.pivot(index='Serviço', columns='Faixa Horária', values='distancia_planejada').fillna(0)

            st.subheader("Quilometragem realizada por faixa horária e por serviço")
            st.dataframe(km_pivot)

            # Se o arquivo XLSX foi enviado
            if xlsx_file:
                df_planejamento = pd.read_excel(xlsx_file)

                # Normaliza nomes das colunas pra evitar erro
                df_planejamento.columns = df_planejamento.columns.str.strip()

                # Junta com o planejamento
                df_comparado = df_planejamento.merge(km_pivot, how='left', on='Serviço')

                st.subheader("Comparação com o planejamento")
                st.dataframe(df_comparado)

    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {e}")
