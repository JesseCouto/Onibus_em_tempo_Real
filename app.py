import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cumprimento de Viagens", layout="wide")

st.title("Análise de Cumprimento de Viagens por Faixa Horária")

# Upload dos arquivos
st.sidebar.header("Carregar arquivos")
csv_file = st.sidebar.file_uploader("Carregar arquivo de realizado (.csv)", type="csv")
plan_file = st.sidebar.file_uploader("Carregar arquivo de planejamento (.xlsx)", type="xlsx")

def classificar_faixa_horaria(horario):
    if pd.isnull(horario):
        return "Indefinido"
    hora = horario.hour
    if 0 <= hora < 3:
        return "00:00 - 02:59"
    elif 3 <= hora < 6:
        return "03:00 - 05:59"
    elif 6 <= hora < 9:
        return "06:00 - 08:59"
    elif 9 <= hora < 12:
        return "09:00 - 11:59"
    elif 12 <= hora < 15:
        return "12:00 - 14:59"
    elif 15 <= hora < 18:
        return "15:00 - 17:59"
    elif 18 <= hora < 21:
        return "18:00 - 20:59"
    else:
        return "21:00 - 23:59"

if csv_file:
    try:
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        df['Início da viagem'] = pd.to_datetime(df['Início da viagem'], errors='coerce')
        df['Faixa Horária'] = df['Início da viagem'].dt.time.apply(
            lambda x: classificar_faixa_horaria(pd.to_datetime(x, errors='coerce'))
        )

        st.subheader("Dados de Viagens Realizadas")
        st.write(df.head())

        # Tabela dinâmica de viagens por faixa horária e serviço
        viagens_por_faixa = df.groupby(['Serviço', 'Faixa Horária']).size().unstack(fill_value=0)
        st.subheader("Viagens Realizadas por Faixa Horária")
        st.dataframe(viagens_por_faixa)

        if plan_file:
            try:
                planejamento_df = pd.read_excel(plan_file)
                st.subheader("Planejamento")
                st.write(planejamento_df)

                # Converter coluna "Serviço" para índice
                planejamento_df.set_index('Serviço', inplace=True)

                # Converter valores para float, tratando vírgulas
                planejamento_df = planejamento_df.applymap(
                    lambda x: float(str(x).replace(',', '.')) if pd.notnull(x) else 0
                )

                # Alinhar os índices e colunas para fazer a divisão
                planejamento_df = planejamento_df.reindex(index=viagens_por_faixa.index, columns=viagens_por_faixa.columns, fill_value=0)

                percentual_df = (viagens_por_faixa / planejamento_df.replace(0, pd.NA)) * 100
                percentual_df = percentual_df.fillna(0).round(1)

                st.subheader("Percentual de Cumprimento (%) - 13/04/2025")
                st.dataframe(percentual_df)

            except Exception as e:
                st.error(f"Erro ao ler ou processar o arquivo de planejamento: {e}")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo CSV: {e}")
