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
        agency = gtfs["agency.txt"]

        trips_routes = trips.merge(routes, on="route_id").merge(agency, on="agency_id", how="left")
        linhas = trips_routes[["route_id", "route_short_name", "route_long_name", "trip_id", "shape_id", "agency_name"]].drop_duplicates()
        linhas["linha_nome"] = linhas["route_short_name"].fillna('').astype(str) + " - " + linhas["route_long_name"].fillna('').astype(str) + " (" + linhas["agency_name"].fillna('Desconhecida') + ")"

        st.sidebar.title("🔍 Filtros de Busca")
        agencias_disponiveis = linhas["agency_name"].dropna().unique()
        if len(agencias_disponiveis) > 0:
            st.sidebar.markdown("**Operadoras encontradas:**")
            for ag in agencias_disponiveis:
                st.sidebar.markdown(f"- {ag}")

        linhas_selecionadas = st.sidebar.multiselect("Selecione uma ou mais linhas de ônibus:", linhas["linha_nome"].unique())
        linhas_dados = linhas[linhas["linha_nome"].isin(linhas_selecionadas)]
        shapes_selecionados = shapes[shapes["shape_id"].isin(linhas_dados["shape_id"])]
        paradas_selecionadas = stop_times[stop_times["trip_id"].isin(linhas_dados["trip_id"])]
        paradas_viagem = paradas_selecionadas.merge(stops, on="stop_id")

        if len(linhas_selecionadas) == 1:
            operadora = linhas_dados.iloc[0]["agency_name"]
            st.markdown(f"### 🏢 Operadora responsável: **{operadora}**")

        st.subheader("🛣️ Trajeto das Linhas Selecionadas")

        if shapes_selecionados.empty:
            st.warning("Nenhuma forma (shape) encontrada para as linhas selecionadas.")
            st.stop()

        mapa_folium = folium.Map(location=[-22.9068, -43.1729], zoom_start=12)

        cores_operadoras = {}
        cores_base = ["red", "blue", "green", "orange", "purple", "darkred", "cadetblue", "black"]
        for i, ag in enumerate(linhas_dados["agency_name"].unique()):
            cores_operadoras[ag] = cores_base[i % len(cores_base)]

        for shape_id, shape_df in shapes_selecionados.groupby("shape_id"):
            shape_df = shape_df.sort_values("shape_pt_sequence")
            pontos = list(zip(shape_df["shape_pt_lat"], shape_df["shape_pt_lon"]))
            ag_name = linhas_dados[linhas_dados["shape_id"] == shape_id]["agency_name"].values[0]
            cor = cores_operadoras.get(ag_name, "blue")
            if len(pontos) >= 2:
                folium.PolyLine(pontos, color=cor, weight=4, opacity=0.7, tooltip=ag_name).add_to(mapa_folium)

        for _, parada in paradas_viagem.iterrows():
            folium.CircleMarker(
                location=(parada["stop_lat"], parada["stop_lon"]),
                radius=4,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.8,
                popup=parada["stop_name"]
            ).add_to(mapa_folium)

        mostrar_legenda = st.checkbox("📘 Mostrar legenda de cores por operadora", value=True)
        if mostrar_legenda:
            legenda_html = """<div style='position: absolute; 
                                top: 20px; right: 20px; width: 220px; height: auto; 
                                z-index:9999; font-size:13px; background:rgba(255,255,255,0.9); padding: 10px; 
                                border:1px solid #ccc; border-radius:8px; box-shadow: 2px 2px 6px rgba(0,0,0,0.1);'>
                                <b style='font-size:14px;'>Operadoras e cores:</b><br>"""
            for ag, cor in cores_operadoras.items():
                legenda_html += f"<div style='margin-bottom:4px;'><i style='background:{cor};width:12px;height:12px;display:inline-block;margin-right:6px;vertical-align:middle;border-radius:50%;'></i> {ag}</div>"
            legenda_html += "</div>"
            mapa_folium.get_root().html.add_child(folium.Element(legenda_html))

        st_data = st_folium(mapa_folium, width=1000, height=600)

        st.subheader("📍 Veículos em Tempo Real")
        df_realtime = carregar_dados_realtime()

        if df_realtime.empty:
            st.info("Nenhuma posição de veículo em tempo real disponível no momento.")
        else:
            df_realtime_filtrado = df_realtime[df_realtime["route_id"].isin(linhas_dados["route_id"])]
            if not df_realtime_filtrado.empty:
                mapa_veiculos = folium.Map(location=[-22.9068, -43.1729], zoom_start=12)
                for _, v in df_realtime_filtrado.iterrows():
                    folium.Marker(
                        location=(v["latitude"], v["longitude"]),
                        popup=f"Linha: {v['route_id']} | Veículo: {v['vehicle_id']} | Horário: {v['timestamp']}",
                        icon=folium.Icon(color="green", icon="bus", prefix="fa")
                    ).add_to(mapa_veiculos)
                st_folium(mapa_veiculos, width=1000, height=600)
            else:
                st.info("Nenhum veículo encontrado para as linhas selecionadas.")
