import streamlit as st
import pandas as pd

st.title("Visualização e Comparação de Dados - Planejado x Realizado")

# Upload da planilha de viagens (realizado)
st.sidebar.header("Carregar Dados de Viagens (Realizado)")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV de viagens", type=["csv"])

# Upload da planilha de planejamento
st.sidebar.header("Carregar Planejamento (Planejado)")
uploaded_plan = st.sidebar.file_uploader("Escolha um arquivo CSV de planejamento", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if 'Início da viagem' in df.columns:
        month_map = {
            'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04',
            'mai.': '05', 'jun.': '06', 'jul.': '07', 'ago.': '08',
            'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
        }

        try:
            df['Data Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2} de \w{3}\. de \d{4})')[0]
            df['Data Início da viagem'] = df['Data Início da viagem'].replace(month_map, regex=True)
            df['Data Início da viagem'] = df['Data Início da viagem'].str.replace(r' de ', '/', regex=True)
            df['Data Início da viagem'] = pd.to_datetime(df['Data Início da viagem'], format='%d/%m/%Y', errors='coerce')
            df['Data Início da viagem'] = df['Data Início da viagem'].dt.date
            df['Hora Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2}:\d{2}:\d{2})')[0]
            df['Hora Início da viagem'] = pd.to_datetime(df['Hora Início da viagem'], format='%H:%M:%S', errors='coerce').dt.time
            df = df.dropna(subset=['Data Início da viagem', 'Hora Início da viagem'])
        except Exception as e:
            st.error(f"Erro ao processar datas e horas: {e}")
        
        if 'distancia_planejada' in df.columns:
            df['distancia_planejada'] = (
                df['distancia_planejada']
                .astype(str)
                .str.replace(',', '.', regex=False)
                .str.replace(' ', '')
            )
            df['distancia_planejada'] = pd.to_numeric(df['distancia_planejada'], errors='coerce')

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

        # Tabela com km realizado por Serviço e Faixa Horária
        if 'distancia_planejada' in df.columns and 'Serviço' in df.columns:
            realizado = df.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()
            realizado.rename(columns={'distancia_planejada': 'Km Realizado'}, inplace=True)

            st.subheader("Realizado por Serviço e Faixa Horária")
            st.write(realizado)

            # Se o planejamento foi carregado
            if uploaded_plan is not None:
                planejamento = pd.read_csv(uploaded_plan)

                # Supondo que o planejamento tem colunas: 'Serviço', 'Faixa Horária', 'Km Planejado'
                # Ajuste os nomes se forem diferentes
                planejamento.rename(columns=lambda x: x.strip(), inplace=True)
                
                comparativo = pd.merge(planejamento, realizado, on=['Serviço', 'Faixa Horária'], how='left')
                comparativo['Km Realizado'] = comparativo['Km Realizado'].fillna(0)

                # Cálculo do percentual de cumprimento
                comparativo['% Cumprimento'] = (comparativo['Km Realizado'] / comparativo['Km Planejado']) * 100
                comparativo['% Cumprimento'] = comparativo['% Cumprimento'].round(1)

                st.subheader("Comparativo Planejado x Realizado")
                st.write(comparativo)

            else:
                st.info("Carregue a planilha de planejamento para ver a comparação.")

    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada.")
