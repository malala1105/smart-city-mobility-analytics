import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)

from agregations.queries import (
    trafic_par_heure,
    impact_meteo,
    stats_par_vehicule,
    vehicules_par_type_zone,
)

# CONFIG
st.set_page_config(page_title="Dashboard · MobiTana", page_icon="📊", layout="wide")

# PALETTE PASTEL
PASTEL = [
    "#A8D8EA", "#FFCBA4", "#B5EAD7", "#FFD6D6",
    "#C9C0E3", "#FFF1A8", "#F4C2C2"
]

METEO_COLORS = {
    "sunny":  "#FFF1A8",
    "rain":   "#A8D8EA",
    "cloudy": "#C9C0E3",
}

# STYLE
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .section-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.3rem;
        color: #0f1923;
        margin-bottom: 0.2rem;
    }
    .section-desc {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-bottom: 1rem;
    }
    .divider {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("## Dashboard")
st.markdown("Vue d'ensemble des flux de mobilité à Antananarivo.")
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# 1. TRAFIC PAR HEURE
st.markdown('<div class="section-title">Trafic par heure</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Nombre de trajets enregistrés pour chaque heure de la journée.</div>', unsafe_allow_html=True)

data_heure = trafic_par_heure()
df_heure = pd.DataFrame(
    list(data_heure.items()), columns=["Heure", "Trajets"]
)

fig1 = px.line(
    df_heure, x="Heure", y="Trajets",
    markers=True,
    color_discrete_sequence=["#A8D8EA"]
)
fig1.update_traces(line=dict(width=2.5), marker=dict(size=7))
fig1.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="DM Sans", margin=dict(t=10, b=10),
    xaxis=dict(dtick=1, gridcolor="#f3f4f6"),
    yaxis=dict(gridcolor="#f3f4f6"),
)
st.plotly_chart(fig1, use_container_width=True, key="fig_heure")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# 2. VÉHICULES PAR TYPE DE ZONE
st.markdown('<div class="section-title">Véhicules par type de zone</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Quel véhicule domine dans chaque type de quartier ?</div>', unsafe_allow_html=True)
with st.expander("Voir la liste des quartiers par type"):
    st.markdown("""
    | Type | Quartiers |
    |---|---|
    | Résidentiel | 67Ha, Ivandry, Ambohijatovo, Faravohitra, Ambanidia, Ankadifotsy, Itaosy |
    | Business | Analakely, Ankorondrano, Andraharo, Tsaralalàna, Isotry, Tanjombato |
    | Éducation | Ankatso, Mahamasina |
    """)

data_vz = vehicules_par_type_zone()
rows = []
for zone_type, vehicules in data_vz.items():
    for vehicule, count in vehicules.items():
        rows.append({"Type de zone": zone_type, "Vehicule": vehicule, "Trajets": count})
df_vz = pd.DataFrame(rows)
df_vz = df_vz[df_vz["Type de zone"] != "transport"]

fig2 = px.bar(
    df_vz, x="Type de zone", y="Trajets",
    color="Vehicule", barmode="stack",
    color_discrete_sequence=PASTEL,
    labels={"Type de zone": "Type de zone", "Trajets": "Nombre de trajets"}
)
fig2.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="DM Sans", margin=dict(t=10, b=10),
    xaxis=dict(gridcolor="#f3f4f6"),
    yaxis=dict(gridcolor="#f3f4f6"),
)
st.plotly_chart(fig2, use_container_width=True, key="fig_zones_vehicules")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# 3. IMPACT MÉTÉO
st.markdown('<div class="section-title">Impact météo sur la durée des trajets</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Durée moyenne des trajets (en minutes) selon la condition météo.</div>', unsafe_allow_html=True)

data_meteo = impact_meteo()
df_meteo = pd.DataFrame(
    [(k, v["duree_moyenne"]) for k, v in data_meteo.items()],
    columns=["Meteo", "Duree_moyenne"]
)

fig3 = px.bar(
    df_meteo, x="Meteo", y="Duree_moyenne",
    color="Meteo",
    color_discrete_map=METEO_COLORS,
    labels={"Meteo": "Météo", "Duree_moyenne": "Durée moyenne (min)"}
)
fig3.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="DM Sans", showlegend=False,
    margin=dict(t=10, b=10),
    xaxis=dict(gridcolor="#f3f4f6"),
    yaxis=dict(gridcolor="#f3f4f6"),
)
st.plotly_chart(fig3, use_container_width=True, key="fig_meteo")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# 4. STATS PAR VÉHICULE
st.markdown('<div class="section-title">Distance et durée moyennes par véhicule</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Comparaison des profils de déplacement selon le type de véhicule.</div>', unsafe_allow_html=True)

data_vehicule = stats_par_vehicule()
df_v = pd.DataFrame([
    {
        "Vehicule": k,
        "Distance": v["distance_moyenne"],
        "Duree": v["duree_moyenne"],
        "Vitesse": v["vitesse_moyenne"],
        "Trajets": v["nb_trajets"],
    }
    for k, v in data_vehicule.items()
])

col1, col2 = st.columns(2)

with col1:
    st.caption("Distance moyenne (km)")
    fig4a = px.bar(
        df_v, x="Vehicule", y="Distance",
        color="Vehicule", color_discrete_sequence=PASTEL,
        labels={"Vehicule": "Véhicule", "Distance": "Distance moy. (km)"}
    )
    fig4a.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="DM Sans", showlegend=False,
        margin=dict(t=10, b=10),
        xaxis=dict(gridcolor="#f3f4f6"),
        yaxis=dict(gridcolor="#f3f4f6"),
    )
    st.plotly_chart(fig4a, use_container_width=True, key="fig_vehicule_dist")

with col2:
    st.caption("Durée moyenne (min)")
    fig4b = px.bar(
        df_v, x="Vehicule", y="Duree",
        color="Vehicule", color_discrete_sequence=PASTEL,
        labels={"Vehicule": "Véhicule", "Duree": "Durée moy. (min)"}
    )
    fig4b.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="DM Sans", showlegend=False,
        margin=dict(t=10, b=10),
        xaxis=dict(gridcolor="#f3f4f6"),
        yaxis=dict(gridcolor="#f3f4f6"),
    )
    st.plotly_chart(fig4b, use_container_width=True, key="fig_vehicule_duree")

st.markdown("---")
st.caption("Détail complet")
st.dataframe(df_v, use_container_width=True)