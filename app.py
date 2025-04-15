import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

    # Seleção da data de filtragem
    data_filtro = st.date_input("Selecione a data para análise", min_value=datetime(2020, 1, 1), max_value=datetime.today(), value=datetime(2025, 4, 13))
    df_realizado['Início convertida'] = pd.to_datetime(df_realizado['Início da viagem'], errors='coerce', dayfirst=True)
    
    # Filtrar pelo dia selecionado
    df_realizado_dia = df_realizado[df_realizado['Início convertida'].dt.date == data_filtro.date()].copy()

    # Extrair hora e faixa
    df_realizado_dia['hora'] = df_realizado_dia['Início convertida'].dt.hour
    df_realizado_dia['faixa'] = df_realizado_dia['hora'].apply(identificar_faixa_horaria)

    # Permitir escolha da coluna de distância
    colunas_disponiveis = df_realizado.columns.tolist()
    coluna_distancia = st.selectbox("Selecione a coluna de quilometragem realizada", colunas_disponiveis)

    # Somar km realizada por Serviço e Faixa
    km_realizada = df_realizado_dia.groupby(['Serviço', 'faixa'])[coluna_distancia].sum().unstack(fill_value=0)

    # Adiciona coluna com o total da quilometragem realizada por linha
    km_realizada['Total realizado'] = km_realizada.sum(axis=1)

    # Converte de volta para o formato com índice como coluna
    km_realizada = km_realizada.reset_index()

    st.subheader("Km Realizada por Faixa Horária")
    st.dataframe(km_realizada)

    # Gráfico de barras interativo para visualização da quilometragem realizada por faixa
    st.subheader("Gráfico de Quilometragem Realizada por Faixa Horária")
    plt.figure(figsize=(10, 6))
    km_realizada.set_index('Serviço')[faixas_horarias.keys()].plot(kind='bar', stacked=True, figsize=(12, 8))
    plt.title(f'Quilometragem Realizada por Faixa Horária em {data_filtro.strftime("%d/%m/%Y")}')
    plt.ylabel('Km Realizada')
    plt.xlabel('Serviço')
    plt.xticks(rotation=45)
    st.pyplot()

    # Se o CSV também tiver a coluna de distância planejada, somamos ela por faixa
    if 'distancia_planejada' in df_realizado_dia.columns:
        km_planejada = df_realizado_dia.groupby(['Serviço', 'faixa'])['distancia_planejada'].sum().unstack(fill_value=0)
        km_planejada['Total planejado (csv)'] = km_planejada.sum(axis=1)
        km_planejada = km_planejada.reset_index()

        st.subheader("Km Planejada por Faixa Horária - Extraído do CSV")
        st.dataframe(km_planejada)

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

            # Calcular total planejado
            df_planejado['Total planejado'] = df_planejado[[col for col in renomear.values()]].sum(axis=1)

            # Mesclar os dados de realizado e planejado
            df_comparativo = pd.merge(km_realizada, df_planejado, on='Serviço', how='outer', suffixes=('_realizado', '_planejado'))

            # Calcular percentual por faixa
            for faixa in faixas_horarias.keys():
                col_real = f"{faixa}_realizado"
                col_plan = f"{faixa}_planejado"
                if col_real in df_comparativo.columns and col_plan in df_comparativo.columns:
                    df_comparativo[f"{faixa}_%"] = (df_comparativo[col_real] / df_comparativo[col_plan]) * 100

            # Calcular diferença e percentual total
            df_comparativo['Diferença total'] = df_comparativo['Total realizado'] - df_comparativo['Total planejado']
            df_comparativo['% realizado vs planejado'] = (df_comparativo['Total realizado'] / df_comparativo['Total planejado']) * 100

            st.subheader("Comparativo Km Realizado x Planejado por Faixa Horária")
            st.dataframe(df_comparativo)

            # Opção para exportar os dados
            exportar = st.radio("Deseja exportar os dados?", options=["Não", "CSV", "Excel"])
            if exportar == "CSV":
                st.download_button(
                    label="Baixar CSV",
                    data=df_comparativo.to_csv(index=False),
                    file_name="comparativo_km.csv",
                    mime="text/csv"
                )
            elif exportar == "Excel":
                st.download_button(
                    label="Baixar Excel",
                    data=df_comparativo.to_excel(index=False, engine="openpyxl"),
                    file_name="comparativo_km.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Erro ao processar o arquivo .xlsx: {e}")


