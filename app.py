import streamlit as st
import pandas as pd
import datetime

st.set_page_config(layout="wide")
st.title("Análise de Quilometragem por Faixa Horária")

# Upload dos arquivos
csv_file = st.file_uploader("Envie o arquivo de realizado (.csv)", type="csv")
plan_file = st.file_uploader("Envie o arquivo de planejamento (.xlsx)", type="xlsx")

# Data de interesse
data_planejada = datetime.date(2025, 4, 13)

# Faixas horárias
faixas = {
    "00h às 03h": (0, 3),
    "03h às 06h": (3, 6),
    "06h às 09h": (6, 9),
    "09h às 12h": (9, 12),
    "12h às 15h": (12, 15),
    "15h às 18h": (15, 18),
    "18h às 21h": (18, 21),
    "21h às 24h": (21, 24),
}

# Processar realizado
if csv_file is not None:
    try:
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        df['Início da viagem'] = pd.to_datetime(df['Início da viagem'], errors='coerce')

        df = df[df['Início da viagem'].dt.date == data_planejada]
        df['Hora'] = df['Início da viagem'].dt.hour

        resultados = []
        for faixa, (inicio, fim) in faixas.items():
            faixa_df = df[(df['Hora'] >= inicio) & (df['Hora'] < fim)]
            soma_distancia = faixa_df.groupby('Serviço')['Distância'].sum()
            resultados.append(soma_distancia.rename(faixa))

        realizado = pd.concat(resultados, axis=1).fillna(0)
        st.subheader(f"Km Realizada por Faixa Horária ({data_planejada.strftime('%d/%m/%Y')})")
        st.write(realizado)

    except Exception as e:
        st.error(f"Erro ao ler ou processar o arquivo de realizado: {e}")

# Processar planejamento
if plan_file is not None:
    try:
        planejamento_df = pd.read_excel(plan_file)

        # Converter coluna de data e filtrar
        if 'Data' in planejamento_df.columns:
            planejamento_df['Data'] = pd.to_datetime(planejamento_df['Data'], dayfirst=True, errors='coerce').dt.date
            planejamento_df = planejamento_df[planejamento_df['Data'] == data_planejada]

        st.subheader("Planejamento (13/04/2025)")
        st.write(planejamento_df)

        colunas_faixas = [
            'Quilometragem entre 00h e 03h',
            'Quilometragem entre 03h e 06h',
            'Quilometragem entre 06h e 09h',
            'Quilometragem entre 09h e 12h',
            'Quilometragem entre 12h e 15h',
            'Quilometragem entre 15h e 18h',
            'Quilometragem entre 18h e 21h',
            'Quilometragem entre 21h e 24h'
        ]

        planejamento_df = planejamento_df[['Serviço'] + colunas_faixas]
        planejamento_df[colunas_faixas] = planejamento_df[colunas_faixas].apply(
            lambda x: x.astype(str).str.replace(',', '.').astype(float)
        )
        planejamento_df = planejamento_df.set_index('Serviço')

        # Comparar com realizado
        realizado = realizado.reindex(index=planejamento_df.index, columns=colunas_faixas, fill_value=0)

        percentual_df = (realizado / planejamento_df.replace(0, pd.NA)) * 100
        percentual_df = percentual_df.fillna(0).round(1)

        st.subheader("Percentual de Cumprimento (%) - 13/04/2025")
        st.write(percentual_df)

    except Exception as e:
        st.error(f"Erro ao ler ou processar o arquivo de planejamento: {e}")
