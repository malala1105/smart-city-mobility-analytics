import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)

from agregations.queries import (
    trafic_par_heure,
    zones_plus_chargees,
    stats_par_vehicule,
    impact_meteo,
)

# CONFIG
st.set_page_config(page_title="Exploration · MobiTana", page_icon="🔍", layout="wide")

# PALETTE
PASTEL = ["#A8D8EA", "#FFCBA4", "#B5EAD7", "#FFD6D6", "#C9C0E3", "#FFF1A8", "#F4C2C2"]
METEO_COLORS = {"sunny": "#FFF1A8", "rain": "#A8D8EA", "cloudy": "#C9C0E3"}

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
    .question {
        font-size: 1rem;
        color: #3b5bdb;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .divider { border: none; border-top: 1px solid #e5e7eb; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("## Exploration")
st.markdown("Sélectionne un filtre dans la sidebar et observe son impact sur les flux.")
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# SIDEBAR — FILTRES
st.sidebar.markdown("### Filtres")

vehicule = st.sidebar.selectbox(
    "Type de véhicule",
    ["Tous", "car", "taxi", "taxi-be", "moto"]
)

meteo = st.sidebar.selectbox(
    "Météo",
    ["Tous", "sunny", "rain", "cloudy"]
)

heure_range = st.sidebar.slider(
    "Plage horaire",
    min_value=0, max_value=23, value=(5, 22)
)

heure_min, heure_max = heure_range
v = None if vehicule == "Tous" else vehicule
m = None if meteo == "Tous" else meteo

st.sidebar.markdown('<hr style="border-top:1px solid #e5e7eb">', unsafe_allow_html=True)
st.sidebar.caption(f"**{vehicule}** · **{meteo}** · **{heure_min}h – {heure_max}h**")

def chart_layout(fig, key=None):
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="DM Sans", showlegend=False,
        margin=dict(t=10, b=10),
        xaxis=dict(gridcolor="#f3f4f6"),
        yaxis=dict(gridcolor="#f3f4f6"),
    )
    return fig

# BLOC 1 — FILTRE VÉHICULE
# "À quelle heure circule ce véhicule ?"
st.markdown('<div class="section-title">Par type de véhicule</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="question">🚗 À quelle heure circule <b>{vehicule}</b> ?</div>',
    unsafe_allow_html=True
)

data_heure = trafic_par_heure(vehicule=v, meteo=m)
df_heure = pd.DataFrame(
    list(data_heure.items()), columns=["Heure", "Trajets"]
)
df_heure = df_heure[(df_heure["Heure"] >= heure_min) & (df_heure["Heure"] <= heure_max)]

if df_heure.empty:
    st.info("Aucun trajet pour ce filtre.")
else:
    fig1 = px.bar(
        df_heure, x="Heure", y="Trajets",
        color="Trajets", color_continuous_scale=["#e0f4fb", "#A8D8EA", "#5bb8d4"]
    )
    fig1.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="DM Sans",
        margin=dict(t=10, b=10),
        xaxis=dict(dtick=1, gridcolor="#f3f4f6"),
        yaxis=dict(gridcolor="#f3f4f6"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig1, use_container_width=True, key="exp_fig_heure")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# BLOC 2 — FILTRE MÉTÉO
# "Quelles zones souffrent le plus sous cette météo ?"
st.markdown('<div class="section-title">Par condition météo</div>', unsafe_allow_html=True)
meteo_label = meteo if meteo != "Tous" else "toutes conditions"
st.markdown(
    f'<div class="question"> Quelles zones ont les trajets les plus longs sous <b>{meteo_label}</b> ?</div>',
    unsafe_allow_html=True
)

data_meteo = impact_meteo(vehicule=v, heure_min=heure_min, heure_max=heure_max)
df_meteo = pd.DataFrame(
    [(k, val["duree_moyenne"]) for k, val in data_meteo.items()],
    columns=["Meteo", "Duree_moyenne"]
)

data_zones = zones_plus_chargees(vehicule=v, meteo=m)
df_zones = pd.DataFrame(
    list(data_zones["arrivees"].items()),
    columns=["Zone", "Trajets"]
).sort_values("Trajets", ascending=True)

col1, col2 = st.columns(2)

with col1:
    st.caption("Durée moyenne par condition météo")
    if df_meteo.empty:
        st.info("Aucune donnée.")
    else:
        fig2a = px.bar(
            df_meteo, x="Meteo", y="Duree_moyenne",
            color="Meteo", color_discrete_map=METEO_COLORS,
            labels={"Meteo": "Météo", "Duree_moyenne": "Durée moyenne (min)"}
        )
        st.plotly_chart(chart_layout(fig2a), use_container_width=True, key="exp_fig_meteo")

with col2:
    st.caption("Zones les plus chargées à l'arrivée")
    if df_zones.empty:
        st.info("Aucune donnée.")
    else:
        fig2b = px.bar(
            df_zones, x="Trajets", y="Zone", orientation="h",
            color="Zone", color_discrete_sequence=PASTEL
        )
        st.plotly_chart(chart_layout(fig2b), use_container_width=True, key="exp_fig_zones")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# BLOC 3 — FILTRE PLAGE HORAIRE
# "Qui roule sur cette plage horaire ?"
st.markdown('<div class="section-title">Par plage horaire</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="question"> Qui roule entre <b>{heure_min}h</b> et <b>{heure_max}h</b> ?</div>',
    unsafe_allow_html=True
)

data_v = stats_par_vehicule(meteo=m, heure_min=heure_min, heure_max=heure_max)
df_v = pd.DataFrame(
    [
        {
            "Vehicule": k,
            "Trajets": val["nb_trajets"],
            "Distance": val["distance_moyenne"],
            "Duree": val["duree_moyenne"],
        }
        for k, val in data_v.items()
    ]
).sort_values("Trajets", ascending=False)

if df_v.empty:
    st.info("Aucune donnée pour cette plage horaire.")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Nombre de trajets par véhicule")
        fig3a = px.pie(
            df_v, names="Vehicule", values="Trajets",
            color_discrete_sequence=PASTEL, hole=0.4
        )
        fig3a.update_layout(
            paper_bgcolor="white", font_family="DM Sans",
            margin=dict(t=10, b=10), showlegend=True
        )
        st.plotly_chart(fig3a, use_container_width=True, key="exp_fig_pie")

    with col2:
        st.caption("Distance vs durée moyenne")
        fig3b = px.scatter(
            df_v, x="Distance", y="Duree",
            color="Vehicule", size="Trajets",
            color_discrete_sequence=PASTEL,
            labels={"Distance": "Distance moy. (km)", "Duree": "Durée moy. (min)"},
            text="Vehicule"
        )
        fig3b.update_traces(textposition="top center")
        fig3b.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="DM Sans", showlegend=False,
            margin=dict(t=10, b=10),
            xaxis=dict(gridcolor="#f3f4f6"),
            yaxis=dict(gridcolor="#f3f4f6"),
        )
        st.plotly_chart(fig3b, use_container_width=True, key="exp_fig_scatter")