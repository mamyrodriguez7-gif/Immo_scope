import streamlit as st
from immo_scope.visualizer import Visualizer
from immo_scope.map_visualizer import MapVisualizer

st.set_page_config(
    page_title="Immo_Scope Dashboard",
    page_icon="🏡",
    layout="wide"
)

st.title("🏡 Immo_Scope – Analyse du marché immobilier français")
st.markdown("Visualisations interactives et carte des prix DVF.")

viz = Visualizer()
map_viz = MapVisualizer()

menu = st.sidebar.selectbox(
    "📌 Navigation",
    ["Accueil", "Visualisations", "Carte interactive", "Dashboard complet"]
)

if menu == "Accueil":
    st.header("Bienvenue 👋")
    st.write("""
    Ce dashboard présente :
    - des visualisations DVF,
    - une carte interactive,
    - un tableau de bord global.
    """)

elif menu == "Visualisations":
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Types de biens", "Distribution des prix", "Top communes", "Surface vs Prix"]
    )

    with tab1:
        st.plotly_chart(viz.create_property_types_chart(), use_container_width=True)

    with tab2:
        st.plotly_chart(viz.create_price_distribution(), use_container_width=True)

    with tab3:
        st.plotly_chart(viz.create_top_cities_chart(), use_container_width=True)

    with tab4:
        st.plotly_chart(viz.create_price_vs_surface(), use_container_width=True)

elif menu == "Carte interactive":
    st.plotly_chart(map_viz.create_price_map(), use_container_width=True)

elif menu == "Dashboard complet":
    st.plotly_chart(viz.create_dashboard_overview(), use_container_width=True)
