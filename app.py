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

    /* ========================================================
       APP
       ======================================================== */

    .stApp {
        background-color: #f5f7fa;
        color: #111827;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Input numerici */
    section[data-testid="stSidebar"] input {
        color: #111827 !important;
        background-color: white !important;
    }

    /* Selectbox */
    section[data-testid="stSidebar"]
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: #111827 !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] span {
        color: #111827 !important;
    }

    /* Radio */
    section[data-testid="stSidebar"]
    div[role="radiogroup"] label {
        color: white !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label p {
        color: white !important;
    }

    /* Multiselect */
    section[data-testid="stSidebar"]
    div[data-baseweb="select"] {
        background-color: white !important;
    }

    /* ========================================================
       TITOLI
       ======================================================== */

    h1,
    h2,
    h3,
    h4 {
        color: #111827 !important;
    }

    /* ========================================================
       HEADER
       ======================================================== */

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 4px;
    }

    .main-subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    /* ========================================================
       METRICHE
       ======================================================== */

    [data-testid="stMetricLabel"] {
        color: #4b5563 !important;
    }

    [data-testid="stMetricValue"] {
        color: #111827 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #4b5563 !important;
    }

    /* ========================================================
       DESCRIZIONE WORKOUT
       ======================================================== */

    .workout-description {
        color: #374151 !important;
        line-height: 1.7;
    }

    .workout-description strong {
        color: #111827 !important;
    }

    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        color: #9ca3af !important;
        font-size: 12px;
        text-align: center;
        margin-top: 40px;
        padding-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    st.markdown(
        "## 🚴 Luca Cycling Coach"
    )

    st.caption(
        "Personal Cycling Coach"
    )

    st.divider()

    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    st.markdown("**MENU**")

    pagina = st.radio(
        "Navigazione",
        [
            "🏠 Dashboard",
            "📅 Calendario",
            "🚴 Allenamenti",
            "📊 Analisi",
            "🧠 AI Coach",
            "👤 Profilo",
        ],
        index=0,
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.divider()

    # --------------------------------------------------------
    # PROFILO
    # --------------------------------------------------------

    st.markdown("**PROFILO**")

    weight = st.number_input(
        "Peso (kg)",
        min_value=30.0,
        max_value=150.0,
        value=50.0,
        step=0.5,
        key="profile_weight",
    )

    ftp = st.number_input(
        "FTP (W)",
        min_value=50,
        max_value=500,
        value=160,
        step=1,
        key="profile_ftp",
    )

    fc_max = st.number_input(
        "FC max (bpm)",
        min_value=100,
        max_value=230,
        value=190,
        step=1,
        key="profile_hrmax",
    )

    obiettivo = st.selectbox(
        "Obiettivo",
        [
            "Migliorare la forma generale",
            "Migliorare in salita",
            "Aumentare FTP",
            "Preparare una gara",
        ],
        key="profile_goal",
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
            "Domenica",
        ],
        default=[
            "Lunedì",
            "Martedì",
            "Giovedì",
            "Venerdì",
            "Sabato",
        ],
        key="profile_days",
    )

    st.divider()

    st.caption(
        "Luca Cycling Coach · Versione 0.1"
    )


# ============================================================
# DATI DI BASE
# ============================================================

watts_per_kg = ftp / weight


# ============================================================
# FUNZIONE FOOTER
# ============================================================

