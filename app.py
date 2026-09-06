import streamlit as st

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide",
)

st.title("🚴 Luca Cycling Coach")
st.caption("Il tuo coach ciclistico personale")

# SIDEBAR
st.sidebar.header("👤 Profilo atleta")

weight = st.sidebar.number_input(
    "Peso (kg)",
    min_value=30.0,
    max_value=150.0,
    value=50.0,
    step=0.5
)

ftp = st.sidebar.number_input(
    "FTP (W)",
    min_value=50,
    max_value=500,
    value=160,
    step=1
)

hr_max = st.sidebar.number_input(
    "FC max (bpm)",
    min_value=100,
    max_value=230,
    value=190,
    step=1
)

st.sidebar.divider()

goal = st.sidebar.selectbox(
    "🎯 Obiettivo principale",
    [
        "Migliorare la forma generale",
        "Migliorare in salita",
        "Aumentare FTP",
        "Preparare una gara",
    ]
)

days = st.sidebar.multiselect(
    "📅 Giorni disponibili",
    [
        "Lunedì",
        "Martedì",
        "Mercoledì",
        "Giovedì",
        "Venerdì",
        "Sabato",
        "Domenica",
    ],
    default=[
        "Lunedì",
        "Martedì",
        "Giovedì",
        "Venerdì",
        "Sabato",
    ],
)

# DASHBOARD
st.header("📊 Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("FTP", f"{ftp} W")
col2.metric("Peso", f"{weight:.1f} kg")
col3.metric("W/kg", f"{ftp / weight:.2f}")
col4.metric("Giorni disponibili", len(days))

st.divider()

# PROSSIMO ALLENAMENTO
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏋️ Prossimo allenamento")

    st.info(
        """
        **Z2 Endurance — 60 min**

        • 10' riscaldamento  
        • 40' Z2  
        • 10' defaticamento  

        Obiettivo: costruire la base aerobica senza accumulare
        troppa fatica.
        """
    )

with col2:
    st.subheader("📈 Stato attuale")

    st.metric("Carico settimanale", "—")
    st.metric("Fitness", "—")
    st.metric("Fatigue", "—")
    st.metric("Form", "—")

st.divider()

# CALENDARIO
st.subheader("📅 Piano della settimana")

week = [
    ("Lunedì", "Z2 Endurance", "1h 30m"),
    ("Martedì", "Sweet Spot", "1h 30m"),
    ("Mercoledì", "Riposo", "—"),
    ("Giovedì", "Intervalli", "1h"),
    ("Venerdì", "Recupero", "1h"),
    ("Sabato", "Endurance + salita", "3h"),
    ("Domenica", "Riposo", "—"),
]

for day, workout, duration in week:
    c1, c2, c3 = st.columns([1, 3, 1])

    c1.write(f"**{day}**")
    c2.write(workout)
    c3.write(duration)

st.divider()

st.caption(
    f"🎯 Obiettivo: {goal}  |  "
    f"📅 Giorni disponibili: {', '.join(days) if days else 'nessuno'}"
)
