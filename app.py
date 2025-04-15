import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Análise de Quilometragem por Faixa Horária")

# Upload dos arquivos
csv_file = st.file_uploader("Faça upload do arquivo .csv (Realizado)", type=["csv"])
xlsx_file = st.file_uploader("Faça upload do arquivo .xlsx (Planejado)", type=["xlsx"])

# Faixas horárias definidas
faixas_horarias = {
    "00:00 - 02:59": (0, 3),
    "03:00 - 05:59": (3, 6),
    "06:00 - 08:59": (6, 9),
    "09:00 - 11:59": (9, 12),
    "12:00 - 14:59": (12, 15),
    "15:00 - 17:59": (15, 18),
    "18:00 - 20:59": (18, 21),
    "21:00 - 23:59": (21, 24)
}

def identificar_faixa_horaria(hora):
    for faixa, (inicio, fim) in faixas_horarias.items():
        if inicio <= hora < fim:
            return faixa
    return "Fora do intervalo"

if csv_file is not None:
    # Leitura do CSV com detecção automática de separador e encoding
    try:
        df_realizado = pd.read_csv(csv_file, encoding="utf-8", sep=None, engine="python")
    except Exception as e:
        st.error(f"Erro ao ler o CSV: {e}")
        st.stop()

    # Mostrar dados brutos do CSV
    st.subheader("Dados Brutos do CSV (Realizado)")
    st.dataframe(df_realizado)

    # Conversão de datas sem alterar a coluna original, apenas para análise posterior
    try:
        df_realizado['Início convertida'] = pd.to_datetime(df_realizado['Início da viagem'], errors='coerce', dayfirst=True)
    except Exception as e:
        st.warning(f"Erro na conversão da coluna 'Início da viagem': {e}")
        df_realizado['Início convertida'] = pd.NaT

    # Filtrar pelo dia 13/04/2025
    data_filtro = pd.to_datetime("2025-04-13")
    df_realizado_dia = df_realizado[df_realizado['Início convertida'].dt.date == data_filtro.date()].copy()

    # Extrair hora e faixa
    df_realizado_dia['hora'] = df_realizado_dia['Início convertida'].dt.hour
    df_realizado_dia['faixa'] = df_realizado_dia['hora'].apply(identificar_faixa_horaria)

    # Somar km realizada por Serviço e Faixa
    km_realizada = df_realizado_dia.groupby(['Serviço', 'faixa'])['distancia_planejada'].sum().unstack(fill_value=0).reset_index()

    st.subheader("Km Realizada por Faixa Horária (13/04/2025)")
    st.dataframe(km_realizada)

    # Comparação com planejado
    if xlsx_file is not None:
        try:
            df_planejado = pd.read_excel(xlsx_file)

            # Agrupar por serviço e reorganizar colunas
            colunas_planejado = [
                "Serviço",
                "Quilometragem entre 00h e 03h",
                "Quilometragem entre 03h e 06h",
                "Quilometragem entre 06h e 09h",
                "Quilometragem entre 09h e 12h",
                "Quilometragem entre 12h e 15h",
                "Quilometragem entre 15h e 18h",
                "Quilometragem entre 18h e 21h",
                "Quilometragem entre 21h e 24h",
            ]

            df_planejado = df_planejado[colunas_planejado]

            # Renomear colunas para facilitar comparação
            renomear = {
                "Quilometragem entre 00h e 03h": "00:00 - 02:59",
                "Quilometragem entre 03h e 06h": "03:00 - 05:59",
                "Quilometragem entre 06h e 09h": "06:00 - 08:59",
                "Quilometragem entre 09h e 12h": "09:00 - 11:59",
                "Quilometragem entre 12h e 15h": "12:00 - 14:59",
                "Quilometragem entre 15h e 18h": "15:00 - 17:59",
                "Quilometragem entre 18h e 21h": "18:00 - 20:59",
                "Quilometragem entre 21h e 24h": "21:00 - 23:59",
            }

            df_planejado = df_planejado.rename(columns=renomear)

            # Mesclar os dados de realizado e planejado
            df_comparativo = pd.merge(km_realizada, df_planejado, on='Serviço', how='outer', suffixes=('_realizado', '_planejado'))

            # Calcular percentual
            for faixa in faixas_horarias.keys():
                col_real = f"{faixa}_realizado"
                col_plan = f"{faixa}_planejado"
                if col_real in df_comparativo.columns and col_plan in df_comparativo.columns:
                    df_comparativo[f"{faixa}_%"] = (df_comparativo[col_real] / df_comparativo[col_plan]) * 100

            st.subheader("Comparativo Km Realizado x Planejado por Faixa Horária")
            st.dataframe(df_comparativo)

        except Exception as e:
            st.error(f"Erro ao processar o arquivo .xlsx: {e}")