def show_footer():
    st.markdown(
        """
        <div class="footer">
            Luca Cycling Coach · Versione 0.1 ·
            Costruiamo il tuo coach personale 🚴
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        '<div class="main-title">Buongiorno, Luca 👋</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        'Ecco il tuo stato di allenamento.'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # METRICHE
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚡ FTP",
            f"{ftp} W",
            f"{watts_per_kg:.2f} W/kg",
        )

    with col2:
        st.metric(
            "💪 Fitness",
            "—",
        )

    with col3:
        st.metric(
            "😴 Fatigue",
            "—",
        )

    with col4:
        st.metric(
            "📈 Form",
            "—",
        )

    # --------------------------------------------------------
    # ALLENAMENTO DI OGGI
    # --------------------------------------------------------

    st.divider()

    st.markdown("## 🏋️ Allenamento di oggi")

    today_col1, today_col2 = st.columns(
        [2, 1]
    )

    with today_col1:

        st.subheader(
            "Z2 Endurance"
        )

        st.write(
            "**Endurance aerobica — 60 minuti**"
        )

        st.markdown(
            """
            <div class="workout-description">

            <strong>Struttura</strong><br><br>

            🟢 10' — Riscaldamento<br>
            🟢 40' — Z2 Endurance<br>
            🟢 10' — Defaticamento<br><br>

            <strong>Obiettivo</strong><br><br>

            Costruire e mantenere una buona base
            aerobica lavorando a intensità controllata.

            </div>
            """,
            unsafe_allow_html=True,
        )

    with today_col2:

        st.info(
            "🟢 **Z2 Endurance**\n\n"
            "**60 minuti**\n\n"
            "Intensità: **bassa**"
        )

        if st.button(
            "▶️ Apri allenamento",
            use_container_width=True,
            key="open_today_workout",
        ):
            st.session_state[
                "show_workout"
            ] = True

    # --------------------------------------------------------
    # DETTAGLI
    # --------------------------------------------------------

    if st.session_state.get(
        "show_workout",
        False,
    ):

        st.divider()

        st.subheader(
            "📋 Dettagli allenamento"
        )

        st.write(
            "Mantieni un'intensità comoda e costante. "
            "L'obiettivo non è spingere, ma accumulare "
            "tempo aerobico di qualità."
        )

        st.write("**Indicazioni:**")

        st.write("• Pedalata fluida")
        st.write("• Intensità conversazionale")
        st.write("• Evita picchi di intensità")
        st.write("• Mantieni una cadenza naturale")

    # --------------------------------------------------------
    # PIANO SETTIMANALE
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        "## 📅 Piano della settimana"
    )

    days_plan = [
        (
            "Lunedì",
            "Z2 Endurance",
            "1h 30m",
            "🟢",
        ),
        (
            "Martedì",
            "Sweet Spot",
            "1h 30m",
            "🟠",
        ),
        (
            "Mercoledì",
            "Riposo",
            "—",
            "⚪",
        ),
        (
            "Giovedì",
            "Intervalli",
            "1h",
            "🔴",
        ),
        (
            "Venerdì",
            "Recupero",
            "1h",
            "🔵",
        ),
        (
            "Sabato",
            "Endurance + salita",
            "3h",
            "🟠",
        ),
        (
            "Domenica",
            "Riposo",
            "—",
            "⚪",
        ),
    ]

    week_columns = st.columns(7)

    for column, workout in zip(
        week_columns,
        days_plan,
    ):

        day, name, duration, icon = workout

        with column:

            st.markdown(
                f"### {icon}"
            )

            st.write(
                f"**{day}**"
            )

            st.write(name)

            st.caption(duration)

            if name != "Riposo":

                st.button(
                    "Dettagli",
                    key=f"details_{day}",
                    use_container_width=True,
                )

    # --------------------------------------------------------
    # COACH
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        "## 🧠 Luca Cycling Coach"
    )

    coach_col1, coach_col2 = st.columns(
        [2, 1]
    )

    with coach_col1:

        st.write(
            "Il coach analizzerà progressivamente "
            "i tuoi allenamenti e costruirà il piano "
            "in base alla tua risposta al carico."
        )

        st.write(
            "Quando collegheremo i dati reali, "
            "questa sezione potrà valutare automaticamente:"
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

    # --------------------------------------------------------
    # PROGRESSI
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        "## 📊 Progressi"
    )

    progress1, progress2, progress3 = st.columns(3)

    with progress1:
        st.metric(
            "Tempo settimanale",
            "—",
        )

    with progress2:
        st.metric(
            "Carico settimanale",
            "—",
        )

    with progress3:
        st.metric(
            "Allenamenti completati",
            "—",
        )


# ============================================================
# CALENDARIO
# ============================================================

def show_calendar():

    st.title("📅 Calendario")

    st.write(
        "Il tuo calendario di allenamento."
    )

    st.divider()

    st.subheader(
        "Questa settimana"
    )

    calendar_data = [
        ("Lunedì", "Z2 Endurance", "1h 30m", "🟢"),
        ("Martedì", "Sweet Spot", "1h 30m", "🟠"),
        ("Mercoledì", "Riposo", "—", "⚪"),
        ("Giovedì", "Intervalli", "1h", "🔴"),
        ("Venerdì", "Recupero", "1h", "🔵"),
        ("Sabato", "Endurance + salita", "3h", "🟠"),
        ("Domenica", "Riposo", "—", "⚪"),
    ]

    for day, name, duration, icon in calendar_data:

        col1, col2, col3 = st.columns(
            [1, 3, 1]
        )

        with col1:
            st.write(f"**{day}**")

        with col2:
            st.write(f"{icon} {name}")

        with col3:
            st.write(duration)

        st.divider()

    st.info(
        "🚧 Prossimo step: calendario interattivo "
        "collegato agli allenamenti reali."
    )


# ============================================================
# ALLENAMENTI
# ============================================================

def show_workouts():

    st.title("🚴 Allenamenti")

    st.write(
        "Tutti gli allenamenti del tuo piano."
    )

    st.divider()

    workouts = [
        (
            "🟢",
            "Z2 Endurance",
            "Base aerobica",
            "60 min",
        ),
        (
            "🟠",
            "Sweet Spot",
            "Sviluppo della FTP",
            "90 min",
        ),
        (
            "🔴",
            "Intervalli",
            "Stimolo VO2max",
            "60 min",
        ),
        (
            "🔵",
            "Recupero",
            "Recupero attivo",
            "60 min",
        ),
        (
            "🟠",
            "Endurance + salita",
            "Resistenza e climbing",
            "3 h",
        ),
    ]

    for icon, name, goal, duration in workouts:

        col1, col2, col3 = st.columns(
            [1, 4, 1]
        )

        with col1:
            st.markdown(
                f"## {icon}"
            )

        with col2:
            st.write(
                f"**{name}**"
            )
            st.caption(goal)

        with col3:
            st.write(duration)

        st.divider()

    st.info(
        "🚧 Prossimo step: pagina dettagliata "
        "per ogni allenamento."
    )


# ============================================================
# ANALISI
# ============================================================

def show_analysis():

    st.title("📊 Analisi")

    st.write(
        "Qui analizzeremo le tue prestazioni."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "FTP",
            f"{ftp} W",
        )

    with col2:
        st.metric(
            "FTP relativo",
            f"{watts_per_kg:.2f} W/kg",
        )

    with col3:
        st.metric(
            "FC max",
            f"{fc_max} bpm",
        )

    st.divider()

    st.subheader(
        "📈 Progressione"
    )

    st.info(
        "🚧 Qui aggiungeremo i grafici reali "
        "di FTP, carico, Fitness, Fatigue e Form."
    )


# ============================================================
# AI COACH
# ============================================================

def show_ai_coach():

    st.title("🧠 AI Coach")

    st.write(
        "Il tuo coach personale."
    )

    st.divider()

    st.info(
        "🤖 **Il coach sta preparando il tuo piano.**\n\n"
        "Quando collegheremo i dati reali degli allenamenti, "
        "potrà analizzare le tue sessioni, valutare il carico "
        "e suggerire modifiche al piano."
    )

    st.subheader(
        "🎯 Obiettivo attuale"
    )

    st.write(
        obiettivo
    )

    st.subheader(
        "💬 Prossimamente"
    )

    st.write(
        "• Analisi automatica degli allenamenti"
    )

    st.write(
        "• Feedback dopo ogni sessione"
    )

    st.write(
        "• Adattamento del carico"
    )

    st.write(
        "• Ripianificazione automatica"
    )


# ============================================================
# PROFILO
# ============================================================

def show_profile():

    st.title("👤 Profilo")

    st.write(
        "I tuoi dati ciclistici."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Peso",
            f"{weight:.1f} kg",
        )

        st.metric(
            "FTP",
            f"{ftp} W",
        )

    with col2:

        st.metric(
            "FTP relativo",
            f"{watts_per_kg:.2f} W/kg",
        )

        st.metric(
            "FC max",
            f"{fc_max} bpm",
        )

    st.divider()

    st.subheader(
        "🎯 Obiettivo"
    )

    st.write(
        obiettivo
    )

    st.subheader(
        "📅 Giorni disponibili"
    )

    if giorni:
        st.write(
            ", ".join(giorni)
        )
    else:
        st.warning(
            "Nessun giorno selezionato."
        )


# ============================================================
# ROUTING DELLE PAGINE
# ============================================================

if pagina == "🏠 Dashboard":

    show_dashboard()

elif pagina == "📅 Calendario":

    show_calendar()

elif pagina == "🚴 Allenamenti":

    show_workouts()

elif pagina == "📊 Analisi":

    show_analysis()

elif pagina == "🧠 AI Coach":

    show_ai_coach()

elif pagina == "👤 Profilo":

    show_profile()


# ============================================================
# FOOTER
# ============================================================

show_footer()
