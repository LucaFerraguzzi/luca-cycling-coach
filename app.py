import streamlit as st
import requests
from datetime import datetime, date, timedelta


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide"
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

if "wellness_cache" not in st.session_state:
    st.session_state.wellness_cache = None


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>

    /* SFONDO PRINCIPALE */

    .stApp {
        background-color: white;
    }

    .main {
        background-color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* TESTO PRINCIPALE */

    h1, h2, h3, h4 {
        color: #111827 !important;
    }

    p, span, label {
        color: #111827;
    }


    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background-color: #111827 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: white !important;
    }


    /* RADIO SIDEBAR */

    [data-testid="stSidebar"] [role="radiogroup"] label {
        color: white !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label span {
        color: white !important;
    }


    /* INPUT SIDEBAR */

    [data-testid="stSidebar"] input {
        color: #111827 !important;
        background-color: white !important;
    }

    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stTextInput input {
        color: #111827 !important;
        background-color: white !important;
    }


    /* SELECT SIDEBAR */

    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: white !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #111827 !important;
    }


    /* PULSANTI */

    .stButton > button {
        background-color: #111827 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }

    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: white !important;
    }

    .stButton > button:hover {
        background-color: #374151 !important;
        color: white !important;
    }

    .stButton > button:hover p,
    .stButton > button:hover span,
    .stButton > button:hover div {
        color: white !important;
    }


    /* METRICHE */

    [data-testid="stMetricValue"] {
        color: #111827 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #4b5563 !important;
    }


    /* RIQUADRI */

    .workout-card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        border: 1px solid #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INTERVALS.ICU CONFIG
# ============================================================

try:

    INTERVALS_ATHLETE_ID = st.secrets["INTERVALS_ATHLETE_ID"]
    INTERVALS_API_KEY = st.secrets["INTERVALS_API_KEY"]

except Exception:

    st.error(
        "Mancano INTERVALS_ATHLETE_ID e INTERVALS_API_KEY "
        "nei Secrets di Streamlit."
    )

    st.stop()


BASE_URL = "https://intervals.icu/api/v1"


def intervals_auth():
    return ("API_KEY", INTERVALS_API_KEY)


# ============================================================
# GET EVENTS FROM INTERVALS.ICU
# ============================================================

def get_intervals_events(start_date, end_date):

    url = (
        f"{BASE_URL}/athlete/"
        f"{INTERVALS_ATHLETE_ID}/events"
    )

    params = {
        "oldest": start_date.strftime("%Y-%m-%d"),
        "newest": end_date.strftime("%Y-%m-%d")
    }

    try:

        response = requests.get(
            url,
            params=params,
            auth=intervals_auth(),
            timeout=20
        )

        response.raise_for_status()

        events = response.json()

        workouts = []

        for event in events:

            if event.get("category") == "WORKOUT":
                workouts.append(event)

        workouts.sort(
            key=lambda x: x.get(
                "start_date_local",
                ""
            )
        )

        return workouts

    except requests.exceptions.RequestException as e:

        st.error(
            f"Errore nella connessione a Intervals.icu: {e}"
        )

        return []


# ============================================================
# GET WELLNESS FROM INTERVALS.ICU
# ============================================================

def get_wellness_data():

    today = date.today()

    oldest = today - timedelta(days=7)

    url = (
        f"{BASE_URL}/athlete/"
        f"{INTERVALS_ATHLETE_ID}/wellness"
    )

    params = {
        "oldest": oldest.strftime("%Y-%m-%d"),
        "newest": today.strftime("%Y-%m-%d")
    }

    try:

        response = requests.get(
            url,
            params=params,
            auth=intervals_auth(),
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return None

        data.sort(
            key=lambda x: x.get("id", "")
        )

        return data[-1]

    except requests.exceptions.RequestException:

        return None


# ============================================================
# UPDATE EVENT
# ============================================================

def update_intervals_event(
    event_id,
    name,
    start_datetime,
    end_datetime,
    description
):

    url = (
        f"{BASE_URL}/athlete/"
        f"{INTERVALS_ATHLETE_ID}/events/{event_id}"
    )

    payload = {

        "name": name,

        "start_date_local": start_datetime.strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),

        "end_date_local": end_datetime.strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),

        "description": description,

        "category": "WORKOUT",

        "type": "Ride"
    }

    try:

        response = requests.put(
            url,
            json=payload,
            auth=intervals_auth(),
            timeout=20
        )

        response.raise_for_status()

        return True

    except requests.exceptions.RequestException as e:

        st.error(
            "Errore durante il salvataggio "
            f"su Intervals.icu: {e}"
        )

        return False


