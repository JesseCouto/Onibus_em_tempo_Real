import streamlit as st
import pandas as pd

st.title("Visualização de Dados CSV com Comparativo de Planejado x Realizado")

# Carregamento do CSV
st.sidebar.header("Carregar Dados CSV Realizado")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=["csv"])

# Carregamento da planilha de planejamento
st.sidebar.header("Carregar Planilha de Planejamento (.xlsx)")
uploaded_plan = st.sidebar.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if 'Início da viagem' in df.columns:
        # Mapeamento de meses para substituir a abreviação pelo número
        month_map = {
            'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04',
            'mai.': '05', 'jun.': '06', 'jul.': '07', 'ago.': '08',
            'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
        }

        try:
            df['Data Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2} de \w{3}\. de \d{4})')[0]
            df['Data Início da viagem'] = df['Data Início da viagem'].replace(month_map, regex=True)
            df['Data Início da viagem'] = df['Data Início da viagem'].str.replace(r' de ', '/', regex=True)
            df['Data Início da viagem'] = pd.to_datetime(df['Data Início da viagem'], format='%d/%m/%Y', errors='coerce').dt.date

            df['Hora Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2}:\d{2}:\d{2})')[0]
            df['Hora Início da viagem'] = pd.to_datetime(df['Hora Início da viagem'], format='%H:%M:%S', errors='coerce').dt.time

            df = df.dropna(subset=['Data Início da viagem', 'Hora Início da viagem'])

        except Exception as e:
            st.error(f"Erro ao processar datas e horas: {e}")

        if 'distancia_planejada' in df.columns:
            df['distancia_planejada'] = df['distancia_planejada'].astype(str).str.replace('.', ',', regex=False)
            df['distancia_planejada'] = df['distancia_planejada'].str.replace(',', '.').astype(float)

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

        df['Faixa Horária'] = df['Hora Início da viagem'].apply(lambda x: faixa_horaria(int(str(x)[:2])))

        # Selecionar a data para comparação, se a planilha for carregada
        data_planejada = None
        if uploaded_plan is not None:
            try:
                plan_df = pd.read_excel(uploaded_plan)
                if 'Data' in plan_df.columns:
                    plan_df['Data'] = pd.to_datetime(plan_df['Data']).dt.date
                    data_options = plan_df['Data'].dropna().unique()
                    data_planejada = st.sidebar.selectbox("Escolha a Data para Comparação", sorted(data_options))
            except Exception as e:
                st.error(f"Erro ao ler o arquivo de planejamento: {e}")

        # Filtrar a data selecionada no realizado
        if data_planejada:
            df = df[df['Data Início da viagem'] == data_planejada]

        # Agrupar por serviço e faixa
        if 'distancia_planejada' in df.columns and 'Serviço' in df.columns:
            realizado_grouped = df.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()
            realizado_grouped.rename(columns={'distancia_planejada': 'Realizado'}, inplace=True)

            if uploaded_plan is not None and 'Serviço' in plan_df.columns and 'Faixa Horária' in plan_df.columns and 'Planejado' in plan_df.columns:
                comparativo = pd.merge(plan_df, realizado_grouped, how='left', on=['Serviço', 'Faixa Horária'])
                comparativo['Realizado'] = comparativo['Realizado'].fillna(0)
                comparativo['Percentual de Cumprimento (%)'] = ((comparativo['Realizado'] / comparativo['Planejado']) * 100).round(2)
                comparativo = comparativo[comparativo['Data'] == data_planejada]

                st.subheader("Comparativo Planejado x Realizado")
                st.write(comparativo)
            else:
                st.warning("A planilha de planejamento está incompleta ou não foi carregada corretamente.")

        else:
            st.warning("Colunas necessárias ausentes no arquivo de realizado.")

    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada no CSV.")
