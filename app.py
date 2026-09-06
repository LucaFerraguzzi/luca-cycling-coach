import streamlit as st
import requests
from datetime import datetime, timedelta, date

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE
# ============================================================

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

if "edit_event" not in st.session_state:
    st.session_state.edit_event = None

if "events_cache" not in st.session_state:
    st.session_state.events_cache = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       APP GENERALE
       ======================================================== */

    .stApp {
        background-color: #f7f8fa;
    }

    .main {
        color: #111827 !important;
    }

    .main p,
    .main span,
    .main label,
    .main div,
    .main li,
    .main td,
    .main th {
        color: #111827 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
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

    section[data-testid="stSidebar"] [data-baseweb="select"] {
        color: #111827 !important;
        background-color: white !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #111827 !important;
    }

    /* ========================================================
       TITOLI
       ======================================================== */

    .page-title {
        font-size: 36px;
        font-weight: 800;
        color: #111827 !important;
        margin-bottom: 4px;
    }

    .page-subtitle {
        font-size: 16px;
        color: #6b7280 !important;
        margin-bottom: 24px;
    }

    /* ========================================================
       CARD
       ======================================================== */

    .card {
        background: white;
        border-radius: 18px;
        padding: 22px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        margin-bottom: 18px;
    }

    .card * {
        color: #111827 !important;
    }

    .card-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    /* ========================================================
       WORKOUT CARD
       ======================================================== */

    .workout-card {
        background: white;
        border-radius: 16px;
        padding: 18px;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.03);
    }

    .workout-card * {
        color: #111827 !important;
    }

    .workout-date {
        font-size: 13px;
        font-weight: 700;
        color: #6b7280 !important;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .workout-name {
        font-size: 20px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .workout-meta {
        font-size: 14px;
        color: #4b5563 !important;
    }

    /* ========================================================
       DAY CARD
       ======================================================== */

    .day-card {
        background: white;
        border-radius: 14px;
        padding: 14px;
        border: 1px solid #e5e7eb;
        min-height: 120px;
    }

    .day-card * {
        color: #111827 !important;
    }

    .day-title {
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .day-workout {
        background: #f3f4f6;
        border-radius: 10px;
        padding: 9px;
        margin-top: 7px;
        font-size: 13px;
    }

    /* ========================================================
       DETTAGLI ALLENAMENTO
       ======================================================== */

    .detail-box {
        background: white;
        border-radius: 18px;
        padding: 24px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        margin-top: 20px;
    }

    .detail-box,
    .detail-box *,
    .detail-box p,
    .detail-box span,
    .detail-box div,
    .detail-box li {
        color: #111827 !important;
    }

    .detail-title {
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .detail-description {
        white-space: pre-wrap;
        line-height: 1.6;
        color: #111827 !important;
    }

    /* ========================================================
       METRICHE
       ======================================================== */

    [data-testid="stMetric"] {
        background-color: white !important;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #111827 !important;
    }

    /* ========================================================
       INPUT
       ======================================================== */

    input {
        color: #111827 !important;
        background-color: white !important;
    }

    textarea {
        color: #111827 !important;
        background-color: white !important;
    }

    /* ========================================================
       BOTTONI
       ======================================================== */

    .stButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    .stButton button p,
    .stButton button span {
        color: inherit !important;
    }

    /* ========================================================
       EXPANDER
       ======================================================== */

    [data-testid="stExpander"] {
        background-color: white !important;
        border-radius: 14px !important;
        border: 1px solid #e5e7eb !important;
    }

    [data-testid="stExpander"] * {
        color: #111827 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INTERVALS API
# ============================================================

try:
    INTERVALS_ATHLETE_ID = st.secrets["INTERVALS_ATHLETE_ID"]
    INTERVALS_API_KEY = st.secrets["INTERVALS_API_KEY"]
except Exception:
    st.error(
        "Non trovo INTERVALS_ATHLETE_ID e INTERVALS_API_KEY nei Secrets di Streamlit."
    )
    st.stop()


BASE_URL = "https://intervals.icu/api/v1"


def intervals_auth():
    return ("API_KEY", INTERVALS_API_KEY)


# ============================================================
# GET EVENTS
# ============================================================

def get_intervals_events(start_date, end_date):
    """
    Recupera gli eventi pianificati da Intervals.icu.
    """

    url = (
        f"{BASE_URL}/athlete/"
        f"{INTERVALS_ATHLETE_ID}/events"
    )

    params = {
        "oldest": start_date.strftime("%Y-%m-%d"),
        "newest": end_date.strftime("%Y-%m-%d"),
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=intervals_auth(),
            timeout=20,
        )

        if response.status_code != 200:
            st.error(
                f"Errore Intervals.icu: "
                f"{response.status_code} - {response.text}"
            )
            return []

        data = response.json()

        # Mostriamo solo gli allenamenti
        events = [
            event
            for event in data
            if event.get("category") == "WORKOUT"
        ]

        return events

    except Exception as e:
        st.error(f"Errore durante il collegamento a Intervals.icu: {e}")
        return []


# ============================================================
# UPDATE EVENT
# ============================================================

def update_intervals_event(
    event_id,
    name,
    start_datetime,
    end_datetime,
    description,
):
    """
    Modifica un allenamento esistente su Intervals.icu.
    """

    url = (
        f"{BASE_URL}/athlete/"
        f"{INTERVALS_ATHLETE_ID}/events/"
        f"{event_id}"
    )

    payload = {
        "name": name,
        "start_date_local": start_datetime.isoformat(),
        "end_date_local": end_datetime.isoformat(),
        "description": description,
        "category": "WORKOUT",
        "type": "Ride",
    }

    try:
        response = requests.put(
            url,
            json=payload,
            auth=intervals_auth(),
            timeout=20,
        )

        if response.status_code not in [200, 201]:
            st.error(
                f"Errore salvataggio Intervals.icu: "
                f"{response.status_code} - {response.text}"
            )
            return False

        return True

    except Exception as e:
        st.error(f"Errore durante il salvataggio: {e}")
        return False


# ============================================================
# DATE HELPERS
# ============================================================

def parse_event_datetime(event):
    value = event.get("start_date_local")

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "")
        )
    except Exception:
        return None


def format_duration(minutes):
    if not minutes:
        return "—"

    try:
        minutes = int(round(float(minutes)))
    except Exception:
        return "—"

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:
        return f"{hours}h {mins}m"

    return f"{mins}m"


def get_event_duration(event):
    start = parse_event_datetime(event)

    end_value = event.get("end_date_local")

    if start and end_value:
        try:
            end = datetime.fromisoformat(
                end_value.replace("Z", "")
            )

            return max(
                1,
                int((end - start).total_seconds() / 60)
            )

        except Exception:
            pass

    moving_time = event.get("moving_time")

    if moving_time:
        try:
            return int(float(moving_time) / 60)
        except Exception:
            pass

    return None


# ============================================================
# LOAD CURRENT MONTH
# ============================================================

today = date.today()

month_start = today.replace(day=1)

if today.month == 12:
    next_month = date(
        today.year + 1,
        1,
        1
    )
else:
    next_month = date(
        today.year,
        today.month + 1,
        1
    )

month_end = next_month - timedelta(days=1)


if st.session_state.events_cache is None:
    st.session_state.events_cache = get_intervals_events(
        month_start,
        month_end,
    )

events = st.session_state.events_cache


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:28px;
            font-weight:800;
            margin-bottom:5px;
        ">
            🚴 Luca Cycling Coach
        </div>

        <div style="
            font-size:13px;
            opacity:0.75;
            margin-bottom:25px;
        ">
            Il tuo coach per il ciclismo
        </div>
        """,
        unsafe_allow_html=True,
    )

    pagina = st.radio(
        "MENU",
        [
            "🏠 Dashboard",
            "📅 Calendario",
            "🚴 Allenamenti",
            "📊 Analisi",
            "🤖 AI Coach",
            "👤 Profilo",
        ],
        key="main_navigation",
    )

    st.divider()

    st.markdown("### Profilo")

    weight = st.number_input(
        "Peso (kg)",
        min_value=30.0,
        max_value=150.0,
        value=50.0,
        step=0.5,
    )

    ftp = st.number_input(
        "FTP (W)",
        min_value=50,
        max_value=500,
        value=160,
        step=1,
    )

    fc_max = st.number_input(
        "FC max",
        min_value=100,
        max_value=230,
        value=200,
        step=1,
    )

    goal = st.selectbox(
        "Obiettivo",
        [
            "Salita",
            "Resistenza",
            "FTP",
            "Gran fondo",
            "Prestazione generale",
        ],
    )

    st.divider()

    st.caption("🔗 Calendario sincronizzato con Intervals.icu")


# ============================================================
# HELPERS UI
# ============================================================

def show_page_title(title, subtitle):
    st.markdown(
        f'<div class="page-title">{title}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def find_event_by_id(event_id):
    for event in events:
        if str(event.get("id")) == str(event_id):
            return event

    return None


# ============================================================
# SELECT WORKOUT
# ============================================================

def select_workout(event):
    st.session_state.selected_event = event.get("id")


# ============================================================
# WORKOUT DETAIL
# ============================================================

def show_workout_detail(event):

    if not event:
        return

    start = parse_event_datetime(event)

    duration = get_event_duration(event)

    st.markdown(
        '<div class="detail-box">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="detail-title">🚴 {event.get("name", "Allenamento")}</div>',
        unsafe_allow_html=True,
    )

    if start:
        st.markdown(
            f"""
            <div style="
                color:#6b7280 !important;
                margin-bottom:18px;
            ">
                {start.strftime("%d/%m/%Y")} ·
                {start.strftime("%H:%M")} ·
                {format_duration(duration)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Durata",
            format_duration(duration),
        )

    with col2:
        st.metric(
            "Tipo",
            event.get("type", "Ride"),
        )

    with col3:
        load = event.get("load")

        if load is None:
            load = event.get("icu_training_load")

        st.metric(
            "Carico",
            str(round(load)) if load is not None else "—",
        )

    st.markdown("### Descrizione")

    description = event.get("description")

    if not description:
        description = "Nessuna descrizione disponibile."

    st.markdown(
        f"""
        <div class="detail-description">
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# EDIT WORKOUT
# ============================================================

def show_edit_form(event):

    if not event:
        return

    st.markdown("## ✏️ Modifica allenamento")

    start = parse_event_datetime(event)

    if start is None:
        start = datetime.now()

    duration = get_event_duration(event)

    if duration is None:
        duration = 60

    with st.form("edit_workout_form"):

        new_name = st.text_input(
            "Nome allenamento",
            value=event.get("name", ""),
        )

        col1, col2 = st.columns(2)

        with col1:

            new_date = st.date_input(
                "Data",
                value=start.date(),
            )

        with col2:

            new_time = st.time_input(
                "Ora",
                value=start.time(),
            )

        new_duration = st.number_input(
            "Durata (minuti)",
            min_value=1,
            max_value=600,
            value=int(duration),
            step=5,
        )

        old_description = event.get(
            "description",
            "",
        )

        new_description = st.text_area(
            "Descrizione allenamento",
            value=old_description,
            height=250,
        )

        col_save, col_cancel = st.columns(2)

        with col_save:

            save = st.form_submit_button(
                "💾 Salva su Intervals.icu",
                use_container_width=True,
            )

        with col_cancel:

            cancel = st.form_submit_button(
                "Annulla",
                use_container_width=True,
            )

    if cancel:

        st.session_state.edit_event = None
        st.rerun()

    if save:

        new_start = datetime.combine(
            new_date,
            new_time,
        )

        new_end = (
            new_start
            + timedelta(minutes=int(new_duration))
        )

        success = update_intervals_event(
            event_id=event.get("id"),
            name=new_name,
            start_datetime=new_start,
            end_datetime=new_end,
            description=new_description,
        )

        if success:

            st.success(
                "Allenamento aggiornato su Intervals.icu ✅"
            )

            st.session_state.events_cache = None
            st.session_state.edit_event = None
            st.session_state.selected_event = event.get("id")

            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    show_page_title(
        "Dashboard",
        "Panoramica del tuo allenamento.",
    )

    today_events = []

    for event in events:

        start = parse_event_datetime(event)

        if start and start.date() == today:
            today_events.append(event)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "FTP",
            f"{ftp} W",
        )

    with col2:
        st.metric(
            "Peso",
            f"{weight:.1f} kg",
        )

    with col3:
        st.metric(
            "Obiettivo",
            goal,
        )

    with col4:
        st.metric(
            "Allenamenti oggi",
            len(today_events),
        )

    st.markdown("## 📅 Allenamento di oggi")

    if today_events:

        for event in today_events:

            start = parse_event_datetime(event)

            duration = get_event_duration(event)

            st.markdown(
                '<div class="workout-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="workout-name">
                    🚴 {event.get("name", "Allenamento")}
                </div>

                <div class="workout-meta">
                    {start.strftime("%H:%M") if start else ""}
                    · {format_duration(duration)}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            if st.button(
                "Dettagli",
                key=f"dashboard_detail_{event.get('id')}",
            ):

                st.session_state.selected_event = event.get("id")
                st.rerun()

    else:

        st.info(
            "Nessun allenamento programmato per oggi."
        )

    st.markdown("## 🔜 Prossimi allenamenti")

    upcoming = []

    for event in events:

        start = parse_event_datetime(event)

        if start and start.date() >= today:
            upcoming.append(event)

    upcoming.sort(
        key=lambda x: parse_event_datetime(x)
        or datetime.max
    )

    for event in upcoming[:5]:

        start = parse_event_datetime(event)
        duration = get_event_duration(event)

        st.markdown(
            f"""
            <div class="workout-card">

                <div class="workout-date">
                    {start.strftime("%A %d %B")
                    if start else ""}
                </div>

                <div class="workout-name">
                    🚴 {event.get("name", "Allenamento")}
                </div>

                <div class="workout-meta">
                    {format_duration(duration)}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Apri allenamento",
            key=f"dashboard_open_{event.get('id')}",
        ):

            st.session_state.selected_event = event.get("id")
            st.rerun()


# ============================================================
# CALENDAR
# ============================================================

def show_calendar():

    show_page_title(
        "Calendario",
        "Gli allenamenti programmati su Intervals.icu.",
    )

    if not events:

        st.warning(
            "Non sono stati trovati allenamenti su Intervals.icu."
        )

        return

    # --------------------------------------------------------
    # SELECT MONTH
    # --------------------------------------------------------

    col1, col2 = st.columns([1, 3])

    with col1:

        selected_month = st.selectbox(
            "Mese",
            [
                "Settembre 2026",
                "Ottobre 2026",
                "Novembre 2026",
                "Dicembre 2026",
            ],
        )

    st.markdown("### Allenamenti")

    # --------------------------------------------------------
    # LISTA EVENTI
    # --------------------------------------------------------

    sorted_events = sorted(
        events,
        key=lambda x: parse_event_datetime(x)
        or datetime.max,
    )

    for event in sorted_events:

        start = parse_event_datetime(event)

        if not start:
            continue

        duration = get_event_duration(event)

        st.markdown(
            '<div class="workout-card">',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(
            [1.5, 4, 1]
        )

        with col1:

            st.markdown(
                f"""
                <div class="workout-date">
                    {start.strftime("%a %d/%m")}
                </div>

                <div class="workout-meta">
                    {start.strftime("%H:%M")}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:

            st.markdown(
                f"""
                <div class="workout-name">
                    {event.get("name", "Allenamento")}
                </div>

                <div class="workout-meta">
                    🚴 {event.get("type", "Ride")}
                    · ⏱️ {format_duration(duration)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:

            if st.button(
                "Apri",
                key=f"calendar_open_{event.get('id')}",
                use_container_width=True,
            ):

                st.session_state.selected_event = event.get("id")
                st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# WORKOUTS
# ============================================================

def show_workouts():

    show_page_title(
        "Allenamenti",
        "Tutti gli allenamenti presenti su Intervals.icu.",
    )

    if not events:

        st.info(
            "Nessun allenamento disponibile."
        )

        return

    sorted_events = sorted(
        events,
        key=lambda x: parse_event_datetime(x)
        or datetime.max,
    )

    for event in sorted_events:

        start = parse_event_datetime(event)
        duration = get_event_duration(event)

        st.markdown(
            f"""
            <div class="workout-card">

                <div class="workout-date">
                    {start.strftime("%d/%m/%Y · %H:%M")
                    if start else ""}
                </div>

                <div class="workout-name">
                    🚴 {event.get("name", "Allenamento")}
                </div>

                <div class="workout-meta">
                    {event.get("type", "Ride")}
                    · {format_duration(duration)}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "👁 Dettagli",
                key=f"workout_detail_{event.get('id')}",
                use_container_width=True,
            ):

                st.session_state.selected_event = event.get("id")
                st.rerun()

        with col2:

            if st.button(
                "✏️ Modifica",
                key=f"workout_edit_{event.get('id')}",
                use_container_width=True,
            ):

                st.session_state.edit_event = event.get("id")
                st.session_state.selected_event = event.get("id")
                st.rerun()


# ============================================================
# ANALYSIS
# ============================================================

def show_analysis():

    show_page_title(
        "Analisi",
        "Qui analizzeremo progressivamente i tuoi allenamenti.",
    )

    st.info(
        "📊 La parte avanzata dell'analisi verrà collegata "
        "alle attività completate e ai dati di Intervals.icu."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "FTP attuale",
            f"{ftp} W",
        )

    with col2:

        st.metric(
            "Peso",
            f"{weight:.1f} kg",
        )

    with col3:

        if weight > 0:
            wkg = ftp / weight
        else:
            wkg = 0

        st.metric(
            "W/kg",
            f"{wkg:.2f}",
        )

    st.markdown(
        """
        <div class="card">

            <div class="card-title">
                🔍 Prossimo step
            </div>

            <p>
                L'app potrà leggere le attività completate,
                confrontarle con gli allenamenti programmati
                e valutare fatica, carico e progressione.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AI COACH
# ============================================================

def show_ai_coach():

    show_page_title(
        "AI Coach",
        "Il futuro coach intelligente di Luca Cycling Coach.",
    )

    st.markdown(
        """
        <div class="card">

            <div class="card-title">
                🤖 AI Coach
            </div>

            <p>
                In questa sezione costruiremo il vero coach
                automatico dell'app.
            </p>

            <p>
                L'obiettivo sarà far analizzare all'AI:
            </p>

            <ul>
                <li>gli allenamenti programmati</li>
                <li>gli allenamenti realmente completati</li>
                <li>carico e fatica</li>
                <li>progressione nel tempo</li>
                <li>eventuali giorni saltati</li>
                <li>prestazioni e sensazioni</li>
            </ul>

            <p>
                Successivamente il coach potrà modificare
                automaticamente gli allenamenti futuri
                direttamente su Intervals.icu.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.button(
        "🤖 Analizza allenamento",
        disabled=True,
    )


# ============================================================
# PROFILE
# ============================================================

def show_profile():

    show_page_title(
        "Profilo",
        "Le tue impostazioni di allenamento.",
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.markdown(
            "### 🚴 Dati atleta"
        )

        st.write(
            f"**Peso:** {weight:.1f} kg"
        )

        st.write(
            f"**FTP:** {ftp} W"
        )

        st.write(
            f"**FC max:** {fc_max} bpm"
        )

        st.write(
            f"**Obiettivo:** {goal}"
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.markdown(
            "### 🔗 Collegamenti"
        )

        st.write(
            "🟢 Intervals.icu: collegato"
        )

        st.write(
            "🟡 Garmin: integrazione futura"
        )

        st.write(
            "🟡 Strava: integrazione futura"
        )

        st.write(
            "🟡 MyWhoosh: integrazione futura"
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# ROUTING PAGINE
# ============================================================

if pagina == "🏠 Dashboard":

    show_dashboard()

elif pagina == "📅 Calendario":

    show_calendar()

elif pagina == "🚴 Allenamenti":

    show_workouts()

elif pagina == "📊 Analisi":

    show_analysis()

elif pagina == "🤖 AI Coach":

    show_ai_coach()

elif pagina == "👤 Profilo":

    show_profile()


# ============================================================
# SELECTED WORKOUT DETAIL
# ============================================================

if st.session_state.selected_event:

    selected = find_event_by_id(
        st.session_state.selected_event
    )

    if selected:

        st.markdown("---")

        show_workout_detail(selected)

        st.markdown("")

        if st.button(
            "✏️ Modifica questo allenamento",
            key="selected_edit_button",
        ):

            st.session_state.edit_event = selected.get("id")
            st.rerun()


# ============================================================
# EDIT FORM
# ============================================================

if st.session_state.edit_event:

    edit_event = find_event_by_id(
        st.session_state.edit_event
    )

    if edit_event:

        st.markdown("---")

        show_edit_form(edit_event)
