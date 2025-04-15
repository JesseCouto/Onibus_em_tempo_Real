import streamlit as st
import pandas as pd

st.title("Visualização de Dados Realizados x Planejamento")

# Carregar arquivo CSV
st.sidebar.header("Carregar Dados Realizados (CSV)")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=["csv"])

# Carregar arquivo de planejamento
st.sidebar.header("Carregar Planejamento (XLSX)")
plan_file = st.sidebar.file_uploader("Escolha um arquivo XLSX", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if 'Início da viagem' in df.columns:
        month_map = {
            'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04',
            'mai.': '05', 'jun.': '06', 'jul.': '07', 'ago.': '08',
            'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
        }

        try:
            # Extrair data e hora separadamente
            df['Data Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2} de \w{3}\. de \d{4})')[0]
            df['Data Início da viagem'] = df['Data Início da viagem'].replace(month_map, regex=True)
            df['Data Início da viagem'] = df['Data Início da viagem'].str.replace(r' de ', '/', regex=True)
            df['Data Início da viagem'] = pd.to_datetime(df['Data Início da viagem'], format='%d/%m/%Y', errors='coerce')
            df['Data Início da viagem'] = df['Data Início da viagem'].dt.date

            df['Hora Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2}:\d{2}:\d{2})')[0]
            df['Hora Início da viagem'] = pd.to_datetime(df['Hora Início da viagem'], format='%H:%M:%S', errors='coerce').dt.time

            df = df.dropna(subset=['Data Início da viagem', 'Hora Início da viagem'])

        except Exception as e:
            st.error(f"Erro ao separar e converter os dados: {e}")

        # Converter distancia_planejada se existir
        if 'distancia_planejada' in df.columns:
            df['distancia_planejada'] = df['distancia_planejada'].astype(str).str.replace(',', '.').astype(float)

        st.subheader("Dados Brutos")
        st.write(df)

        def faixa_horaria(hour):
            if 0 <= hour < 3:
                return '00:00 - 02:59'
            elif 3 <= hour < 6:
                return '03:00 - 05:59'
            elif 6 <= hour < 9:
                return '06:00 - 08:59'
            elif 9 <= hour < 12:
                return '09:00 - 11:59'
            elif 12 <= hour < 15:
                return '12:00 - 14:59'
            elif 15 <= hour < 18:
                return '15:00 - 17:59'
            elif 18 <= hour < 21:
                return '18:00 - 20:59'
            else:
                return '21:00 - 23:59'

        # Criar faixa horária
        df['Faixa Horária'] = df['Hora Início da viagem'].apply(lambda x: faixa_horaria(int(str(x)[:2])))

        if 'distancia_planejada' in df.columns and 'Serviço' in df.columns:
            # Agrupar distância planejada por Serviço e Faixa Horária
            df_grouped = df.pivot_table(
                index='Serviço',
                columns='Faixa Horária',
                values='distancia_planejada',
                aggfunc='sum',
                fill_value=0
            )

            st.subheader("Km Realizada por Faixa Horária")
            st.write(df_grouped)

            # Se a planilha de planejamento for carregada
            if plan_file is not None:
                try:
                    planejamento_df = pd.read_excel(plan_file)

                    st.subheader("Planejamento")
                    st.write(planejamento_df)

                    # Selecione apenas linhas do planejamento que coincidem com a data do realizado
                    data_realizada = df['Data Início da viagem'].unique()
                    if 'Data' in planejamento_df.columns:
                        planejamento_df['Data'] = pd.to_datetime(planejamento_df['Data'], errors='coerce').dt.date
                        planejamento_df = planejamento_df[planejamento_df['Data'].isin(data_realizada)]

                    # Garantir que ambos os dataframes têm os mesmos índices e colunas
                    comum_index = df_grouped.index.intersection(planejamento_df['Serviço'])
                    planejamento_df = planejamento_df.set_index('Serviço').loc[comum_index]
                    realizado_df = df_grouped.loc[comum_index]

                    comum_colunas = realizado_df.columns.intersection(planejamento_df.columns)
                    planejamento_df = planejamento_df[comum_colunas]
                    realizado_df = realizado_df[comum_colunas]

                    # Calcular percentual de cumprimento
                    percentual_df = (realizado_df / planejamento_df.replace(0, pd.NA)) * 100
                    percentual_df = percentual_df.round(1).fillna(0)

                    st.subheader("Percentual de Cumprimento (%)")
                    st.write(percentual_df)

                except Exception as e:
                    st.error(f"Erro ao ler o arquivo de planejamento: {e}")

    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada no arquivo.")