# ============================================================
# HELPERS
# ============================================================

def parse_event_datetime(value):

    if not value:
        return None

    try:

        return datetime.fromisoformat(
            value.replace("Z", "")
        )

    except Exception:

        return None


def get_event_duration(event):

    start = parse_event_datetime(
        event.get("start_date_local")
    )

    end = parse_event_datetime(
        event.get("end_date_local")
    )

    if start and end:

        return int(
            (end - start).total_seconds() / 60
        )

    moving_time = event.get("moving_time")

    if moving_time:

        return int(moving_time / 60)

    return 60


def find_event_by_id(event_id):

    if not st.session_state.events_cache:
        return None

    for event in st.session_state.events_cache:

        if str(event.get("id")) == str(event_id):
            return event

    return None


def refresh_events():

    today = date.today()

    month_start = today.replace(day=1)

    if month_start.month == 12:

        next_month = date(
            month_start.year + 1,
            1,
            1
        )

    else:

        next_month = date(
            month_start.year,
            month_start.month + 1,
            1
        )

    month_end = next_month - timedelta(days=1)

    st.session_state.events_cache = (
        get_intervals_events(
            month_start,
            month_end
        )
    )


def refresh_wellness():

    st.session_state.wellness_cache = (
        get_wellness_data()
    )


# ============================================================
# LOAD DATA
# ============================================================

if st.session_state.events_cache is None:

    refresh_events()


if st.session_state.wellness_cache is None:

    refresh_wellness()


events = (
    st.session_state.events_cache or []
)


wellness = (
    st.session_state.wellness_cache
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🚴 Luca Cycling Coach")

    st.divider()

    page = st.radio(
        "Menu",
        [
            "Dashboard",
            "Calendario",
            "Allenamenti",
            "Analisi",
            "AI Coach",
            "Profilo"
        ],
        index=0
    )

    st.divider()

    st.subheader("Profilo")

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
        "FC max",
        min_value=100,
        max_value=230,
        value=200,
        step=1
    )

    goal = st.text_input(
        "Obiettivo",
        value="Migliorare fitness e salite"
    )


# ============================================================
# PROFILO
# ============================================================

watts_per_kg = ftp / weight


# ============================================================
# WELLNESS VALUES
# ============================================================

fitness = None
fatigue = None
form = None

if wellness:

    fitness = wellness.get("ctl")

    fatigue = wellness.get("atl")

    form = wellness.get("tsb")


# ============================================================
# TITLE
# ============================================================

def show_page_title(title, subtitle=None):

    st.title(title)

    if subtitle:

        st.caption(subtitle)


# ============================================================
# WORKOUT DETAIL
# ============================================================

