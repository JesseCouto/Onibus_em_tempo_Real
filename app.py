import pandas as pd
import streamlit as st
import re

# Exemplo de DataFrame (substitua pelo seu CSV real)
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

# Função para extrair a hora da string
def extrai_hora(horario_str):
    match = re.search(r'(\d{2}):\d{2}:\d{2}', horario_str)
    if match:
        return int(match.group(1))
    return None

# Aplicando a função
df['Hora'] = df['Início da viagem'].apply(extrai_hora)

# Definindo as faixas horárias
faixas = [
    (0, 2), (3, 5), (6, 8), (9, 11), (12, 14), (15, 17), (18, 20), (21, 23)
]
faixas_label = ['00:00 - 02:59', '03:00 - 05:59', '06:00 - 08:59', '09:00 - 11:59', '12:00 - 14:59', '15:00 - 17:59', '18:00 - 20:59', '21:00 - 23:59']

# Função para mapear a hora em uma faixa
def faixa_horaria(hora):
    for i, (inicio, fim) in enumerate(faixas):
        if inicio <= hora <= fim:
            return faixas_label[i]
    return None

# Aplicando a classificação por faixa
df['Faixa Horária'] = df['Hora'].apply(faixa_horaria)

# Tabela dinâmica: soma da distância por faixa e serviço
pivot_table = df.pivot_table(values='Distância Planejada', index='Serviço', columns='Faixa Horária', aggfunc='sum', fill_value=0)

# Adiciona a linha de totais por faixa
pivot_table.loc['Total'] = pivot_table.sum()

# Mostra os resultados
st.write("**Dados com Faixas Horárias**")
st.write(df)

st.write("**Soma de Km Planejado por Faixa Horária**")
st.write(pivot_table)
