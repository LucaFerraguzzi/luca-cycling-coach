```python
import streamlit as st
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* Pagina */
    .stApp {
        background-color: #f6f7f9;
    }

    /* Nasconde elementi Streamlit */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Titoli */
    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 0px;
        color: #111827;
    }

    .subtitle {
        color: #6b7280;
        font-size: 16px;
        margin-top: 2px;
        margin-bottom: 25px;
    }

    /* Card */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        min-height: 125px;
    }

    .metric-title {
        font-size: 14px;
        color: #6b7280;
        font-weight: 600;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #111827;
        margin-top: 8px;
    }

    .metric-description {
        font-size: 13px;
        color: #6b7280;
        margin-top: 4px;
    }

    /* Workout principale */
    .workout-card {
        background: white;
        border-radius: 18px;
        padding: 25px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    .workout-label {
        color: #6b7280;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .workout-title {
        font-size: 26px;
        font-weight: 800;
        color: #111827;
        margin-top: 5px;
    }

    .workout-info {
        color: #4b5563;
        font-size: 15px;
        margin-top: 5px;
    }

    /* Giorni */
    .day-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px;
        min-height: 115px;
    }

    .day-name {
        font-size: 12px;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
    }

    .day-workout {
        font-size: 15px;
        font-weight: 750;
        color: #111827;
        margin-top: 8px;
    }

    .day-duration {
        font-size: 13px;
        color: #6b7280;
        margin-top: 5px;
    }

    /* Coach */
    .coach-card {
        background: #111827;
        color: white;
        padding: 24px;
        border-radius: 18px;
        margin-top: 10px;
    }

    .coach-title {
        font-size: 20px;
        font-weight: 800;
    }

    .coach-text {
        color: #d1d5db;
        margin-top: 8px;
        line-height: 1.5;
    }

    /* Separatore */
    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        margin-top: 10px;
        margin-bottom: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## 🚴 Luca Cycling Coach")
    st.caption("Personal Cycling Coach")

    st.divider()

    st.markdown("### 👤 Profilo atleta")

    weight = st.number_input(
        "Peso",
        min_value=30.0,
        max_value=150.0,
        value=50.0,
        step=0.5,
        format="%.1f",
    )

    ftp = st.number_input(
        "FTP",
        min_value=50,
        max_value=500,
        value=160,
        step=1,
    )

    hr_max = st.number_input(
        "FC Max",
        min_value=100,
        max_value=230,
        value=190,
        step=1,
    )

    st.divider()

    goal = st.selectbox(
        "🎯 Obiettivo",
        [
            "Migliorare la forma generale",
            "Migliorare in salita",
            "Aumentare FTP",
            "Preparare una gara",
        ],
    )

    st.divider()

    st.markdown("### 📅 Disponibilità")

    days = st.multiselect(
        "Giorni di allenamento",
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
        label_visibility="collapsed",
    )

    st.divider()

    st.caption("Luca Cycling Coach")
    st.caption("Versione 0.1")

# ---------------------------------------------------------
# DATI CALCOLATI
# ---------------------------------------------------------

watts_per_kg = ftp / weight

today = datetime.now().strftime("%A")

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">Buongiorno, Luca 👋</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Ecco come sta andando il tuo percorso.</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# METRICHE
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">⚡ FTP</div>
            <div class="metric-value">{ftp} W</div>
            <div class="metric-description">{watts_per_kg:.2f} W/kg</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">💪 FITNESS</div>
            <div class="metric-value">—</div>
            <div class="metric-description">Dati non ancora collegati</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">😴 FATIGUE</div>
            <div class="metric-value">—</div>
            <div class="metric-description">Dati non ancora collegati</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">📈 FORM</div>
            <div class="metric-value">—</div>
            <div class="metric-description">Dati non ancora collegati</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------
# ALLENAMENTO + COACH
# ---------------------------------------------------------

left, right = st.columns([1.35, 1])

with left:

    st.markdown(
        '<div class="section-title">🏋️ Allenamento di oggi</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="workout-card">

            <div class="workout-label">
                ENDURANCE
            </div>

            <div class="workout-title">
                Z2 Endurance
            </div>

            <div class="workout-info">
                ⏱️ 60 minuti &nbsp;&nbsp; • &nbsp;&nbsp; 🟢 Intensità bassa
            </div>

            <br>

            <b>Struttura</b>

            <br><br>

            10' — Riscaldamento<br>
            40' — Z2 Endurance<br>
            10' — Defaticamento

            <br><br>

            <b>Obiettivo</b>

            <br>

            Sviluppare la base aerobica mantenendo un'intensità
            sostenibile e controllata.

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button("▶️ Apri allenamento", use_container_width=True):
        st.success("Dettagli dell'allenamento disponibili nella prossima versione.")

with right:

    st.markdown(
        '<div class="section-title">🧠 Coach</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="coach-card">

            <div class="coach-title">
                Il tuo coach
            </div>

            <div class="coach-text">
                Per ora sto utilizzando i dati del tuo profilo.
                Quando collegheremo gli allenamenti reali,
                potrò analizzare carico, recupero e andamento
                della forma.
                <br><br>
                Il prossimo passo sarà permettermi di prendere
                decisioni automatiche sul tuo piano.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# SETTIMANA
# ---------------------------------------------------------

st.write("")

st.markdown(
    '<div class="section-title">📅 Questa settimana</div>',
    unsafe_allow_html=True,
)

week = [
    ("LUN", "Z2 Endurance", "1h 30m"),
    ("MAR", "Sweet Spot", "1h 30m"),
    ("MER", "Riposo", "—"),
    ("GIO", "Intervalli", "1h"),
    ("VEN", "Recupero", "1h"),
    ("SAB", "Endurance + salita", "3h"),
    ("DOM", "Riposo", "—"),
]

cols = st.columns(7)

for col, (day, workout, duration) in zip(cols, week):

    with col:

        st.markdown(
            f"""
            <div class="day-card">

                <div class="day-name">
                    {day}
                </div>

                <div class="day-workout">
                    {workout}
                </div>

                <div class="day-duration">
                    {duration}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# PROGRESSI
# ---------------------------------------------------------

st.write("")

st.markdown(
    '<div class="section-title">📊 Progressi</div>',
    unsafe_allow_html=True,
)

p1, p2, p3 = st.columns(3)

with p1:
    st.metric(
        "Tempo questa settimana",
        "—",
        help="Verrà calcolato dagli allenamenti reali.",
    )

with p2:
    st.metric(
        "Carico",
        "—",
        help="Verrà calcolato quando collegheremo i dati.",
    )

with p3:
    st.metric(
        "Allenamenti completati",
        "—",
        help="Verrà calcolato dal calendario reale.",
    )

st.write("")

st.caption(
    f"🎯 Obiettivo attuale: {goal}  •  "
    f"Peso: {weight:.1f} kg  •  "
    f"FC max: {hr_max} bpm"
)
```