def show_workout_detail(event):

    st.divider()

    st.subheader("Dettagli allenamento")

    name = event.get(
        "name",
        "Allenamento"
    )

    st.markdown(
        f"### {name}"
    )

    start = parse_event_datetime(
        event.get("start_date_local")
    )

    duration = get_event_duration(event)

    col1, col2, col3 = st.columns(3)

    with col1:

        if start:

            st.metric(
                "Data",
                start.strftime("%d/%m/%Y")
            )

        else:

            st.metric(
                "Data",
                "-"
            )

    with col2:

        if start:

            st.metric(
                "Ora",
                start.strftime("%H:%M")
            )

        else:

            st.metric(
                "Ora",
                "-"
            )

    with col3:

        st.metric(
            "Durata",
            f"{duration} min"
        )

    st.markdown("#### Descrizione")

    description = event.get(
        "description",
        ""
    )

    if description:

        st.text(description)

    else:

        st.info(
            "Questo allenamento non contiene "
            "una descrizione."
        )

    if st.button(
        "✏️ Modifica allenamento",
        key=f"edit_{event.get('id')}"
    ):

        st.session_state.edit_event = event

        st.rerun()


# ============================================================
# EDIT FORM
# ============================================================

def show_edit_form(event):

    st.divider()

    st.subheader("Modifica allenamento")

    start = parse_event_datetime(
        event.get("start_date_local")
    )

    if start is None:

        start = datetime.now()

    duration = get_event_duration(event)

    current_name = event.get(
        "name",
        "Allenamento"
    )

    current_description = event.get(
        "description",
        ""
    )

    with st.form(
        f"edit_form_{event.get('id')}"
    ):

        name = st.text_input(
            "Nome allenamento",
            value=current_name
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            new_date = st.date_input(
                "Data",
                value=start.date()
            )

        with col2:

            new_time = st.time_input(
                "Ora",
                value=start.time()
            )

        with col3:

            new_duration = st.number_input(
                "Durata (minuti)",
                min_value=1,
                max_value=600,
                value=duration,
                step=5
            )

        description = st.text_area(
            "Descrizione / workout",
            value=current_description,
            height=250
        )

        col_save, col_cancel = st.columns(2)

        with col_save:

            save = st.form_submit_button(
                "💾 Salva su Intervals.icu"
            )

        with col_cancel:

            cancel = st.form_submit_button(
                "Annulla"
            )

    if cancel:

        st.session_state.edit_event = None

        st.rerun()

    if save:

        new_start = datetime.combine(
            new_date,
            new_time
        )

        new_end = (
            new_start +
            timedelta(
                minutes=int(new_duration)
            )
        )

        success = update_intervals_event(
            event_id=event.get("id"),
            name=name,
            start_datetime=new_start,
            end_datetime=new_end,
            description=description
        )

        if success:

            st.success(
                "Allenamento aggiornato "
                "su Intervals.icu!"
            )

            st.session_state.edit_event = None

            refresh_events()

            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    show_page_title(
        "Dashboard",
        "Il tuo centro di controllo per il ciclismo."
    )

    # --------------------------------------------------------
    # TOP METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "⚡ FTP",
            f"{ftp} W",
            f"{watts_per_kg:.2f} W/kg"
        )

    with col2:

        if fitness is not None:

            st.metric(
                "💪 Fitness",
                f"{fitness:.0f}"
            )

        else:

            st.metric(
                "💪 Fitness",
                "—"
            )

    with col3:

        if fatigue is not None:

            st.metric(
                "😴 Fatigue",
                f"{fatigue:.0f}"
            )

        else:

            st.metric(
                "😴 Fatigue",
                "—"
            )

    with col4:

        if form is not None:

            st.metric(
                "📈 Form",
                f"{form:+.0f}"
            )

        else:

            st.metric(
                "📈 Form",
                "—"
            )

    st.divider()

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    if st.button(
        "🔄 Aggiorna dati",
        key="dashboard_refresh"
    ):

        refresh_events()

        refresh_wellness()

        st.rerun()

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    st.subheader("🏋️ Prossimo allenamento")

    today = date.today()

    upcoming = []

    for event in events:

        start = parse_event_datetime(
            event.get("start_date_local")
        )

        if start and start.date() >= today:

            upcoming.append(event)

    upcoming = upcoming[:1]

    if not upcoming:

        st.info(
            "Non ci sono allenamenti imminenti "
            "nel calendario."
        )

    else:

        event = upcoming[0]

        start = parse_event_datetime(
            event.get("start_date_local")
        )

        duration = get_event_duration(event)

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [3, 1, 1]
            )

            with col1:

                st.markdown(
                    f"### {event.get('name', 'Allenamento')}"
                )

            with col2:

                if start:

                    st.write(
                        start.strftime(
                            "%d/%m %H:%M"
                        )
                    )

            with col3:

                st.write(
                    f"{duration} min"
                )

            if st.button(
                "Apri allenamento",
                key=f"dashboard_open_{event.get('id')}"
            ):

                st.session_state.selected_event = (
                    event.get("id")
                )

                st.rerun()

    st.divider()

    # --------------------------------------------------------
    # TRAINING STATUS
    # --------------------------------------------------------

    st.subheader("📊 Stato allenamento")

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:

        if fitness is not None:

            st.metric(
                "Fitness / CTL",
                f"{fitness:.0f}"
            )

        else:

            st.metric(
                "Fitness / CTL",
                "—"
            )

    with status_col2:

        if fatigue is not None:

            st.metric(
                "Fatigue / ATL",
                f"{fatigue:.0f}"
            )

        else:

            st.metric(
                "Fatigue / ATL",
                "—"
            )

    with status_col3:

        if form is not None:

            st.metric(
                "Form / TSB",
                f"{form:+.0f}"
            )

        else:

            st.metric(
                "Form / TSB",
                "—"
            )

    if form is not None:

        if form > 10:

            st.success(
                "🟢 Sei molto fresco. "
                "Potresti essere pronto per una sessione impegnativa."
            )

        elif form >= -10:

            st.info(
                "🟡 La tua forma è relativamente equilibrata."
            )

        else:

            st.warning(
                "🔴 Il carico recente è elevato. "
                "Il recupero potrebbe essere importante."
            )

    st.divider()

    # --------------------------------------------------------
    # NEXT WORKOUTS
    # --------------------------------------------------------

    st.subheader("📅 Prossimi allenamenti")

    if not events:

        st.info(
            "Nessun allenamento programmato."
        )

    else:

        shown = 0

        for event in events:

            if shown >= 5:

                break

            start = parse_event_datetime(
                event.get("start_date_local")
            )

            if start and start.date() >= today:

                duration = get_event_duration(
                    event
                )

                with st.container(border=True):

                    col1, col2, col3 = st.columns(
                        [3, 1.5, 1]
                    )

                    with col1:

                        st.write(
                            f"**{event.get('name', 'Allenamento')}**"
                        )

                    with col2:

                        st.write(
                            start.strftime(
                                "%d/%m %H:%M"
                            )
                        )

                    with col3:

                        st.write(
                            f"{duration} min"
                        )

                shown += 1


