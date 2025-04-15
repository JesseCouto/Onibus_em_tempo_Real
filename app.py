import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

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
    try:
        df_realizado = pd.read_csv(csv_file, encoding="utf-8", sep=None, engine="python")
    except Exception as e:
        st.error(f"Erro ao ler o CSV: {e}")
        st.stop()

    st.subheader("Dados Brutos do CSV (Realizado)")
    st.dataframe(df_realizado)

    try:
        df_realizado['Início convertida'] = pd.to_datetime(df_realizado['Início da viagem'], errors='coerce', dayfirst=True)
    except Exception as e:
        st.warning(f"Erro na conversão da coluna 'Início da viagem': {e}")
        df_realizado['Início convertida'] = pd.NaT

    data_filtro = pd.to_datetime("2025-04-13")
    df_realizado_dia = df_realizado[df_realizado['Início convertida'].dt.date == data_filtro.date()].copy()

    df_realizado_dia['hora'] = df_realizado_dia['Início convertida'].dt.hour
    df_realizado_dia['faixa'] = df_realizado_dia['hora'].apply(identificar_faixa_horaria)

    colunas_disponiveis = df_realizado.columns.tolist()
    coluna_distancia = st.selectbox("Selecione a coluna de quilometragem realizada", colunas_disponiveis)

    # Filtro por serviço
    servicos_disponiveis = sorted(df_realizado_dia['Serviço'].dropna().unique())
    servicos_selecionados = st.multiselect("Filtrar por Serviço", servicos_disponiveis, default=servicos_disponiveis)

    df_realizado_dia = df_realizado_dia[df_realizado_dia['Serviço'].isin(servicos_selecionados)]

    km_realizada = df_realizado_dia.groupby(['Serviço', 'faixa'])[coluna_distancia].sum().unstack(fill_value=0)
    for faixa in faixas_horarias.keys():
        if faixa not in km_realizada.columns:
            km_realizada[faixa] = 0
    km_realizada = km_realizada[faixas_horarias.keys()]  # garantir ordem
    km_realizada['Total realizado'] = km_realizada.sum(axis=1)
    km_realizada = km_realizada.reset_index()

    st.subheader("Km Realizada por Faixa Horária (13/04/2025)")
    st.dataframe(km_realizada)

    if xlsx_file is not None:
        try:
            df_planejado = pd.read_excel(xlsx_file)

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
            df_planejado['Total planejado'] = df_planejado[list(renomear.values())].sum(axis=1)

            df_comparativo = pd.merge(km_realizada, df_planejado, on='Serviço', how='outer', suffixes=('_realizado', '_planejado'))

            for faixa in faixas_horarias.keys():
                if faixa in df_comparativo.columns:
                    df_comparativo[f"{faixa}_%"] = (df_comparativo[faixa + '_realizado'] / df_comparativo[faixa]) * 100

            df_comparativo['Diferença total'] = df_comparativo['Total realizado'] - df_comparativo['Total planejado']
            df_comparativo['% realizado vs planejado'] = (df_comparativo['Total realizado'] / df_comparativo['Total planejado']) * 100

            st.subheader("Comparativo Km Realizado x Planejado por Faixa Horária")
            st.dataframe(df_comparativo)

            # Gráfico Comparativo
            st.subheader("Gráfico Comparativo por Faixa Horária")

            grafico_data = df_comparativo.melt(
                id_vars=['Serviço'],
                value_vars=[
                    *[faixa for faixa in faixas_horarias.keys()],
                    *[faixa + '_realizado' for faixa in faixas_horarias.keys()]
                ],
                var_name='FaixaTipo', value_name='Quilometragem'
            )

            grafico_data['Tipo'] = grafico_data['FaixaTipo'].apply(lambda x: 'Planejado' if '_realizado' not in x else 'Realizado')
            grafico_data['Faixa'] = grafico_data['FaixaTipo'].apply(lambda x: x.replace('_realizado', ''))

            chart = alt.Chart(grafico_data).mark_bar().encode(
                x='Faixa:N',
                y='Quilometragem:Q',
                color='Tipo:N',
                column='Serviço:N'
            ).properties(width=100, height=300)

            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao ler ou processar o arquivo XLSX: {e}")








