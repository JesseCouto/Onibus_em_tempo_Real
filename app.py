import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Dashboard Interativo - estilo Power BI")

uploaded_file = st.file_uploader("📁 Faça upload do seu arquivo CSV", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 🟡 Formatar distancia_planejada para o formato brasileiro
    if "distancia_planejada" in df.columns:
        try:
            df["distancia_planejada"] = df["distancia_planejada"].astype(float)
            df["distancia_planejada"] = df["distancia_planejada"].apply(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        except ValueError:
            st.warning("⚠️ A coluna 'distancia_planejada' contém valores não numéricos.")

    st.subheader("📋 Dados brutos")
    st.dataframe(df)

    # 🟠 Função para calcular total de distância planejada e realizada por serviço em faixas horárias específicas
    if "servico" in df.columns and "data_hora_viagem" in df.columns:
        st.subheader("📊 Total de Distância Planejada e Realizada por Serviço nas Faixas Horárias")

        # Garantir os tipos corretos
        df["data_hora_viagem"] = pd.to_datetime(df["data_hora_viagem"])
        df["distancia_realizada"] = pd.to_numeric(df["distancia_realizada"], errors="coerce")
        df["distancia_planejada"] = pd.to_numeric(df["distancia_planejada"], errors="coerce")

        # Função para classificar faixa horária
        def classificar_faixa(hora):
            if hora < 3:
                return "00:00 - 02:59"
            elif hora < 6:
                return "03:00 - 05:59"
            elif hora < 9:
                return "06:00 - 08:59"
            elif hora < 12:
                return "09:00 - 11:59"
            elif hora < 15:
                return "12:00 - 14:59"
            elif hora < 18:
                return "15:00 - 17:59"
            elif hora < 21:
                return "18:00 - 20:59"
            else:
                return "21:00 - 23:59"

        # Adicionar coluna de faixa horária
        df["faixa_fixa"] = df["data_hora_viagem"].dt.hour.apply(classificar_faixa)

        # Agrupar por serviço e faixa, somando as distâncias planejada e realizada
        distancia_por_servico = df.groupby(["servico", "faixa_fixa"])["distancia_planejada", "distancia_realizada"].sum().reset_index()

        # Exibir a tabela com total de distância planejada e realizada por serviço e faixa horária
        tabela_distancia = distancia_por_servico.pivot(index="servico", columns="faixa_fixa", values=["distancia_planejada", "distancia_realizada"]).fillna(0)

        # Formatar valores para string com vírgula
        tabela_formatada = tabela_distancia.applymap(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(tabela_formatada, use_container_width=True)

        # Calcular somatório por serviço
        resumo_distancia = distancia_por_servico.groupby("servico")[["distancia_planejada", "distancia_realizada"]].sum()

        # Exibir resumo do somatório
        st.subheader("📊 Resumo de Distância Planejada e Realizada por Serviço")
        
        # Formatar valores para string com vírgula
        resumo_formatado = resumo_distancia.applymap(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(resumo_formatado, use_container_width=True)

    # 🔵 Agrupamento por faixa de 3 horas automáticas
    if "data_hora_viagem" in df.columns and "distancia_realizada" in df.columns:
        try:
            df["data_hora_viagem"] = pd.to_datetime(df["data_hora_viagem"])
            df["distancia_realizada"] = pd.to_numeric(df["distancia_realizada"], errors="coerce")
            df["faixa_3h"] = df["data_hora_viagem"].dt.floor("3H")

            soma_faixas = df.groupby("faixa_3h")["distancia_realizada"].sum().reset_index()

            st.subheader("🕒 Distância Realizada por Faixa de 3 Horas (automática)")

            # 🔸 Exibir resumo textual por faixa de horário
            for _, row in soma_faixas.iterrows():
                hora = row["faixa_3h"].strftime("%H:%M")
                distancia = f"{row['distancia_realizada']:.2f}".replace(".", ",")
                st.markdown(f"- 🕓 **{hora}** → **{distancia} km**")

            # 🔸 Gráfico de barras
            fig = px.bar(soma_faixas, x="faixa_3h", y="distancia_realizada",
                         title="Distância Realizada por Faixa de 3h")
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.warning(f"Erro ao processar faixas de horário: {e}")

    # 🟠 Distância por SERVIÇO em faixas fixas de 3h
    if "servico" in df.columns and "data_hora_viagem" in df.columns and "distancia_realizada" in df.columns:
        st.subheader("📊 Distância Realizada por Serviço em Faixas de 3 Horas (fixas)")

        # Garantir os tipos corretos
        df["data_hora_viagem"] = pd.to_datetime(df["data_hora_viagem"])
        df["distancia_realizada"] = pd.to_numeric(df["distancia_realizada"], errors="coerce")

        # Criar coluna de período fixo
        def classificar_faixa(hora):
            if hora < 3:
                return "00:00 - 02:59"
            elif hora < 6:
                return "03:00 - 05:59"
            elif hora < 9:
                return "06:00 - 08:59"
            elif hora < 12:
                return "09:00 - 11:59"
            elif hora < 15:
                return "12:00 - 14:59"
            elif hora < 18:
                return "15:00 - 17:59"
            elif hora < 21:
                return "18:00 - 20:59"
            else:
                return "21:00 - 23:59"

        df["faixa_fixa"] = df["data_hora_viagem"].dt.hour.apply(classificar_faixa)

        # Agrupar por serviço e faixa
        resumo = df.groupby(["servico", "faixa_fixa"])["distancia_realizada"].sum().reset_index()

        # Pivotar para formato de tabela dinâmica
        tabela_pivot = resumo.pivot(index="servico", columns="faixa_fixa", values="distancia_realizada").fillna(0)

        # Formatar valores para string com vírgula
        tabela_formatada = tabela_pivot.applymap(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(tabela_formatada, use_container_width=True)