# ============================================================
# CALENDAR
# ============================================================

elif page == "Calendario":

    show_page_title(
        "Calendario",
        "Allenamenti sincronizzati direttamente da Intervals.icu."
    )

    if st.button(
        "🔄 Aggiorna calendario",
        key="refresh_calendar"
    ):

        refresh_events()

        st.rerun()

    if not events:

        st.info(
            "Nessun allenamento trovato."
        )

    else:

        for event in events:

            start = parse_event_datetime(
                event.get("start_date_local")
            )

            duration = get_event_duration(event)

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(
                    [1.3, 3, 1.5, 1]
                )

                with col1:

                    if start:

                        st.markdown(
                            f"**{start.strftime('%d/%m')}**"
                        )

                        st.caption(
                            start.strftime("%H:%M")
                        )

                with col2:

                    st.markdown(
                        f"**{event.get('name', 'Allenamento')}**"
                    )

                    st.caption(
                        event.get(
                            "type",
                            "Ride"
                        )
                    )

                with col3:

                    st.write(
                        f"⏱️ {duration} min"
                    )

                with col4:

                    if st.button(
                        "Apri",
                        key=f"calendar_{event.get('id')}"
                    ):

                        st.session_state.selected_event = (
                            event.get("id")
                        )

                        st.rerun()


