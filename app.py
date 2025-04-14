import streamlit as st
import pandas as pd

# Título do aplicativo
st.title("Visualização de Dados CSV")

# Carregar arquivo CSV
st.sidebar.header("Carregar Dados CSV")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Ler os dados CSV sem tentar converter a coluna 'Início da viagem' para datetime automaticamente
    df = pd.read_csv(uploaded_file)

    # Verificar se a coluna 'Início da viagem' está presente
    if 'Início da viagem' in df.columns:
        # Mostrar os primeiros valores da coluna 'Início da viagem' para diagnosticar
        st.subheader("Valores da coluna 'Início da viagem' (para diagnóstico)")
        st.write(df['Início da viagem'].head(20))  # Mostrar os 20 primeiros valores
        
        # Tentar converter a coluna 'Início da viagem' para datetime
        try:
            # Tentar diferentes formatos de hora
            df['Início da viagem'] = pd.to_datetime(df['Início da viagem'], errors='coerce', format='%H:%M:%S')

            # Caso o formato anterior não funcione, tentar com AM/PM
            if df['Início da viagem'].isnull().any():
                df['Início da viagem'] = pd.to_datetime(df['Início da viagem'], errors='coerce', format='%I:%M %p')

            # Caso ainda não tenha sido convertido, tentar com milissegundos
            if df['Início da viagem'].isnull().any():
                df['Início da viagem'] = pd.to_datetime(df['Início da viagem'], errors='coerce', format='%H:%M:%S.%f')

            # Verificar os valores que não puderam ser convertidos
            invalid_values = df[df['Início da viagem'].isnull()]['Início da viagem']
            
            if not invalid_values.empty:
                st.warning("Alguns valores na coluna 'Início da viagem' não puderam ser convertidos para data/hora. Veja abaixo os valores problemáticos:")
                st.write(invalid_values)

            # Limpar valores nulos da coluna 'Início da viagem'
            df = df.dropna(subset=['Início da viagem'])

        except Exception as e:
            st.error(f"Erro ao converter os dados de hora: {e}")
        
        # Substituir "." por "," na coluna 'distancia_planejada' (ajustando para numeral brasileiro)
        if 'distancia_planejada' in df.columns:
            df['distancia_planejada'] = df['distancia_planejada'].astype(str).str.replace('.', ',', regex=False)

        # Exibir a tabela de dados brutos
        st.subheader("Dados Brutos")
        st.write(df)

        # Garantir que 'Início da viagem' está no formato correto de hora
        df['Hora'] = df['Início da viagem'].dt.hour

        # Criar as faixas horárias
        bins = [0, 2, 5, 8, 11, 14, 17, 20, 23, 24]  # Intervalos de hora
        labels = ['00:00-02:59', '03:00-05:59', '06:00-08:59', '09:00-11:59', '12:00-14:59', '15:00-17:59', '18:00-20:59', '21:00-23:59']
        
        # Adicionar a coluna 'Faixa Horária' com as faixas baseadas no 'Hora'
        df['Faixa Horária'] = pd.cut(df['Hora'], bins=bins, labels=labels, right=False)

        # Calcular a soma da distância planejada por 'Serviço' e 'Faixa Horária'
        df_grouped = df.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()

        # Exibir a tabela "Km Realizada por Faixa Horária" abaixo de "Dados Brutos"
        st.subheader("Km Realizada por Faixa Horária")
        st.write(df_grouped)

    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada no arquivo.")
