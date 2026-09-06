
import streamlit as st
from datetime import date, timedelta

# =========================================================
# CONFIGURAZIONE
# =========================================================

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# STILE
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
        color: #111827;
    }

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

    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: white !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #111827 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        color: white !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: white !important;
    }

    /* =========================
       PULSANTI
       ========================= */

    div.stButton > button {
        color: white !important;
        background-color: #111827 !important;
        border: 1px solid #111827 !important;
    }

    div.stButton > button:hover {
        color: white !important;
        background-color: #1f2937 !important;
        border-color: #1f2937 !important;
    }

    div.stButton > button p {
        color: white !important;
    }

    /* Pulsanti primary */
    div.stButton > button[kind="primary"] {
        color: white !important;
        background-color: #111827 !important;
    }

    div.stButton > button[kind="primary"] p {
        color: white !important;
    }

    /* =========================
       TESTI PRINCIPALI
       ========================= */

    h1, h2, h3, h4 {
        color: #111827 !important;
    }

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

    [data-testid="stMetricLabel"] {
        color: #4b5563 !important;
    }

    [data-testid="stMetricValue"] {
        color: #111827 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #4b5563 !important;
    }

    .workout-description {
        color: #374151 !important;
        line-height: 1.7;
    }

    .workout-description strong {
        color: #111827 !important;
    }

    .footer {
        color: #9ca3af !important;
        font-size: 12px;
        text-align: center;
        margin-top: 40px;
        padding-bottom: 20px;
    }

    .day-card {
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: white;
        min-height: 150px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "selected_workout" not in st.session_state:
    st.session_state["selected_workout"] = None

if "completed_workouts" not in st.session_state:
    st.session_state["completed_workouts"] = set()

if "calendar_week" not in st.session_state:
    st.session_state["calendar_week"] = date.today()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🚴 Luca Cycling Coach")
    st.caption("Personal Cycling Coach")

    st.divider()

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

    st.caption("Luca Cycling Coach · Versione 0.2")

# =========================================================
# DATI PROFILO
# =========================================================

watts_per_kg = ftp / weight

# =========================================================
# DATABASE ALLENAMENTI
# =========================================================

WORKOUTS = {

    "Z2 Endurance": {
        "icon": "🟢",
        "category": "Endurance",
        "duration": "1h 30m",
        "minutes": 90,
        "intensity": "Bassa",
        "goal": "Costruzione della base aerobica",
        "description": (
            "Allenamento continuo a intensità aerobica controllata. "
            "Deve essere sostenibile e permettere di pedalare "
            "senza accumulare eccessiva fatica."
        ),
        "steps": [
            ("Riscaldamento", "10 min", "Z2"),
            ("Endurance", "70 min", "Z2"),
            ("Defaticamento", "10 min", "Z2"),
        ],
    },

    "Sweet Spot": {
        "icon": "🟠",
        "category": "FTP",
        "duration": "1h 30m",
        "minutes": 90,
        "intensity": "Media/Alta",
        "goal": "Sviluppare la FTP",
        "description": (
            "Allenamento orientato allo sviluppo della potenza "
            "sostenibile. Gli intervalli sono impegnativi ma "
            "devono rimanere controllati."
        ),
        "steps": [
            ("Riscaldamento", "15 min", "Z2"),
            ("Sweet Spot", "12 min", "88-94% FTP"),
            ("Recupero", "5 min", "Recupero"),
            ("Sweet Spot", "12 min", "88-94% FTP"),
            ("Recupero", "5 min", "Recupero"),
            ("Sweet Spot", "12 min", "88-94% FTP"),
            ("Defaticamento", "29 min", "Z2"),
        ],
    },

    "Intervalli": {
        "icon": "🔴",
        "category": "VO2max",
        "duration": "1h",
        "minutes": 60,
        "intensity": "Alta",
        "goal": "Aumentare la capacità VO2max",
        "description": (
            "Sessione ad alta intensità con intervalli brevi. "
            "L'obiettivo è lavorare vicino alla massima capacità "
            "aerobica mantenendo una buona qualità di esecuzione."
        ),
        "steps": [
            ("Riscaldamento", "15 min", "Z2"),
            ("Intervallo 1", "4 min", "VO2max"),
            ("Recupero", "4 min", "Recupero"),
            ("Intervallo 2", "4 min", "VO2max"),
            ("Recupero", "4 min", "Recupero"),
            ("Intervallo 3", "4 min", "VO2max"),
            ("Recupero", "4 min", "Recupero"),
            ("Intervallo 4", "4 min", "VO2max"),
            ("Defaticamento", "13 min", "Z2"),
        ],
    },

    "Recupero": {
        "icon": "🔵",
        "category": "Recovery",
        "duration": "1h",
        "minutes": 60,
        "intensity": "Molto bassa",
        "goal": "Favorire il recupero",
        "description": (
            "Pedalata molto facile. L'obiettivo è muovere le gambe "
            "senza aggiungere un carico significativo."
        ),
        "steps": [
            ("Riscaldamento", "10 min", "Z2"),
            ("Recupero", "40 min", "Recupero"),
            ("Defaticamento", "10 min", "Z2"),
        ],
    },

    "Endurance + salita": {
        "icon": "🟠",
        "category": "Endurance / Climbing",
        "duration": "3h",
        "minutes": 180,
        "intensity": "Media",
        "goal": "Resistenza e capacità in salita",
        "description": (
            "Uscita lunga con prevalenza di lavoro aerobico e "
            "alcuni tratti in salita. La maggior parte del tempo "
            "deve rimanere controllata."
        ),
        "steps": [
            ("Riscaldamento", "20 min", "Z2"),
            ("Endurance", "60 min", "Z2"),
            ("Salita 1", "10 min", "Z3"),
            ("Recupero", "10 min", "Recupero"),
            ("Endurance", "30 min", "Z2"),
            ("Salita 2", "10 min", "Z3"),
            ("Recupero", "10 min", "Recupero"),
            ("Endurance", "20 min", "Z2"),
            ("Defaticamento", "10 min", "Z2"),
        ],
    },
}

# =========================================================
# PIANO SETTIMANALE
# =========================================================

WEEK_PLAN = {
    0: "Z2 Endurance",
    1: "Sweet Spot",
    2: "Riposo",
    3: "Intervalli",
    4: "Recupero",
    5: "Endurance + salita",
    6: "Riposo",
}

DAY_NAMES = [
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica",
]

# =========================================================
# FUNZIONI
# =========================================================

def get_monday(reference_date):
    return reference_date - timedelta(days=reference_date.weekday())


def show_footer():
    st.markdown(
        """
        <div class="footer">
            Luca Cycling Coach · Versione 0.2 ·
            Costruiamo il tuo coach personale 🚴
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_workout_detail(workout_name):

    if workout_name not in WORKOUTS:
        return

    # Anchor per portare l'utente alla scheda
    st.markdown(
        '<div id="workout-details"></div>',
        unsafe_allow_html=True,
    )

    workout = WORKOUTS[workout_name]

    st.divider()

    st.markdown(
        f"## {workout['icon']} {workout_name}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Durata",
            workout["duration"],
        )

    with col2:
        st.metric(
            "Intensità",
            workout["intensity"],
        )

    with col3:
        st.metric(
            "Categoria",
            workout["category"],
        )

    with col4:
        st.metric(
            "FTP",
            f"{ftp} W",
        )

    st.markdown("### 🎯 Obiettivo")

    st.write(workout["goal"])

    st.markdown("### 📋 Descrizione")

    st.write(workout["description"])

    st.markdown("### 🧱 Struttura")

    for index, (step_name, duration, zone) in enumerate(
        workout["steps"]
    ):

        col1, col2, col3 = st.columns(
            [3, 1, 2]
        )

        with col1:
            st.write(
                f"**{index + 1}. {step_name}**"
            )

        with col2:
            st.write(duration)

        with col3:
            st.write(zone)

        st.divider()

    if workout_name in st.session_state[
        "completed_workouts"
    ]:

        st.success(
            "✅ Allenamento completato"
        )

        if st.button(
            "↩️ Annulla completamento",
            key=f"undo_{workout_name}",
        ):

            st.session_state[
                "completed_workouts"
            ].remove(workout_name)

            st.rerun()

    else:

        if st.button(
            "✅ Segna come completato",
            type="primary",
            key=f"complete_{workout_name}",
        ):

            st.session_state[
                "completed_workouts"
            ].add(workout_name)

            st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

def show_dashboard():

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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚡ FTP",
            f"{ftp} W",
            f"{watts_per_kg:.2f} W/kg",
        )

    with col2:
        st.metric("💪 Fitness", "—")

    with col3:
        st.metric("😴 Fatigue", "—")

    with col4:
        st.metric("📈 Form", "—")

    st.divider()

    st.markdown("## 🏋️ Allenamento di oggi")

    today = date.today()

    today_workout_name = WEEK_PLAN[
        today.weekday()
    ]

    if today_workout_name == "Riposo":

        st.success(
            "😴 **Oggi è un giorno di riposo.**\n\n"
            "Recupera bene per affrontare i prossimi allenamenti."
        )

    else:

        workout = WORKOUTS[
            today_workout_name
        ]

        col1, col2 = st.columns(
            [2, 1]
        )

        with col1:

            st.subheader(
                f"{workout['icon']} "
                f"{today_workout_name}"
            )

            st.write(
                f"**{workout['goal']} — "
                f"{workout['duration']}**"
            )

            st.write(
                workout["description"]
            )

        with col2:

            st.info(
                f"**{workout['duration']}**\n\n"
                f"Intensità: "
                f"**{workout['intensity']}**"
            )

            if st.button(
                "▶️ Apri allenamento",
                use_container_width=True,
                key="dashboard_open_workout",
            ):

                st.session_state[
                    "selected_workout"
                ] = today_workout_name

                st.session_state[
                    "main_navigation"
                ] = "🚴 Allenamenti"

                st.rerun()

    st.divider()

    st.markdown(
        "## 📅 Piano della settimana"
    )

    monday = get_monday(today)

    week_columns = st.columns(7)

    for index, column in enumerate(
        week_columns
    ):

        current_day = (
            monday +
            timedelta(days=index)
        )

        workout_name = WEEK_PLAN[index]

        with column:

            st.markdown(
                f"**{DAY_NAMES[index]}**"
            )

            if current_day == today:
                st.caption("📍 OGGI")

            if workout_name == "Riposo":

                st.info(
                    "😴\n\nRiposo"
                )

            else:

                workout = WORKOUTS[
                    workout_name
                ]

                st.write(
                    f"{workout['icon']} "
                    f"**{workout_name}**"
                )

                st.caption(
                    workout["duration"]
                )

                if st.button(
                    "Dettagli",
                    key=f"dashboard_details_{index}",
                    use_container_width=True,
                ):

                    st.session_state[
                        "selected_workout"
                    ] = workout_name

                    st.session_state[
                        "main_navigation"
                    ] = "🚴 Allenamenti"

                    st.rerun()

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
            "Quando avremo i dati reali potremo analizzare:"
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


# =========================================================
# CALENDARIO
# =========================================================

def show_calendar():

    st.title("📅 Calendario")

    st.write(
        "Il tuo piano di allenamento settimanale."
    )

    st.divider()

    # =====================================================
    # NAVIGAZIONE SETTIMANA
    # =====================================================

    current_reference = (
        st.session_state["calendar_week"]
    )

    current_monday = get_monday(
        current_reference
    )

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col1:

        if st.button(
            "⬅️ Settimana precedente",
            use_container_width=True,
            key="calendar_previous",
        ):

            st.session_state[
                "calendar_week"
            ] = (
                current_monday -
                timedelta(days=7)
            )

            st.session_state[
                "selected_workout"
            ] = None

            st.rerun()

    with col2:

        st.markdown(
            f"<h3 style='text-align:center;'>"
            f"{current_monday.strftime('%d/%m/%Y')}"
            f" → "
            f"{(current_monday + timedelta(days=6)).strftime('%d/%m/%Y')}"
            f"</h3>",
            unsafe_allow_html=True,
        )

    with col3:

        if st.button(
            "Settimana successiva ➡️",
            use_container_width=True,
            key="calendar_next",
        ):

            st.session_state[
                "calendar_week"
            ] = (
                current_monday +
                timedelta(days=7)
            )

            st.session_state[
                "selected_workout"
            ] = None

            st.rerun()

    if st.button(
        "📍 Torna a questa settimana",
        use_container_width=True,
        key="calendar_today",
    ):

        st.session_state[
            "calendar_week"
        ] = date.today()

        st.session_state[
            "selected_workout"
        ] = None

        st.rerun()

    st.divider()

    # =====================================================
    # GIORNI
    # =====================================================

    for index in range(7):

        current_day = (
            current_monday +
            timedelta(days=index)
        )

        workout_name = WEEK_PLAN[index]

        col1, col2, col3, col4 = st.columns(
            [1.2, 3, 1.5, 1.5]
        )

        with col1:

            st.write(
                f"**{DAY_NAMES[index]}**"
            )

            st.caption(
                current_day.strftime("%d/%m")
            )

            if current_day == date.today():

                st.caption(
                    "📍 Oggi"
                )

        if workout_name == "Riposo":

            with col2:
                st.write(
                    "😴 **Riposo**"
                )

            with col3:
                st.write("—")

            with col4:
                st.write(
                    "Recupero"
                )

        else:

            workout = WORKOUTS[
                workout_name
            ]

            with col2:

                st.write(
                    f"{workout['icon']} "
                    f"**{workout_name}**"
                )

                st.caption(
                    workout["goal"]
                )

            with col3:

                st.write(
                    workout["duration"]
                )

            with col4:

                if workout_name in st.session_state[
                    "completed_workouts"
                ]:

                    st.success(
                        "Completato"
                    )

                else:

                    if st.button(
                        "Apri",
                        key=f"calendar_open_{current_day}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "selected_workout"
                        ] = workout_name

                        st.rerun()

        st.divider()

    # =====================================================
    # DETTAGLI ALLENAMENTO
    # =====================================================

    if st.session_state[
        "selected_workout"
    ]:

        show_workout_detail(
            st.session_state[
                "selected_workout"
            ]
        )


# =========================================================
# ALLENAMENTI
# =========================================================

def show_workouts():

    st.title("🚴 Allenamenti")

    st.write(
        "Tutti gli allenamenti disponibili nel tuo piano."
    )

    st.divider()

    for workout_name, workout in WORKOUTS.items():

        col1, col2, col3, col4 = st.columns(
            [1, 4, 2, 1.5]
        )

        with col1:

            st.markdown(
                f"## {workout['icon']}"
            )

        with col2:

            st.write(
                f"**{workout_name}**"
            )

            st.caption(
                workout["goal"]
            )

        with col3:

            st.write(
                workout["duration"]
            )

        with col4:

            if st.button(
                "Apri",
                key=f"workout_open_{workout_name}",
                use_container_width=True,
            ):

                st.session_state[
                    "selected_workout"
                ] = workout_name

                st.rerun()

        st.divider()

    if st.session_state[
        "selected_workout"
    ]:

        show_workout_detail(
            st.session_state[
                "selected_workout"
            ]
        )


# =========================================================
# ANALISI
# =========================================================

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
        "🚧 Qui aggiungeremo i grafici reali di "
        "FTP, carico, Fitness, Fatigue e Form."
    )

    st.divider()

    st.subheader(
        "🏋️ Allenamenti completati"
    )

    completed = st.session_state[
        "completed_workouts"
    ]

    if completed:

        for workout in completed:

            st.write(
                f"✅ {workout}"
            )

    else:

        st.write(
            "Non hai ancora segnato allenamenti come completati."
        )


# =========================================================
# AI COACH
# =========================================================

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
        "📋 Stato attuale"
    )

    st.write(
        f"FTP: **{ftp} W**"
    )

    st.write(
        f"Peso: **{weight:.1f} kg**"
    )

    st.write(
        f"FTP relativo: **{watts_per_kg:.2f} W/kg**"
    )

    st.divider()

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

    st.write(
        "• Analisi della forma"
    )

    st.write(
        "• Consigli personalizzati"
    )


# =========================================================
# PROFILO
# =========================================================

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


# =========================================================
# NAVIGAZIONE
# =========================================================

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


# =========================================================
# FOOTER
# =========================================================

show_footer()
