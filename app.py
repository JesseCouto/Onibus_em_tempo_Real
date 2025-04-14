import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Dashboard Interativo - estilo Power BI")

uploaded_file = st.file_uploader("📁 Faça upload do seu arquivo CSV", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Formatar "distancia_planejada" para o padrão brasileiro
    if "distancia_planejada" in df.columns:
        try:
            df["distancia_planejada"] = df["distancia_planejada"].astype(float)
            df["distancia_planejada"] = df["distancia_planejada"].apply(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        except ValueError:
            st.warning("⚠️ A coluna 'distancia_planejada' contém valores que não podem ser convertidos para número.")

    st.subheader("📋 Dados brutos")
    st.dataframe(df)

    st.subheader("📈 Visualização de Gráficos")

    col1, col2 = st.columns(2)
    with col1:
        coluna_x = st.selectbox("Escolha a coluna para o eixo X:", df.columns)
    with col2:
        coluna_y = st.selectbox("Escolha a coluna para o eixo Y:", df.columns)

    if coluna_x and coluna_y:
        try:
            # Tenta converter a coluna Y para número, se necessário
            df[coluna_y] = pd.to_numeric(df[coluna_y].str.replace(".", "").str.replace(",", "."), errors='coerce')
            fig = px.bar(df, x=coluna_x, y=coluna_y, title=f"{coluna_y} por {coluna_x}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {e}")
