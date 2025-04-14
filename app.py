import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Mobilidade", layout="wide")

st.title("📊 Dashboard de Indicadores de Mobilidade")

# Upload do arquivo
uploaded_file = st.file_uploader("Faça upload do arquivo CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=';')

    # Converte colunas de datas e horas
    df['início de viagem'] = pd.to_datetime(df['início de viagem'], errors='coerce')

    # Cria faixa horária para a distância planejada com base no início de viagem
    def classificar_faixa_horaria(hora):
        if pd.isnull(hora):
            return "Indefinido"
        h = hora.hour
        if 0 <= h < 3:
            return "00:00 - 02:59"
        elif 3 <= h < 6:
            return "03:00 - 05:59"
        elif 6 <= h < 9:
            return "06:00 - 08:59"
        elif 9 <= h < 12:
            return "09:00 - 11:59"
        elif 12 <= h < 15:
            return "12:00 - 14:59"
        elif 15 <= h < 18:
            return "15:00 - 17:59"
        elif 18 <= h < 21:
            return "18:00 - 20:59"
        else:
            return "21:00 - 23:59"

    df['faixa_fixa_planejada'] = df['início de viagem'].apply(classificar_faixa_horaria)

    # Exibe dados brutos
    st.subheader("📄 Dados Brutos")
    st.dataframe(df)

    # Tabela de KM planejado por serviço e faixa horária
    df_pivot = df.groupby(['serviço', 'faixa_fixa_planejada'])['distancia_planejada'].sum().unstack(fill_value=0)

    # Arredonda os valores
    df_pivot = df_pivot.applymap(lambda x: round(x, 2))

    # Ordena colunas na ordem correta das faixas
    ordem_faixas = [
        "00:00 - 02:59", "03:00 - 05:59", "06:00 - 08:59", "09:00 - 11:59",
        "12:00 - 14:59", "15:00 - 17:59", "18:00 - 20:59", "21:00 - 23:59"
    ]
    df_pivot = df_pivot.reindex(columns=ordem_faixas)

    # Adiciona linha total
    totais = df_pivot.sum(numeric_only=True)
    totais.name = 'Total'
    df_pivot = pd.concat([df_pivot, totais.to_frame().T])

    # Exibe tabela com somatório por faixa horária
    st.subheader("🚌 Total KM Planejado por Serviço em Faixas de Horário")
    st.dataframe(df_pivot)
