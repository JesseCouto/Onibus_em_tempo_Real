import streamlit as st
import pandas as pd
import zipfile
import io
import requests
import pydeck as pdk
from google.transit import gtfs_realtime_pb2
import datetime
import time

st.set_page_config(page_title="GTFS Rio - Análise Completa", layout="wide", page_icon="🚌")

GTFS_URL = "https://dados.mobilidade.rio/gis/gtfs.zip"
GTFS_REALTIME_VP = "https://dados.mobilidade.rio/gps/gtfs-rt-vp"

# Estilo customizado
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

    shape_data = shapes_selecionados.sort_values("shape_pt_sequence")
    realtime_data = carregar_dados_realtime()
    veiculos_linha = realtime_data[realtime_data["route_id"].isin(linhas_dados["route_id"])]

    camadas_mapa = [
        pdk.Layer(
            "PathLayer",
            data=[{"path": shape_data[["shape_pt_lon", "shape_pt_lat"]].values.tolist()}],
            get_path="path",
            get_color=[0, 100, 250],
            width_scale=5,
            width_min_pixels=3,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            data=paradas_viagem,
            get_position='[stop_lon, stop_lat]',
            get_radius=30,
            get_fill_color=[255, 0, 0, 160],
        )
    ]

    if not veiculos_linha.empty:
        camadas_mapa.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=veiculos_linha,
                get_position='[longitude, latitude]',
                get_radius=50,
                get_fill_color=[0, 255, 0, 180],
                pickable=True,
            )
        )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=shape_data["shape_pt_lat"].mean(),
            longitude=shape_data["shape_pt_lon"].mean(),
            zoom=12,
            pitch=0,
        ),
        layers=camadas_mapa,
        tooltip={"text": "Veículo {vehicle_id}\nHorário: {timestamp}"}
    ))

    st.markdown("### 📅 Horários da Viagem")
    st.dataframe(paradas_viagem[["stop_name", "arrival_time", "departure_time"]], use_container_width=True)

    st.markdown("### 📄 Detalhes da Linha")
    st.dataframe(linhas_dados, use_container_width=True)

    with st.expander("📋 Ver Todas as Linhas"):
        st.dataframe(linhas.sort_values("linha_nome"), use_container_width=True)

    with st.expander("⬇️ Exportar Dados"):
        csv = paradas_viagem.to_csv(index=False).encode("utf-8")
        nome_arquivo = "paradas_multilinhas.csv"
        st.download_button("💾 Baixar CSV de paradas", csv, nome_arquivo, "text/csv")
else:
    st.error("❌ Não foi possível carregar dados do GTFS.")
