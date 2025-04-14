import streamlit as st
import pandas as pd

# Título do aplicativo
st.title("Visualização de Dados CSV")

# Carregar arquivo CSV
st.sidebar.header("Carregar Dados CSV")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Ler os dados CSV
    df = pd.read_csv(uploaded_file)

    # Verificar se a coluna 'Início da viagem' está presente
    if 'Início da viagem' in df.columns:
        # Mapeamento de meses para substituir a abreviação pelo número
        month_map = {
            'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04',
            'mai.': '05', 'jun.': '06', 'jul.': '07', 'ago.': '08',
            'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
        }

        try:
            # Extrair a data no formato: "13 de jan. de 2025"
            df['Data Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2} de \w{3}\. de \d{4})')[0]
            
            # Substituir as abreviações dos meses para o formato numérico
            df['Data Início da viagem'] = df['Data Início da viagem'].replace(month_map, regex=True)

            # Ajustar o formato da data para dd/mm/yyyy
            df['Data Início da viagem'] = df['Data Início da viagem'].str.replace(r' de ', '/', regex=True)

            # Converter para o formato datetime com o padrão dd/mm/yyyy
            df['Data Início da viagem'] = pd.to_datetime(df['Data Início da viagem'], format='%d/%m/%Y', errors='coerce')

            # Remover a parte da hora da coluna 'Data Início da viagem'
            df['Data Início da viagem'] = df['Data Início da viagem'].dt.date

            # Extrair a hora da viagem
            df['Hora Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2}:\d{2}:\d{2})')[0]
            df['Hora Início da viagem'] = pd.to_datetime(df['Hora Início da viagem'], format='%H:%M:%S', errors='coerce').dt.time

            # Limpar valores nulos da coluna 'Data Início da viagem' e 'Hora Início da viagem'
            df = df.dropna(subset=['Data Início da viagem', 'Hora Início da viagem'])

        except Exception as e:
            st.error(f"Erro ao separar e converter os dados: {e}")
        
        # Substituir "." por "," na coluna 'distancia_planejada' (ajustando para numeral brasileiro)
        if 'distancia_planejada' in df.columns:
            df['distancia_planejada'] = df['distancia_planejada'].astype(str).str.replace('.', ',', regex=False)

        # Exibir a tabela de dados brutos
        st.subheader("Dados Brutos")
        st.write(df)

        # Mapeamento de faixas horárias
        def faixa_horaria(hour):
            if 0 <= hour < 3:
                return '00:00-02:59'
            elif 3 <= hour < 6:
                return '03:00-05:59'
            elif 6 <= hour < 9:
                return '06:00-08:59'
            elif 9 <= hour < 12:
                return '09:00-11:59'
            elif 12 <= hour < 15:
                return '12:00-14:59'
            elif 15 <= hour < 18:
                return '15:00-17:59'
            elif 18 <= hour < 21:
                return '18:00-20:59'
            else:
                return '21:00-23:59'

        # Aplicar a função para mapear as faixas horárias
        df['Faixa Horária'] = df['Hora Início da viagem'].apply(lambda x: faixa_horaria(int(str(x)[:2])))

        # Agrupar por "Serviço", "Faixa Horária" e somar a "distancia_planejada"
        if 'distancia_planejada' in df.columns and 'Serviço' in df.columns:
            df_grouped = df.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()

            # Exibir a tabela "Km Realizada por Faixa Horária"
            st.subheader("Km Realizada por Faixa Horária")
            st.write(df_grouped)

    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada no arquivo.")
