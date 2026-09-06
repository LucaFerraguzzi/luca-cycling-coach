import streamlit as st

# ============================================================
# CONFIGURAZIONE
# ============================================================

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

    /* =========================
       PAGINA PRINCIPALE
       ========================= */

    .stApp {
        background-color: #f5f7fa;
        color: #111827;
    }

    .main {
        color: #111827;
    }

    .main p,
    .main span,
    .main label {
        color: #111827;
    }

    h1, h2, h3, h4 {
        color: #111827 !important;
    }

    .main small,
    .main .stCaption {
        color: #6b7280 !important;
    }

    /* =========================
       SIDEBAR
       ========================= */

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] input {
        color: #111827 !important;
        background-color: white !important;
    }

    section[data-testid="stSidebar"] textarea {
        color: #111827 !important;
        background-color: white !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        color: white !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #111827 !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: white !important;
    }

    /* =========================
       HEADER
       ========================= */

    .title {
        font-size: 38px;
        font-weight: 800;
        color: #111827 !important;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 16px;
        color: #6b7280 !important;
        margin-bottom: 25px;
    }

    /* =========================
       METRICHE
       ========================= */

    [data-testid="stMetricLabel"] {
        color: #4b5563 !important;
    }

    [data-testid="stMetricValue"] {
        color: #111827 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #4b5563 !important;
    }

    /* =========================
       DESCRIZIONI
       ========================= */

    .workout-description {
        color: #374151 !important;
        line-height: 1.6;
    }

    .workout-description p,
    .workout-description li {
        color: #374151 !important;
    }

    .coach-text {
        color: #374151 !important;
        line-height: 1.6;
    }

    /* =========================
       BOTTONI
       ========================= */

    .stButton > button {
        color: #111827 !important;
        background-color: white !important;
        border: 1px solid #d1d5db !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    .stButton > button:hover {
        border-color: #111827 !important;
        color: #111827 !important;
    }

    /* =========================
       INPUT
       ========================= */

    input {
        color: #111827 !important;
    }

    /* =========================
       SELECTBOX
       ========================= */

    div[data-baseweb="select"] {
        color: #111827 !important;
    }

    div[data-baseweb="select"] > div {
        color: #111827 !important;
        background-color: white !important;
    }

    /* =========================
       FOOTER
       ========================= */

    .footer {
        color: #9ca3af !important;
        font-size: 12px;
        text-align: center;
        margin-top: 35px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # LOGO / TITOLO
   st.markdown("## 🚴 Luca Cycling Coach")
st.caption("Personal Cycling Coach")

    st.markdown("---")

    # MENU
    st.markdown(
        """
        <div style="
            color:#9ca3af !important;
            font-size:12px;
            font-weight:600;
            margin-bottom:8px;
        ">
            MENU
        </div>
        """,
        unsafe_allow_html=True
    )

    pagina = st.radio(
        "Navigazione",
        [
            "🏠 Dashboard",
            "📅 Calendario",
            "🚴 Allenamenti",
            "📊 Analisi",
            "🧠 AI Coach",
            "👤 Profilo"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # PROFILO
    st.markdown(
        """
        <div style="
            color:#9ca3af !important;
            font-size:12px;
            font-weight:600;
            margin-bottom:10px;
        ">
            PROFILO
        </div>
        """,
        unsafe_allow_html=True
    )

    weight = st.number_input(
        "Peso (kg)",
        min_value=30.0,
        max_value=150.0,
        value=50.0,
        step=0.5
    )

    ftp = st.number_input(
        "FTP (W)",
        min_value=50,
        max_value=500,
        value=160,
        step=1
    )

    fc_max = st.number_input(
        "FC max (bpm)",
        min_value=100,
        max_value=230,
        value=190,
        step=1
    )

    obiettivo = st.selectbox(
        "Obiettivo",
        [
            "Migliorare la forma generale",
            "Migliorare in salita",
            "Aumentare FTP",
            "Preparare una gara"
        ]
    )

    giorni = st.multiselect(
        "Giorni disponibili",
        [
            "Lunedì",
            "Martedì",
            "Mercoledì",
            "Giovedì",
            "Venerdì",
            "Sabato",
            "Domenica"
        ],
        default=[
            "Lunedì",
            "Martedì",
            "Giovedì",
            "Venerdì",
            "Sabato"
        ]
    )

    st.markdown("---")

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#6b7280 !important;
            font-size:11px;
            padding:5px 0;
        ">
            Luca Cycling Coach<br>
            Versione 0.1
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGINA: DASHBOARD
# ============================================================

if pagina == "🏠 Dashboard":

    # ========================================================
    # CALCOLI
    # ========================================================

    watts_per_kg = ftp / weight

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        '<div class="title">Buongiorno, Luca 👋</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Ecco il tuo stato di allenamento.</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # METRICHE
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="⚡ FTP",
            value=f"{ftp} W",
            delta=f"{watts_per_kg:.2f} W/kg"
        )

    with col2:
        st.metric(
            label="💪 Fitness",
            value="—"
        )

    with col3:
        st.metric(
            label="😴 Fatigue",
            value="—"
        )

    with col4:
        st.metric(
            label="📈 Form",
            value="—"
        )

    # ========================================================
    # ALLENAMENTO DI OGGI
    # ========================================================

    st.divider()

    st.markdown("## 🏋️ Allenamento di oggi")

    today_col1, today_col2 = st.columns([2, 1])

    with today_col1:

        st.subheader("Z2 Endurance")

        st.write("**Endurance aerobica — 60 minuti**")

        st.markdown(
            """
            <div class="workout-description">

            <strong>Struttura</strong><br><br>

            🟢 10' — Riscaldamento<br>
            🟢 40' — Z2 Endurance<br>
            🟢 10' — Defaticamento<br><br>

            <strong>Obiettivo</strong><br><br>

            Costruire e mantenere una buona base aerobica
            lavorando a intensità controllata.

            </div>
            """,
            unsafe_allow_html=True
        )

    with today_col2:

        st.info(
            "🟢 **Z2 Endurance**\n\n"
            "**60 minuti**\n\n"
            "Intensità: **bassa**"
        )

        if st.button(
            "▶️ Apri allenamento",
            use_container_width=True
        ):
            st.session_state["show_workout"] = True

    # ========================================================
    # DETTAGLI ALLENAMENTO
    # ========================================================

    if st.session_state.get("show_workout", False):

        st.divider()

        st.subheader("📋 Dettagli allenamento")

        st.write(
            "Mantieni un'intensità comoda e costante. "
            "L'obiettivo non è spingere, ma accumulare tempo "
            "aerobico di qualità."
        )

        st.write("**Indicazioni:**")

        st.write("• Pedalata fluida")
        st.write("• Intensità conversazionale")
        st.write("• Evita picchi di intensità")
        st.write("• Mantieni una cadenza naturale")

    # ========================================================
    # SETTIMANA
    # ========================================================

    st.divider()

    st.markdown("## 📅 Piano della settimana")

    days_plan = [
        ("Lunedì", "Z2 Endurance", "1h 30m", "🟢"),
        ("Martedì", "Sweet Spot", "1h 30m", "🟠"),
        ("Mercoledì", "Riposo", "—", "⚪"),
        ("Giovedì", "Intervalli", "1h", "🔴"),
        ("Venerdì", "Recupero", "1h", "🔵"),
        ("Sabato", "Endurance + salita", "3h", "🟠"),
        ("Domenica", "Riposo", "—", "⚪"),
    ]

    week_columns = st.columns(7)

    for column, workout in zip(week_columns, days_plan):

        day, name, duration, icon = workout

        with column:

            st.markdown(f"### {icon}")

            st.write(f"**{day}**")

            st.write(name)

            st.caption(duration)

            if name != "Riposo":
                st.button(
                    "Dettagli",
                    key=f"details_{day}",
                    use_container_width=True
                )

    # ========================================================
    # COACH
    # ========================================================

    st.divider()

    st.markdown("## 🧠 Luca Cycling Coach")

    coach_col1, coach_col2 = st.columns([2, 1])

    with coach_col1:

        st.write(
            "Il coach analizzerà progressivamente i tuoi allenamenti "
            "e costruirà il piano in base alla tua risposta al carico."
        )

        st.write(
            "Quando collegheremo i dati reali, questa sezione potrà "
            "valutare automaticamente:"
        )

        st.write("• carico di allenamento")
        st.write("• recupero")
        st.write("• Fitness")
        st.write("• Fatigue")
        st.write("• Form")
        st.write("• progressione")

    with coach_col2:

        st.info(
            "**Prossimamente**\n\n"
            "🤖 Analisi AI\n\n"
            "📊 Dati reali\n\n"
            "🔄 Ripianificazione automatica"
        )

    # ========================================================
    # PROGRESSI
    # ========================================================

    st.divider()

    st.markdown("## 📊 Progressi")

    progress1, progress2, progress3 = st.columns(3)

    with progress1:
        st.metric(
            "Tempo settimanale",
            "—"
        )

    with progress2:
        st.metric(
            "Carico settimanale",
            "—"
        )

    with progress3:
        st.metric(
            "Allenamenti completati",
            "—"
        )


# ============================================================
# PAGINA: CALENDARIO
# ============================================================

elif pagina == "📅 Calendario":

    st.title("📅 Calendario")

    st.write(
        "Qui costruiremo il calendario completo degli allenamenti."
    )

    st.info(
        "🚧 In sviluppo: calendario con allenamenti giornalieri, "
        "durata, intensità e stato di completamento."
    )


# ============================================================
# PAGINA: ALLENAMENTI
# ============================================================

elif pagina == "🚴 Allenamenti":

    st.title("🚴 Allenamenti")

    st.write(
        "Qui troverai tutti gli allenamenti programmati."
    )

    st.info(
        "🚧 In sviluppo: libreria degli allenamenti e pagina "
        "dettagliata per ogni workout."
    )


# ============================================================
# PAGINA: ANALISI
# ============================================================

elif pagina == "📊 Analisi":

    st.title("📊 Analisi")

    st.write(
        "Qui analizzeremo le tue prestazioni e la tua progressione."
    )

    st.info(
        "🚧 In sviluppo: Fitness, Fatigue, Form, carico, "
        "FTP, zone e progressione."
    )


# ============================================================
# PAGINA: AI COACH
# ============================================================

elif pagina == "🧠 AI Coach":

    st.title("🧠 AI Coach")

    st.write(
        "Il tuo coach personale analizzerà i dati degli allenamenti "
        "e ti aiuterà a prendere decisioni sul piano."
    )

    st.info(
        "🚧 In sviluppo: analisi automatica degli allenamenti, "
        "feedback e ripianificazione."
    )


# ============================================================
# PAGINA: PROFILO
# ============================================================

elif pagina == "👤 Profilo":

    st.title("👤 Profilo")

    st.write(
        "Qui potrai gestire i dati utilizzati dal tuo coach."
    )

    st.markdown("### 🚴 Dati ciclistici")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Peso", f"{weight:.1f} kg")
        st.metric("FTP", f"{ftp} W")

    with col2:
        st.metric("FTP relativo", f"{ftp / weight:.2f} W/kg")
        st.metric("FC max", f"{fc_max} bpm")

    st.markdown("### 🎯 Obiettivo")

    st.write(obiettivo)

    st.markdown("### 📅 Giorni disponibili")

    if giorni:
        st.write(", ".join(giorni))
    else:
        st.warning("Nessun giorno selezionato.")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Luca Cycling Coach · Versione 0.1 ·
        Costruiamo il tuo coach personale 🚴
    </div>
    """,
    unsafe_allow_html=True
)