# ============================================================
# WORKOUTS
# ============================================================

elif page == "Allenamenti":

    show_page_title(
        "Allenamenti",
        "Gli allenamenti attualmente presenti su Intervals.icu."
    )

    if not events:

        st.info(
            "Nessun allenamento presente."
        )

    else:

        for event in events:

            start = parse_event_datetime(
                event.get("start_date_local")
            )

            duration = get_event_duration(event)

            with st.container(border=True):

                if start:

                    st.caption(
                        start.strftime(
                            "%d/%m/%Y — %H:%M"
                        )
                    )

                st.subheader(
                    event.get(
                        "name",
                        "Allenamento"
                    )
                )

                st.write(
                    f"Durata: **{duration} minuti**"
                )

                if st.button(
                    "Apri allenamento",
                    key=f"workout_{event.get('id')}"
                ):

                    st.session_state.selected_event = (
                        event.get("id")
                    )

                    st.rerun()


# ============================================================
# ANALYSIS
# ============================================================

elif page == "Analisi":

    show_page_title(
        "Analisi",
        "Analisi della tua situazione attuale."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if fitness is not None:

            st.metric(
                "Fitness",
                f"{fitness:.0f}"
            )

        else:

            st.metric(
                "Fitness",
                "—"
            )

    with col2:

        if fatigue is not None:

            st.metric(
                "Fatigue",
                f"{fatigue:.0f}"
            )

        else:

            st.metric(
                "Fatigue",
                "—"
            )

    with col3:

        if form is not None:

            st.metric(
                "Form",
                f"{form:+.0f}"
            )

        else:

            st.metric(
                "Form",
                "—"
            )

    st.divider()

    st.subheader("Profilo")

    st.write(
        f"Peso: **{weight:.1f} kg**"
    )

    st.write(
        f"FTP: **{ftp} W**"
    )

    st.write(
        f"FTP relativo: **{watts_per_kg:.2f} W/kg**"
    )

    st.write(
        f"FC max: **{hr_max} bpm**"
    )

    st.divider()

    st.info(
        "Il prossimo step sarà aggiungere i grafici "
        "storici di Fitness, Fatigue e Form."
    )


# ============================================================
# AI COACH
# ============================================================

elif page == "AI Coach":

    show_page_title(
        "AI Coach",
        "Il futuro coach automatico di Luca Cycling Coach."
    )

    st.info(
        "🚧 AI Coach in sviluppo"
    )

    st.write(
        """
        L'obiettivo è permettere al coach di:

        - analizzare gli allenamenti completati;
        - confrontare allenamento previsto e allenamento reale;
        - valutare Fitness, Fatigue e Form;
        - valutare il carico di allenamento;
        - considerare gli allenamenti saltati;
        - valutare le sensazioni dell'atleta;
        - modificare gli allenamenti futuri;
        - aggiornare automaticamente Intervals.icu.
        """
    )


# ============================================================
# PROFILE
# ============================================================

elif page == "Profilo":

    show_page_title(
        "Profilo",
        "Le tue impostazioni."
    )

    st.subheader("Dati atleta")

    st.write(
        f"**Peso:** {weight:.1f} kg"
    )

    st.write(
        f"**FTP:** {ftp} W"
    )

    st.write(
        f"**FTP relativo:** {watts_per_kg:.2f} W/kg"
    )

    st.write(
        f"**FC max:** {hr_max} bpm"
    )

    st.write(
        f"**Obiettivo:** {goal}"
    )


# ============================================================
# SELECTED WORKOUT
# ============================================================

if st.session_state.selected_event is not None:

    selected = find_event_by_id(
        st.session_state.selected_event
    )

    if selected:

        show_workout_detail(
            selected
        )


# ============================================================
# EDIT WORKOUT
# ============================================================

if st.session_state.edit_event is not None:

    show_edit_form(
        st.session_state.edit_event
    )
