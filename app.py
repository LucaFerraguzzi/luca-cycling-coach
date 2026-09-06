```python
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
# STILE
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: white;
    }

    .title {
        font-size: 38px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .small-label {
        color: #6b7280;
        font-size: 13px;
        font-weight: 700;
    }

    .big-number {
        color: #111827;
        font-size: 30px;
        font-weight: 800;
    }

    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .workout-description {
        color: #4b5563;
        line-height: 1.6;
    }

    .coach-text {
        color: #4b5563;
        line-height: 1.6;
    }

    .footer {
        color: #9ca3af;
        font-size: 12px;
        text-align: center;
        margin-top: 35px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR - PROFILO
# ============================================================

with st.sidebar:

    st.markdown("## 🚴 Luca Cycling Coach")
    st.caption("Personal Cycling Coach")

    st.divider()

    st.markdown("### 👤 Profilo")

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

    hr_max = st.number_input(
        "FC max (bpm)",
        min_value=100,
        max_value=230,
        value=190,
        step=1
    )

    st.divider()

    st.markdown("### 🎯 Obiettivo")

    goal = st.selectbox(
        "Obiettivo principale",
        [
            "Migliorare la forma generale",
            "Migliorare in salita",
            "Aumentare FTP",
            "Preparare una gara",
        ]
    )

    st.divider()

    st.markdown("### 📅 Disponibilità")

    available_days = st.multiselect(
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
        ]
    )

    st.divider()

    st.caption("Luca Cycling Coach")
    st.caption("Versione 0.1")

# ============================================================
# CALCOLI
# ============================================================

watts_per_kg = ftp / weight

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">Buongiorno, Luca 👋</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Ecco il tuo stato di allenamento.</div>',
    unsafe_allow_html=True
)

# ============================================================
# METRICHE
# ============================================================

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
        value="—",
        help="Lo collegheremo ai dati reali degli allenamenti."
    )

with col3:
    st.metric(
        label="😴 Fatigue",
        value="—",
        help="Lo calcoleremo dagli allenamenti effettuati."
    )

with col4:
    st.metric(
        label="📈 Form",
        value="—",
        help="Verrà calcolata automaticamente."
    )

# ============================================================
# ALLENAMENTO DI OGGI
# ============================================================

st.markdown(
    '<div class="section-title">🏋️ Allenamento di oggi</div>',
    unsafe_allow_html=True
)

today_col1, today_col2 = st.columns([2, 1])

with today_col1:

    st.subheader("Z2 Endurance")

    st.write("**Endurance aerobica — 60 minuti**")

    st.markdown(
        """
        <div class="workout-description">

        **Struttura**

        🟢 10' — Riscaldamento  
        🟢 40' — Z2 Endurance  
        🟢 10' — Defaticamento  

        <br>

        **Obiettivo**

        Costruire e mantenere una buona base aerobica
        lavorando a intensità controllata.

        </div>
        """,
        unsafe_allow_html=True
    )

with today_col2:

    st.info("### 🟢 Z2\n\n**60 min**")

    st.write("Intensità: **bassa**")

    if st.button(
        "▶️ Apri allenamento",
        use_container_width=True
    ):
        st.session_state["show_workout"] = True

# ============================================================
# DETTAGLI ALLENAMENTO
# ============================================================

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

# ============================================================
# SETTIMANA
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">📅 Piano della settimana</div>',
    unsafe_allow_html=True
)

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

# ============================================================
# COACH
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">🧠 Luca Cycling Coach</div>',
    unsafe_allow_html=True
)

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

# ============================================================
# PROGRESSI
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">📊 Progressi</div>',
    unsafe_allow_html=True
)

progress1, progress2, progress3 = st.columns(3)

with progress1:
    st.metric("Tempo settimanale", "—")

with progress2:
    st.metric("Carico settimanale", "—")

with progress3:
    st.metric("Allenamenti completati", "—")

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
```
