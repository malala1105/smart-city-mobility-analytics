import streamlit as st

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="SmartCity",
    page_icon="🚦",
    layout="centered"
)

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 3.2rem;
        line-height: 1.1;
        color: #0f1923;
        margin-bottom: 0.3rem;
        text-align: center;
    }

    .hero-sub {
        font-size: 1.05rem;
        color: #6b7280;
        font-weight: 300;
        margin-bottom: 2.5rem;
        text-align: center;
    }

    .badge {
        display: inline-block;
        background: #f0f4ff;
        color: #3b5bdb;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 20px;
        margin-right: 6px;
        margin-bottom: 6px;
        letter-spacing: 0.03em;
    }

    .badges-center {
        text-align: center;
        margin-bottom: 1rem;
    }

    .divider {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }

    .stat-box {
        background: #f9fafb;
        border-radius: 0px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }

    .stat-number {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #0f1923;
    }

    .stat-label {
        font-size: 0.82rem;
        color: #9ca3af;
        margin-top: 2px;
    }

    .page-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 0px;
        padding: 1.4rem 1.6rem;
        height: 100%;
    }

    .page-card-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }

    .page-card-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.15rem;
        color: #0f1923;
        margin-bottom: 0.4rem;
    }

    .page-card-desc {
        font-size: 0.88rem;
        color: #6b7280;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown('<div class="hero-title">SmartCity</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Analyse des flux de mobilité urbaine · Antananarivo</div>', unsafe_allow_html=True)

st.markdown("""
<div class="badges-center">
    <span class="badge">🚗 Véhicules</span>
    <span class="badge">🌧️ Météo</span>
    <span class="badge">🕐 Heures de pointe</span>
    <span class="badge">📍 17 quartiers</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ============================================================
# CHIFFRES CLÉS
# ============================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">10 000</div>
        <div class="stat-label">trajets analysés</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">17</div>
        <div class="stat-label">quartiers couverts</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">4</div>
        <div class="stat-label">types de véhicules</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ============================================================
# CARDS PAGES
# ============================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="page-card">
        <div class="page-card-icon">📊</div>
        <div class="page-card-title">Dashboard</div>
        <div class="page-card-desc">
            Visualise les 4 analyses clés : trafic par heure,
            zones les plus chargées, impact de la météo sur les trajets,
            et comparaison des véhicules.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="page-card">
        <div class="page-card-icon">🔍</div>
        <div class="page-card-title">Exploration</div>
        <div class="page-card-desc">
            Filtre les données par véhicule, météo ou plage horaire
            et observe comment les flux de mobilité évoluent
            selon les conditions.
        </div>
    </div>
    """, unsafe_allow_html=True)