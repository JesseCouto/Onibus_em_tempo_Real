import streamlit as st
import pandas as pd

st.title("Comparação de Planejado vs Realizado por Faixa Horária")

# Upload dos arquivos
uploaded_csv = st.file_uploader("Envie o arquivo REALIZADO (.csv)", type="csv")
uploaded_xlsx = st.file_uploader("Envie o arquivo PLANEJADO (.xlsx)", type="xlsx")

# Função para determinar a faixa horária
def faixa_horaria(horario):
    hora = horario.hour
    if 0 <= hora < 3:
        return "00h-03h"
    elif 3 <= hora < 6:
        return "03h-06h"
    elif 6 <= hora < 9:
        return "06h-09h"
    elif 9 <= hora < 12:
        return "09h-12h"
    elif 12 <= hora < 15:
        return "12h-15h"
    elif 15 <= hora < 18:
        return "15h-18h"
    elif 18 <= hora < 21:
        return "18h-21h"
    else:
        return "21h-24h"

# Processamento dos arquivos
if uploaded_csv:
    try:
        # Leitura do arquivo CSV (REALIZADO)
        df_realizado = pd.read_csv(uploaded_csv, sep=';', encoding='utf-8', header=0)

        # Exibe as colunas lidas do CSV para debug
        st.subheader("Colunas encontradas no arquivo .csv:")
        st.write(df_realizado.columns.tolist())

        # Verificando se há uma linha extra de cabeçalho e ajustando
        if len(df_realizado.columns) == 1 and 'mapa,Serviço,Vista,Sentido,distancia_planejada,Início da viagem,Fim da viagem,Veículo,Planejamento' in df_realizado.columns:
            # Ajustando as colunas manualmente
            df_realizado.columns = ['mapa', 'Serviço', 'Vista', 'Sentido', 'distancia_planejada', 'Início da viagem', 'Fim da viagem', 'Veículo', 'Planejamento']
            # Recarregando os dados corretamente
            df_realizado = pd.read_csv(uploaded_csv, sep=';', encoding='utf-8', header=1)

        # Tenta acessar a coluna 'Início da viagem' no arquivo CSV
        if 'Início da viagem' not in df_realizado.columns:
            st.error("A coluna 'Início da viagem' não foi encontrada no arquivo CSV. Verifique o nome exato.")
        else:
            # Processando o CSV
            df_realizado['Início da viagem'] = pd.to_datetime(df_realizado['Início da viagem'], dayfirst=True)
            df_realizado['Data'] = df_realizado['Início da viagem'].dt.date
            df_realizado['Faixa Horária'] = df_realizado['Início da viagem'].dt.time.apply(faixa_horaria)

            # Definindo a data de filtro
            data_filtro = pd.to_datetime("13/04/2025", dayfirst=True).date()
            df_realizado = df_realizado[df_realizado['Data'] == data_filtro]

            # Calculando o total de km por faixa horária
            km_realizado_por_faixa = df_realizado.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().unstack().fillna(0)
            st.subheader("Km Realizada por Faixa Horária (13/04/2025)")
            st.dataframe(km_realizado_por_faixa)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo CSV: {e}")

# Processamento do arquivo .xlsx (Planejado)
if uploaded_xlsx:
    try:
        # Leitura do arquivo XLSX (PLANEJADO)
        df_planejado = pd.read_excel(uploaded_xlsx)

        # Exibe as colunas lidas do XLSX para debug
        st.subheader("Colunas encontradas no arquivo .xlsx:")
        st.write(df_planejado.columns.tolist())

        # Processando o arquivo planejado
        df_planejado['Dia'] = pd.to_datetime(df_planejado['Dia'], dayfirst=True)
        df_planejado = df_planejado[df_planejado['Dia'].dt.date == data_filtro]

        # Definindo as colunas de faixas horárias para o planejamento
        colunas_faixas_planejado = {
            '00h-03h': 'Quilometragem entre 00h e 03h',
            '03h-06h': 'Quilometragem entre 03h e 06h',
            '06h-09h': 'Quilometragem entre 06h e 09h',
            '09h-12h': 'Quilometragem entre 09h e 12h',
            '12h-15h': 'Quilometragem entre 12h e 15h',
            '15h-18h': 'Quilometragem entre 15h e 18h',
            '18h-21h': 'Quilometragem entre 18h e 21h',
            '21h-24h': 'Quilometragem entre 21h e 24h'
        }

        # Agrupando o planejamento por serviço e somando as quilometragens
        df_planejado_agg = df_planejado.groupby('Serviço').agg({v: 'sum' for v in colunas_faixas_planejado.values()})
        df_planejado_agg.rename(columns={v: k for k, v in colunas_faixas_planejado.items()}, inplace=True)

        st.subheader("Km Planejada por Faixa Horária (13/04/2025)")
        st.dataframe(df_planejado_agg)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo XLSX: {e}")

# Caso ambos os arquivos tenham sido carregados, comparar os dados
if uploaded_csv and uploaded_xlsx:
    try:
        # Comparação percentual
        percentual_cumprimento = (km_realizado_por_faixa / df_planejado_agg) * 100
        percentual_cumprimento = percentual_cumprimento.fillna(0).round(1)

        st.subheader("Percentual de Cumprimento (%) por Faixa Horária")
        st.dataframe(percentual_cumprimento)

    except Exception as e:
        st.error(f"Erro ao comparar os arquivos: {e}")
