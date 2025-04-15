import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador de Planejado x Realizado", layout="wide")

st.title("📊 Comparador de Planejado x Realizado")

# Upload do arquivo de realizado
real_file = st.file_uploader("Carregar arquivo de realizado (.csv)", type=["csv"])

if real_file is not None:
    # Leitura do arquivo CSV
    df = pd.read_csv(real_file, sep=';', encoding='latin1')

    # Garantir que a coluna de data está em formato datetime
    if 'Início da viagem' in df.columns:
        df['Início da viagem'] = pd.to_datetime(df['Início da viagem'], errors='coerce')
        df['Data Início da viagem'] = df['Início da viagem'].dt.date

    # Faixa horária por hora do início
    def classificar_faixa_horaria(horario):
        if pd.isna(horario):
            return 'Indefinido'
        hora = horario.hour
        if 5 <= hora < 8:
            return 'Madrugada'
        elif 8 <= hora < 12:
            return 'Manhã'
        elif 12 <= hora < 17:
            return 'Tarde'
        elif 17 <= hora < 21:
            return 'Noite'
        else:
            return 'Madrugada'

    df['Faixa Horária'] = df['Início da viagem'].dt.time.apply(lambda x: classificar_faixa_horaria(pd.to_datetime(x, errors='coerce')))

    # Exibir dados carregados
    st.subheader("Dados do Realizado")
    st.write(df)

    # Calcular km realizada por faixa horária
    if 'distancia_planejada' in df.columns and 'Serviço' in df.columns:
        df_grouped = df.pivot_table(
            index='Serviço',
            columns='Faixa Horária',
            values='distancia_planejada',
            aggfunc='sum',
            fill_value=0
        )

        st.subheader("Km Realizada por Faixa Horária (todas as datas)")
        st.write(df_grouped)

    # Upload da planilha de planejamento
    plan_file = st.file_uploader("Carregar arquivo de planejamento (.xlsx)", type=["xlsx"])

    if plan_file is not None:
        try:
            planejamento_df = pd.read_excel(plan_file)

            st.subheader("Planejamento")
            st.write(planejamento_df)

            if 'Data' in planejamento_df.columns:
                planejamento_df['Data'] = pd.to_datetime(planejamento_df['Data'], errors='coerce').dt.date
                data_comum = sorted(set(df['Data Início da viagem']) & set(planejamento_df['Data']))

                if len(data_comum) == 0:
                    st.warning("Não há datas em comum entre os dados realizados e o planejamento.")
                else:
                    # Seleciona uma data em comum (ex: 13/04/2025)
                    data_analise = st.selectbox("Selecionar data para análise", data_comum)

                    df_dia = df[df['Data Início da viagem'] == data_analise]
                    planejamento_dia = planejamento_df[planejamento_df['Data'] == data_analise]

                    # Recalcular distâncias por faixa horária com base no dia selecionado
                    df_grouped_dia = df_dia.pivot_table(
                        index='Serviço',
                        columns='Faixa Horária',
                        values='distancia_planejada',
                        aggfunc='sum',
                        fill_value=0
                    )

                    st.subheader(f"Km Realizada por Faixa Horária em {data_analise}")
                    st.write(df_grouped_dia)

                    # Filtrar e alinhar planejamento com os serviços e faixas horárias do realizado
                    comum_index = df_grouped_dia.index.intersection(planejamento_dia['Serviço'])
                    planejamento_dia = planejamento_dia.set_index('Serviço').loc[comum_index]
                    realizado_df = df_grouped_dia.loc[comum_index]

                    comum_colunas = realizado_df.columns.intersection(planejamento_dia.columns)
                    planejamento_dia = planejamento_dia[comum_colunas]
                    realizado_df = realizado_df[comum_colunas]

                    # Calcular percentual de cumprimento
                    percentual_df = (realizado_df / planejamento_dia.replace(0, pd.NA)) * 100
                    percentual_df = percentual_df.round(1).fillna(0)

                    st.subheader(f"Percentual de Cumprimento em {data_analise} (%)")
                    st.write(percentual_df)

        except Exception as e:
            st.error(f"Erro ao ler o arquivo de planejamento: {e}")
