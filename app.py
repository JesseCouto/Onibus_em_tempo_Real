import pandas as pd
import streamlit as st

# Exemplo de DataFrame (suponha que você tenha seus dados aqui)
data = {
    'Serviço': [1, 1, 1, 2, 2, 2, 3, 3, 3],
    'Início da viagem': [
        '13 de abr. de 2025, 01:23:45', '13 de abr. de 2025, 04:15:00', '13 de abr. de 2025, 07:30:00',
        '13 de abr. de 2025, 02:00:00', '13 de abr. de 2025, 08:45:00', '13 de abr. de 2025, 11:20:00',
        '13 de abr. de 2025, 03:10:00', '13 de abr. de 2025, 15:50:00', '13 de abr. de 2025, 18:25:00'
    ],
    'Distância Planejada': [150.00, 180.00, 220.00, 160.00, 190.00, 100.00, 130.00, 220.00, 210.00]
}

df = pd.DataFrame(data)

# Função para converter a data corretamente
def converte_data(data_str):
    meses = {
        'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04', 'mai.': '05', 'jun.': '06',
        'jul.': '07', 'ago.': '08', 'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
    }
    for mes_abreviado, mes_numero in meses.items():
        if mes_abreviado in data_str:
            data_str = data_str.replace(mes_abreviado, mes_numero)
            break
    return pd.to_datetime(data_str, format='%d/%m/%Y, %H:%M:%S')

# Aplicando a conversão da data na coluna 'Início da viagem'
df['Início da viagem'] = df['Início da viagem'].apply(converte_data)

# Separando a data e hora
df['Data Início da viagem'] = df['Início da viagem'].dt.date
df['Hora Início da viagem'] = df['Início da viagem'].dt.time

# Definindo as faixas horárias
faixas = [
    (0, 2), (3, 5), (6, 8), (9, 11), (12, 14), (15, 17), (18, 20), (21, 23)
]
faixas_label = ['00:00 - 02:59', '03:00 - 05:59', '06:00 - 08:59', '09:00 - 11:59', '12:00 - 14:59', '15:00 - 17:59', '18:00 - 20:59', '21:00 - 23:59']

# Adicionando coluna de faixa horária
def faixa_horaria(hora):
    for i, (inicio, fim) in enumerate(faixas):
        if inicio <= hora <= fim:
            return faixas_label[i]
    return None

df['Faixa Horária'] = df['Hora Início da viagem'].apply(lambda x: faixa_horaria(x.hour))

# Criando a tabela de soma por faixa horária e serviço
pivot_table = df.pivot_table(values='Distância Planejada', index='Serviço', columns='Faixa Horária', aggfunc='sum', fill_value=0)

# Adicionando uma linha total para cada faixa horária
pivot_table.loc['Total'] = pivot_table.sum()

# Exibindo os resultados
st.write("**Dados Brutos**")
st.write(df)

st.write("**Km Realizada por Faixa Horária**")
st.write(pivot_table)
