import streamlit as st
# (restante do código copiado diretamente do canvas atual omitido para brevidade)
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=shape_data["shape_pt_lat"].mean(),
        longitude=shape_data["shape_pt_lon"].mean(),
        zoom=12,
        pitch=0,
    ),
    layers=camadas_mapa,
    tooltip={"text": "Veículo {vehicle_id}
    \\nHorário: {timestamp}"}
))

