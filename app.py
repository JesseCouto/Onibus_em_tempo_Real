# Verificação de ambiente apenas informativa sem encerrar execução
try:
    import streamlit as st
    import pandas as pd
    import zipfile
    import io
    import requests
    import pydeck as pdk
    from google.transit import gtfs_realtime_pb2
    import datetime
    import time
    import folium
    from streamlit_folium import st_folium
except ModuleNotFoundError as e:
    print(f"[Aviso] Módulo ausente: {e.name}")
    print("Este aplicativo requer os seguintes pacotes:")
    print("pip install streamlit pandas requests pydeck protobuf gtfs-realtime-bindings folium streamlit-folium")
    st = None

if st:
    st.set_page_config(page_title="GTFS Rio - Análise Completa", layout="wide", page_icon="🚌")

    GTFS_URL = "https://dados.mobilidade.rio/gis/gtfs.zip"
    GTFS_REALTIME_VP = "https://dados.mobilidade.rio/gps/gtfs-rt-vp"

    st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .block-container {
            padding-top: 2rem;
        }
        .stButton>button {
            color: white;
            background-color: #0d6efd;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
        }
        .stDownloadButton>button {
            background-color: #198754;
            color: white;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    @st.cache_data
    def carregar_dados_gtfs(url):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return None
            z = zipfile.ZipFile(io.BytesIO(response.content))
            dados = {name: pd.read_csv(z.open(name)) for name in z.namelist() if name.endswith('.txt')}
            return dados
        except Exception:
            return None

    @st.cache_data
    def carregar_dados_gtfs_manual(uploaded_file):
        try:
            z = zipfile.ZipFile(uploaded_file)
            dados = {name: pd.read_csv(z.open(name)) for name in z.namelist() if name.endswith('.txt')}
            return dados
        except Exception:
            st.error("Erro ao processar o arquivo GTFS enviado.")
            return None

    def carregar_dados_realtime():
        feed = gtfs_realtime_pb2.FeedMessage()
        try:
            response = requests.get(GTFS_REALTIME_VP)
            feed.ParseFromString(response.content)
            dados = []
            for entity in feed.entity:
                if entity.HasField("vehicle"):
                    info = entity.vehicle
                    dados.append({
                        "trip_id": info.trip.trip_id,
                        "route_id": info.trip.route_id,
                        "vehicle_id": info.vehicle.id,
                        "latitude": info.position.latitude,
                        "longitude": info.position.longitude,
                        "timestamp": datetime.datetime.fromtimestamp(info.timestamp).strftime("%H:%M:%S") if info.timestamp else "",
                    })
            return pd.DataFrame(dados)
        except:
            return pd.DataFrame([])

    st.title("🚌 GTFS Rio de Janeiro - Análise e Visualização de Linhas")

    gtfs = carregar_dados_gtfs(GTFS_URL)

    if not gtfs:
        st.warning("⚠️ Não foi possível carregar os dados automaticamente. Faça o upload manual do arquivo GTFS (.zip).")
        uploaded_file = st.file_uploader("📁 Faça o upload do GTFS.zip", type="zip")
        if uploaded_file:
            gtfs = carregar_dados_gtfs_manual(uploaded_file)
            if gtfs or st.query_params.get("ready") == ["1"]:
                st.success("✅ Arquivo GTFS carregado com sucesso!")
                st.experimental_set_query_params(ready="1")

    if gtfs:
        routes = gtfs["routes.txt"]
        trips = gtfs["trips.txt"]
        shapes = gtfs["shapes.txt"]
        stops = gtfs["stops.txt"]
        stop_times = gtfs["stop_times.txt"]

        trips_routes = trips.merge(routes, on="route_id")
        linhas = trips_routes[["route_id", "route_short_name", "route_long_name", "trip_id", "shape_id"]].drop_duplicates()
        linhas["linha_nome"] = linhas["route_short_name"].fillna('').astype(str) + " - " + linhas["route_long_name"].fillna('').astype(str)

        st.sidebar.title("🔍 Filtros de Busca")
        linhas_selecionadas = st.sidebar.multiselect("Selecione uma ou mais linhas de ônibus:", linhas["linha_nome"].unique())
        linhas_dados = linhas[linhas["linha_nome"].isin(linhas_selecionadas)]
        shapes_selecionados = shapes[shapes["shape_id"].isin(linhas_dados["shape_id"])]
        paradas_selecionadas = stop_times[stop_times["trip_id"].isin(linhas_dados["trip_id"])]
        paradas_viagem = paradas_selecionadas.merge(stops, on="stop_id")

        st.subheader("🛣️ Trajeto das Linhas Selecionadas")

        if shapes_selecionados.empty:
            st.warning("Nenhuma forma (shape) encontrada para as linhas selecionadas.")
            st.stop()

        mapa_folium = folium.Map(location=[-22.9068, -43.1729], zoom_start=12)

        for shape_id, shape_df in shapes_selecionados.groupby("shape_id"):
            pontos = shape_df.sort_values("shape_pt_sequence")[["shape_pt_lat", "shape_pt_lon"]].values.tolist()
            folium.PolyLine(pontos, color="blue", weight=4, opacity=0.7).add_to(mapa_folium)

        for _, parada in paradas_viagem.iterrows():
            folium.CircleMarker(
                location=[parada["stop_lat"], parada["stop_lon"]],
                radius=4,
                color="red",
                fill=True,
                fill_opacity=0.9,
                popup=parada["stop_name"]
            ).add_to(mapa_folium)

        realtime_data = carregar_dados_realtime()
        if not realtime_data.empty and "route_id" in realtime_data.columns:
            veiculos_linha = realtime_data[realtime_data["route_id"].isin(linhas_dados["route_id"])]
            for _, row in veiculos_linha.iterrows():
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    icon=folium.Icon(color="green", icon="bus", prefix="fa"),
                    popup=f"Veículo {row['vehicle_id']} - {row['timestamp']}"
                ).add_to(mapa_folium)

        st_folium(mapa_folium, width=1200, height=700)
