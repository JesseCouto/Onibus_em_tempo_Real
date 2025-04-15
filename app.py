import streamlit as st
import pandas as pd

st.title("Visualização de Dados: Realizado vs Planejado")

# Upload dos arquivos
st.sidebar.header("1. Carregar Dados Realizados (.CSV)")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=["csv"])

st.sidebar.header("2. Carregar Planejamento (.XLSX)")
plan_file = st.sidebar.file_uploader("Escolha um arquivo XLSX", type=["xlsx"])

def classificar_faixa_horaria(hora):
    if pd.isnull(hora):
        return None
    hora = hora.hour
    if 0 <= hora < 3:
        return '00:00 - 02:59'
    elif 3 <= hora < 6:
        return '03:00 - 05:59'
    elif 6 <= hora < 9:
        return '06:00 - 08:59'
    elif 9 <= hora < 12:
        return '09:00 - 11:59'
    elif 12 <= hora < 15:
        return '12:00 - 14:59'
    elif 15 <= hora < 18:
        return '15:00 - 17:59'
    elif 18 <= hora < 21:
        return '18:00 - 20:59'
    else:
        return '21:00 - 23:59'

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if 'Início da viagem' in df.columns:
        try:
            # Extrair data e hora separadamente
            df['Data Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2} de \w{3}\. de \d{4})')[0]
            df['Hora Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2}:\d{2}:\d{2})')[0]

            # Traduzir mês
            month_map = {
                'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04',
                'mai.': '05', 'jun.': '06', 'jul.': '07', 'ago.': '08',
                'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
            }

            df['Data Início da viagem'] = df['Data Início da viagem'].replace(month_map, regex=True)
            df['Data Início da viagem'] = df['Data Início da viagem'].str.replace(r' de ', '/', regex=True)
            df['Data Início da viagem'] = pd.to_datetime(df['Data Início da viagem'], format='%d/%m/%Y', errors='coerce').dt.date

            df['Hora Início da viagem'] = pd.to_datetime(df['Hora Início da viagem'], format='%H:%M:%S', errors='coerce')
            df['Faixa Horária'] = df['Hora Início da viagem'].apply(classificar_faixa_horaria)

            st.subheader("Dados Realizados Brutos")
            st.write(df)

            # Filtro por data específica
            data_base = pd.to_datetime("2025-04-13").date()
            df_filtrado = df[df['Data Início da viagem'] == data_base]

            if df_filtrado.empty:
                st.warning("Nenhum dado encontrado com a data 13/04/2025.")
            else:
                # Agrupamento por Serviço e Faixa Horária
                if 'distancia_planejada' in df_filtrado.columns and 'Serviço' in df_filtrado.columns:
                    df_filtrado['distancia_planejada'] = df_filtrado['distancia_planejada'].astype(str).str.replace(',', '.').astype(float)

                    realizado = df_filtrado.pivot_table(
                        index='Serviço',
                        columns='Faixa Horária',
                        values='distancia_planejada',
                        aggfunc='sum',
                        fill_value=0
                    )

                    st.subheader("Km Realizada por Faixa Horária (13/04/2025)")
                    st.write(realizado)

                    # Leitura do planejamento
                    if plan_file is not None:
                        try:
                            planejamento_df = pd.read_excel(plan_file)

                            # Garantir que todas as colunas numéricas estão como float
                            for col in planejamento_df.columns:
                                if col != 'Serviço':
                                    planejamento_df[col] = (
                                        planejamento_df[col]
                                        .astype(str)
                                        .str.replace(',', '.')
                                        .str.replace(' ', '')
                                        .astype(float)
                                    )

                            st.subheader("Planejamento")
                            st.write(planejamento_df)

                            # Preparar base de comparação
                            planejamento_df = planejamento_df.set_index('Serviço')
                            faixas_planejamento = planejamento_df.columns

                            # Garantir que as mesmas faixas existam no realizado
                            realizado = realizado.reindex(index=planejamento_df.index, columns=faixas_planejamento, fill_value=0)

                            # Calcular o percentual de cumprimento
                            percentual_df = (realizado / planejamento_df.replace(0, pd.NA)) * 100
                            percentual_df = percentual_df.fillna(0).round(1)

                            st.subheader("Percentual de Cumprimento (%) - 13/04/2025")
                            st.dataframe(percentual_df)

                        except Exception as e:
                            st.error(f"Erro ao ler ou processar o arquivo de planejamento: {e}")
                else:
                    st.warning("Colunas 'distancia_planejada' ou 'Serviço' ausentes.")
        except Exception as e:
            st.error(f"Erro ao processar os dados: {e}")
    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada no arquivo CSV.")
