import streamlit as st
import requests
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

if "edit_event" not in st.session_state:
    st.session_state.edit_event = None

if "events_cache" not in st.session_state:
    st.session_state.events_cache = None

if "wellness_cache" not in st.session_state:
    st.session_state.wellness_cache = None

if "calendar_week_offset" not in st.session_state:
    st.session_state.calendar_week_offset = 0

if "coach_message" not in st.session_state:
    st.session_state.coach_message = None

# =========================
# STYLE
# =========================

st.markdown(
    """
    <style>
    .stApp { background-color: white; }
    .main { background-color: white; }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        color: #111827 !important;
    }

    p, span, label {
        color: #111827;
    }

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

    [data-testid="stSidebar"] [role="radiogroup"] label {
        color: white !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label span {
        color: white !important;
    }

    [data-testid="stSidebar"] input {
        color: #111827 !important;
        background-color: white !important;
    }

    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stTextInput input {
        color: #111827 !important;
        background-color: white !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: white !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #111827 !important;
    }

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

    [data-testid="stMetricValue"] {
        color: #111827 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #4b5563 !important;
    }

    .workout-card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        border: 1px solid #e5e7eb;
    }

    .workout-description {
        color: #111827 !important;
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 15px;
        white-space: pre-wrap;
        line-height: 1.5;
    }

    .workout-description * {
        color: #111827 !important;
    }

    .connected-app {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .coach-box {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# INTERVALS. ICU
# =========================

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


def get_intervals_events(start_date, end_date):
    url = f"{BASE_URL}/athlete/{INTERVALS_ATHLETE_ID}/events"
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
            key=lambda x: x.get("start_date_local", "")
        )

        return workouts

    except requests.exceptions.RequestException as e:
        st.error(
            f"Errore nella connessione a Intervals.icu: {e}"
        )
        return []


def get_wellness_data():
    today = date.today()
    oldest = today - timedelta(days=7)

    url = f"{BASE_URL}/athlete/{INTERVALS_ATHLETE_ID}/wellness"

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

        data.sort(key=lambda x: x.get("id", ""))

        return data[-1]

    except requests.exceptions.RequestException:
        return None


def create_intervals_event(
    name,
    start_datetime,
    end_datetime,
    description,
    indoor=False,
    target="AUTO"
):
    url = f"{BASE_URL}/athlete/{INTERVALS_ATHLETE_ID}/events"

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
        "type": "Ride",
        "indoor": indoor,
        "target": target
    }

    try:
        response = requests.post(
            url,
            json=payload,
            auth=intervals_auth(),
            timeout=20
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(
            "Errore durante la creazione "
            f"dell'allenamento su Intervals.icu: {e}"
        )
        return None


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


# =========================
# GENERIC HELPERS
# =========================

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

    start_date = today - timedelta(days=60)
    end_date = today + timedelta(days=120)

    st.session_state.events_cache = get_intervals_events(
        start_date,
        end_date
    )


def refresh_wellness():
    st.session_state.wellness_cache = get_wellness_data()


def get_monday(input_date):
    return input_date - timedelta(
        days=input_date.weekday()
    )


def get_calendar_week():
    today = date.today()

    current_monday = get_monday(today)

    selected_monday = (
        current_monday +
        timedelta(
            weeks=st.session_state.calendar_week_offset
        )
    )

    selected_sunday = (
        selected_monday +
        timedelta(days=6)
    )

    return selected_monday, selected_sunday


def is_event_completed(event):
    if event.get("paired_activity_id"):
        return True

    if event.get("paired_activity"):
        return True

    if event.get("activity_id"):
        return True

    return False


# =========================
# COACH ENGINE - V1
# =========================
# Questa prima versione è un motore deterministico:
# crea allenamenti sensati in base a FTP/FC,
# disponibilità, indoor/outdoor e stato di carico.
#
# In una fase successiva aggiungeremo il vero modulo
# AI che analizzerà automaticamente gli allenamenti reali,
# RPE, carico e risposta individuale.


def zone_power(ftp, percent):
    return round(ftp * percent / 100)


def zone_hr(hr_max, low, high):
    return (
        round(hr_max * low / 100),
        round(hr_max * high / 100)
    )


def coach_state(fitness, fatigue, form):
    if form is None:
        return "unknown"

    if form < -20:
        return "fatigued"

    if form < -10:
        return "loaded"

    if form > 15:
        return "fresh"

    return "balanced"


def generate_indoor_workout(
    workout_type,
    duration,
    ftp
):
    z2_low = zone_power(ftp, 60)
    z2_high = zone_power(ftp, 70)

    if workout_type == "Endurance":
        warmup = 10
        cooldown = 5
        main = max(10, duration - warmup - cooldown)

        return (
            "Riscaldamento: 10' a 55-65% FTP\n"
            f"Endurance: {main}' a 60-70% FTP "
            f"({z2_low}-{z2_high} W)\n"
            "Defaticamento: 5' a 50-60% FTP"
        )

    if workout_type == "Tempo":
        return (
            "Riscaldamento: 15' a 55-70% FTP\n"
            "3 x 8' a 80-85% FTP\n"
            "Recupero: 4' facili tra le ripetute\n"
            "10' a Z2\n"
            "Defaticamento: 5'"
        )

    if workout_type == "Sweet Spot":
        return (
            "Riscaldamento: 15' a 55-70% FTP\n"
            "3 x 8' a 88-92% FTP\n"
            "Recupero: 4' facili tra le ripetute\n"
            "10' a Z2\n"
            "Defaticamento: 5'"
        )

    if workout_type == "Threshold":
        return (
            "Riscaldamento: 15' progressivo fino a 75% FTP\n"
            "3 x 8' a 95-100% FTP\n"
            "Recupero: 4' facili tra le ripetute\n"
            "10' a Z2\n"
            "Defaticamento: 5'"
        )

    if workout_type == "VO2max":
        return (
            "Riscaldamento: 15' progressivo\n"
            "5 x 3' a 110-115% FTP\n"
            "Recupero: 3' facili tra le ripetute\n"
            "10' a Z2\n"
            "Defaticamento: 5'"
        )

    if workout_type == "Recovery":
        return (
            "45' molto facili a 50-60% FTP.\n"
            "Cadenza naturale, nessuna spinta."
        )

    return (
        f"Riscaldamento: 10' a 55-65% FTP\n"
        f"{max(10, duration - 15)}' a 60-70% FTP\n"
        "Defaticamento: 5'"
    )


def generate_outdoor_workout(
    workout_type,
    duration,
    hr_max
):
    z2_low, z2_high = zone_hr(
        hr_max, 65, 75
    )

    if workout_type == "Endurance":
        return (
            "Riscaldamento: 15' in Z2.\n"
            f"Endurance: {max(20, duration - 30)}' "
            f"con FC prevalentemente {z2_low}-{z2_high} bpm.\n"
            "Evita di inseguire la FC nei primi minuti: "
            "lasciala salire gradualmente.\n"
            "Defaticamento: 15' facili."
        )

    if workout_type == "Tempo":
        return (
            "Riscaldamento: 15' in Z2.\n"
            "3 x 8' a ritmo sostenuto controllato, "
            "circa 80-87% FCmax.\n"
            "Recupero: 4' facili tra le ripetute.\n"
            "Completa il resto in Z2.\n"
            "Defaticamento finale."
        )

    if workout_type == "Sweet Spot":
        return (
            "Riscaldamento: 15' in Z2.\n"
            "3 x 8' a ritmo forte ma sostenibile, "
            "circa 85-90% FCmax.\n"
            "Recupero: 4' facili.\n"
            "Non inseguire subito il target: "
            "la FC deve salire progressivamente.\n"
            "Defaticamento finale."
        )

    if workout_type == "Threshold":
        return (
            "Riscaldamento: 15' in Z2.\n"
            "3 x 8' in salita a circa 88-94% FCmax.\n"
            "Recupero: 4' molto facili.\n"
            "Mantieni ritmo regolare e non partire oltre il target."
        )

    if workout_type == "VO2max":
        return (
            "Riscaldamento: 20' progressivo.\n"
            "5 x 3' in salita a intensità molto alta.\n"
            "La FC dovrebbe avvicinarsi a 90-95% FCmax "
            "verso la parte finale delle ripetute.\n"
            "Recupero: 3' facili.\n"
            "La FC è un riferimento ritardato: "
            "non accelerare solo per raggiungere subito il numero."
        )

    if workout_type == "Recovery":
        return (
            "45-60' molto facili.\n"
            f"FC indicativamente sotto {z2_high} bpm.\n"
            "Nessuna salita tirata e nessun intervallo."
        )

    return (
        f"Riscaldamento: 15' in Z2.\n"
        f"{max(30, duration - 30)}' in endurance "
        f"con FC prevalentemente {z2_low}-{z2_high} bpm.\n"
        "Defaticamento: 15'."
    )


def choose_workout_type(day_index, state, goal):
    # Progressione prudente: endurance -> qualità -> endurance.
    # Se l'atleta è affaticato, niente VO2/threshold.
    if state == "fatigued":
        return "Recovery"

    if day_index == 0:
        return "Endurance"

    if day_index == 1:
        return "Sweet Spot"

    if day_index == 2:
        return "Recovery"

    if day_index == 3:
        return "VO2max"

    if day_index == 4:
        return "Endurance"

    return "Endurance"


def build_week_plan(
    start_date,
    ftp,
    hr_max,
    fitness,
    fatigue,
    form,
    indoor_days,
    outdoor_days,
    goal
):
    state = coach_state(
        fitness,
        fatigue,
        form
    )

    available = [
        0,  # lunedì
        1,  # martedì
        3,  # giovedì
        4,  # venerdì
        5   # sabato
    ]

    durations = {
        0: 90,
        1: 90,
        3: 60,
        4: 60,
        5: 180
    }

    plan = []

    for day_index in available:
        current_date = start_date + timedelta(
            days=day_index
        )

        workout_type = choose_workout_type(
            day_index,
            state,
            goal
        )

        duration = durations[day_index]

        # Sabato resta prevalentemente endurance.
        if day_index == 5:
            workout_type = "Endurance"

        # V1: giorni selezionati dall'utente.
        if day_index in indoor_days:
            mode = "Indoor"
            description = generate_indoor_workout(
                workout_type,
                duration,
                ftp
            )
            target = "POWER"
            indoor = True

        elif day_index in outdoor_days:
            mode = "Outdoor"
            description = generate_outdoor_workout(
                workout_type,
                duration,
                hr_max
            )
            target = "HR"
            indoor = False

        else:
            # Se non specificato, usa indoor per la prima versione.
            mode = "Indoor"
            description = generate_indoor_workout(
                workout_type,
                duration,
                ftp
            )
            target = "POWER"
            indoor = True

        name = (
            f"{mode} • {workout_type}"
        )

        plan.append(
            {
                "date": current_date,
                "duration": duration,
                "name": name,
                "type": workout_type,
                "mode": mode,
                "description": description,
                "target": target,
                "indoor": indoor
            }
        )

    return plan, state


def event_exists_on_date(events, target_date):
    for event in events:
        start = parse_event_datetime(
            event.get("start_date_local")
        )

        if start and start.date() == target_date:
            return True

    return False


def create_coach_week(
    plan,
    events
):
    created = []
    skipped = []

    for workout in plan:
        target_date = workout["date"]

        if event_exists_on_date(
            events,
            target_date
        ):
            skipped.append(
                target_date
            )
            continue

        start_hour = 18 if workout["mode"] == "Indoor" else 9

        start_datetime = datetime.combine(
            target_date,
            datetime.min.time()
        ).replace(
            hour=start_hour,
            minute=0,
            second=0
        )

        end_datetime = (
            start_datetime +
            timedelta(
                minutes=workout["duration"]
            )
        )

        result = create_intervals_event(
            name=workout["name"],
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            description=workout["description"],
            indoor=workout["indoor"],
            target=workout["target"]
        )

        if result:
            created.append(result)

    return created, skipped


# =========================
# LOAD DATA
# =========================

if st.session_state.events_cache is None:
    refresh_events()

if st.session_state.wellness_cache is None:
    refresh_wellness()

events = st.session_state.events_cache or []
wellness = st.session_state.wellness_cache

# =========================
# SIDEBAR PROFILE
# =========================

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

watts_per_kg = ftp / weight

fitness = None
fatigue = None
form = None

if wellness:
    fitness = wellness.get("ctl")
    fatigue = wellness.get("atl")
    form = wellness.get("tsb")

    if fitness is None:
        fitness = wellness.get("ctlLoad")

    if fatigue is None:
        fatigue = wellness.get("atlLoad")


# =========================
# PAGE HELPERS
# =========================

def show_page_title(title, subtitle=None):
    st.title(title)

    if subtitle:
        st.caption(subtitle)


def show_workout_detail(event):
    st.divider()
    st.subheader("Dettagli allenamento")

    name = event.get(
        "name",
        "Allenamento"
    )

    completed = is_event_completed(event)

    if completed:
        st.markdown(f"### ✅ {name}")
    else:
        st.markdown(f"### {name}")

    start = parse_event_datetime(
        event.get("start_date_local")
    )

    duration = get_event_duration(event)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Data",
            start.strftime("%d/%m/%Y") if start else "-"
        )

    with col2:
        st.metric(
            "Ora",
            start.strftime("%H:%M") if start else "-"
        )

    with col3:
        st.metric(
            "Durata",
            f"{duration} min"
        )

    if completed:
        st.success(
            "Allenamento completato"
        )

    st.markdown("#### Descrizione")

    description = event.get(
        "description",
        ""
    )

    if description:
        st.markdown(
            f"""
            <div class="workout-description">
            {description}
            </div>
            """,
            unsafe_allow_html=True
        )
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


# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    show_page_title(
        "Dashboard",
        "Il tuo centro di controllo per il ciclismo."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚡ FTP",
            f"{ftp} W",
            f"{watts_per_kg:.2f} W/kg"
        )

    with col2:
        st.metric(
            "💪 Fitness",
            f"{fitness:.0f}" if fitness is not None else "—"
        )

    with col3:
        st.metric(
            "😴 Fatigue",
            f"{fatigue:.0f}" if fatigue is not None else "—"
        )

    with col4:
        st.metric(
            "📈 Form",
            f"{form:+.0f}" if form is not None else "—"
        )

    st.divider()

    if st.button(
        "🔄 Aggiorna dati",
        key="dashboard_refresh"
    ):
        refresh_events()
        refresh_wellness()
        st.rerun()

    st.subheader("🏋️ Prossimo allenamento")

    today = date.today()

    upcoming = []

    for event in events:
        start = parse_event_datetime(
            event.get("start_date_local")
        )

        if start and start.date() >= today:
            upcoming.append(event)

    upcoming.sort(
        key=lambda x: x.get(
            "start_date_local",
            ""
        )
    )

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

        completed = is_event_completed(event)

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [3, 1, 1]
            )

            with col1:
                prefix = "✅ " if completed else ""
                st.markdown(
                    f"### {prefix}{event.get('name', 'Allenamento')}"
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

    st.subheader("📊 Stato allenamento")

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        st.metric(
            "Fitness / CTL",
            f"{fitness:.0f}" if fitness is not None else "—"
        )

    with status_col2:
        st.metric(
            "Fatigue / ATL",
            f"{fatigue:.0f}" if fatigue is not None else "—"
        )

    with status_col3:
        st.metric(
            "Form / TSB",
            f"{form:+.0f}" if form is not None else "—"
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

    st.subheader("📅 Prossimi allenamenti")

    shown = 0

    sorted_events = sorted(
        events,
        key=lambda x: x.get(
            "start_date_local",
            ""
        )
    )

    for event in sorted_events:

        if shown >= 5:
            break

        start = parse_event_datetime(
            event.get("start_date_local")
        )

        if start and start.date() >= today:

            duration = get_event_duration(event)
            completed = is_event_completed(event)

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 1.5, 1]
                )

                with col1:
                    prefix = "✅ " if completed else ""
                    st.write(
                        f"**{prefix}{event.get('name', 'Allenamento')}**"
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


# =========================
# CALENDAR
# =========================

elif page == "Calendario":

    show_page_title(
        "Calendario",
        "La tua settimana di allenamento sincronizzata con Intervals.icu."
    )

    current_monday = get_monday(
        date.today()
    )

    selected_monday, selected_sunday = (
        get_calendar_week()
    )

    nav1, nav2, nav3 = st.columns(
        [1, 3, 1]
    )

    with nav1:
        if st.button(
            "← Settimana precedente",
            key="previous_week"
        ):
            st.session_state.calendar_week_offset -= 1
            st.rerun()

    with nav2:

        if selected_monday == current_monday:

            st.markdown(
                "<h3 style='text-align:center;'>"
                "Settimana corrente"
                "</h3>",
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"<h3 style='text-align:center;'>"
                f"{selected_monday.strftime('%d/%m')} — "
                f"{selected_sunday.strftime('%d/%m/%Y')}"
                f"</h3>",
                unsafe_allow_html=True
            )

    with nav3:

        if st.button(
            "Settimana successiva →",
            key="next_week"
        ):
            st.session_state.calendar_week_offset += 1
            st.rerun()

    st.caption(
        f"Dal {selected_monday.strftime('%d/%m/%Y')} "
        f"al {selected_sunday.strftime('%d/%m/%Y')}"
    )

    st.divider()

    if st.button(
        "🔄 Aggiorna calendario",
        key="refresh_calendar"
    ):
        refresh_events()
        st.rerun()

    week_events = []

    for event in events:

        start = parse_event_datetime(
            event.get("start_date_local")
        )

        if not start:
            continue

        if (
            selected_monday
            <= start.date()
            <= selected_sunday
        ):
            week_events.append(event)

    week_events.sort(
        key=lambda x: x.get(
            "start_date_local",
            ""
        )
    )

    if not week_events:

        st.info(
            "Nessun allenamento programmato "
            "in questa settimana."
        )

    else:

        for event in week_events:

            start = parse_event_datetime(
                event.get("start_date_local")
            )

            duration = get_event_duration(event)

            completed = is_event_completed(event)

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(
                    [1.5, 3.5, 1.5, 1]
                )

                with col1:

                    if start:

                        prefix = "✅ " if completed else ""

                        st.markdown(
                            f"### {prefix}{start.strftime('%a')}"
                        )

                        st.caption(
                            start.strftime(
                                "%d/%m/%Y"
                            )
                        )

                        st.caption(
                            start.strftime("%H:%M")
                        )

                with col2:

                    prefix = "✅ " if completed else ""

                    st.markdown(
                        f"**{prefix}{event.get('name', 'Allenamento')}**"
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

                    if completed:
                        st.success(
                            "Completato"
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


# =========================
# WORKOUTS
# =========================

elif page == "Allenamenti":

    show_page_title(
        "Allenamenti",
        "I prossimi 5 allenamenti presenti su Intervals.icu."
    )

    today = date.today()

    future_events = []

    for event in events:

        start = parse_event_datetime(
            event.get("start_date_local")
        )

        if start and start.date() >= today:
            future_events.append(event)

    future_events.sort(
        key=lambda x: x.get(
            "start_date_local",
            ""
        )
    )

    future_events = future_events[:5]

    if not future_events:

        st.info(
            "Non ci sono prossimi allenamenti programmati."
        )

    else:

        for event in future_events:

            start = parse_event_datetime(
                event.get("start_date_local")
            )

            duration = get_event_duration(event)

            completed = is_event_completed(event)

            with st.container(border=True):

                if start:

                    prefix = "✅ " if completed else ""

                    st.caption(
                        f"{prefix}{start.strftime('%d/%m/%Y — %H:%M')}"
                    )

                prefix = "✅ " if completed else ""

                st.subheader(
                    f"{prefix}{event.get('name', 'Allenamento')}"
                )

                st.write(
                    f"Durata: **{duration} minuti**"
                )

                if completed:

                    st.success(
                        "Allenamento completato"
                    )

                if st.button(
                    "Apri allenamento",
                    key=f"workout_{event.get('id')}"
                ):

                    st.session_state.selected_event = (
                        event.get("id")
                    )

                    st.rerun()


# =========================
# ANALYSIS
# =========================

elif page == "Analisi":

    show_page_title(
        "Analisi",
        "Analisi della tua situazione attuale."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Fitness",
            f"{fitness:.0f}" if fitness is not None else "—"
        )

    with col2:
        st.metric(
            "Fatigue",
            f"{fatigue:.0f}" if fatigue is not None else "—"
        )

    with col3:
        st.metric(
            "Form",
            f"{form:+.0f}" if form is not None else "—"
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
        "storici e l'analisi automatica della risposta "
        "agli allenamenti."
    )


# =========================
# AI COACH
# =========================

elif page == "AI Coach":

    show_page_title(
        "AI Coach",
        "Il coach che crea, analizza e adatta il tuo piano."
    )

    state = coach_state(
        fitness,
        fatigue,
        form
    )

    st.markdown(
        f"""
        <div class="coach-box">
            <h3>🧠 Stato attuale del Coach</h3>
            <p>
                <b>Fitness:</b> {f"{fitness:.0f}" if fitness is not None else "—"}
                &nbsp;&nbsp;
                <b>Fatigue:</b> {f"{fatigue:.0f}" if fatigue is not None else "—"}
                &nbsp;&nbsp;
                <b>Form:</b> {f"{form:+.0f}" if form is not None else "—"}
            </p>
            <p><b>Stato interpretato:</b> {state}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("⚙️ Generazione del piano")

    st.write(
        "Questa prima versione crea una settimana strutturata "
        "e la invia direttamente a Intervals.icu."
    )

    col1, col2 = st.columns(2)

    with col1:

        indoor_days_names = st.multiselect(
            "Giorni Indoor",
            [
                "Lunedì",
                "Martedì",
                "Giovedì",
                "Venerdì",
                "Sabato"
            ],
            default=[
                "Lunedì",
                "Martedì",
                "Giovedì",
                "Venerdì"
            ]
        )

    with col2:

        outdoor_days_names = st.multiselect(
            "Giorni Outdoor",
            [
                "Lunedì",
                "Martedì",
                "Giovedì",
                "Venerdì",
                "Sabato"
            ],
            default=[
                "Sabato"
            ]
        )

    day_map = {
        "Lunedì": 0,
        "Martedì": 1,
        "Giovedì": 3,
        "Venerdì": 4,
        "Sabato": 5
    }

    indoor_days = {
        day_map[name]
        for name in indoor_days_names
    }

    outdoor_days = {
        day_map[name]
        for name in outdoor_days_names
    }

    overlap = indoor_days.intersection(
        outdoor_days
    )

    if overlap:

        st.warning(
            "Hai selezionato lo stesso giorno sia Indoor "
            "che Outdoor. Scegli una sola modalità per ogni giorno."
        )

    if st.button(
        "🧠 Genera anteprima della settimana",
        key="preview_coach_week"
    ):

        if overlap:

            st.error(
                "Correggi prima i giorni sovrapposti."
            )

        else:

            next_monday = get_monday(
                date.today()
            )

            plan, plan_state = build_week_plan(
                start_date=next_monday,
                ftp=ftp,
                hr_max=hr_max,
                fitness=fitness,
                fatigue=fatigue,
                form=form,
                indoor_days=indoor_days,
                outdoor_days=outdoor_days,
                goal=goal
            )

            st.session_state.coach_preview = {
                "plan": plan,
                "state": plan_state
            }

    preview_data = st.session_state.get(
        "coach_preview"
    )

    if preview_data:

        st.divider()

        st.subheader(
            "📋 Anteprima generata dal Coach"
        )

        st.caption(
            "Controlla il piano prima di inviarlo a Intervals.icu."
        )

        for workout in preview_data["plan"]:

            mode_icon = (
                "🏠"
                if workout["mode"] == "Indoor"
                else "🌳"
            )

            with st.container(border=True):

                st.markdown(
                    f"### {mode_icon} {workout['name']}"
                )

                st.write(
                    f"**{workout['date'].strftime('%A %d/%m')}** "
                    f"• {workout['duration']} min"
                )

                st.markdown(
                    f"""
                    <div class="workout-description">
                    {workout['description']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.divider()

        st.warning(
            "Il pulsante seguente creerà gli allenamenti "
            "su Intervals.icu. I giorni che hanno già un "
            "allenamento non verranno sovrascritti."
        )

        if st.button(
            "🚀 Crea questa settimana su Intervals.icu",
            key="create_coach_week"
        ):

            created, skipped = create_coach_week(
                preview_data["plan"],
                events
            )

            refresh_events()

            if created:

                st.success(
                    f"Creati {len(created)} allenamenti su Intervals.icu."
                )

            if skipped:

                skipped_text = ", ".join(
                    d.strftime("%d/%m")
                    for d in skipped
                )

                st.info(
                    "Giorni saltati perché avevano già "
                    f"un allenamento: {skipped_text}"
                )

            if not created and not skipped:

                st.error(
                    "Nessun allenamento è stato creato."
                )

    st.divider()

    st.subheader("🚧 Prossimi moduli del Coach")

    st.write(
        """
        La base di generazione è ora pronta. I prossimi moduli saranno:

        - analisi degli allenamenti realmente svolti;
        - confronto programmato vs reale;
        - analisi di potenza e frequenza cardiaca;
        - RPE e sensazioni dell'atleta;
        - carico acuto e cronico;
        - rilevamento degli allenamenti saltati;
        - modifica automatica dei giorni successivi;
        - periodizzazione su più settimane;
        - test FTP e aggiornamento automatico delle zone;
        - pianificazione gara;
        - conoscenze scientifiche aggiornate;
        - vero modulo AI decisionale;
        - aggiornamento automatico di Intervals.icu.
        """
    )


# =========================
# PROFILE
# =========================

elif page == "Profilo":

    show_page_title(
        "Profilo",
        "Le tue impostazioni e le app collegate."
    )

    st.subheader("Dati atleta")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Peso:** {weight:.1f} kg"
        )

        st.write(
            f"**FTP:** {ftp} W"
        )

        st.write(
            f"**FTP relativo:** {watts_per_kg:.2f} W/kg"
        )

    with col2:

        st.write(
            f"**FC max:** {hr_max} bpm"
        )

        st.write(
            f"**Obiettivo:** {goal}"
        )

    st.divider()

    st.subheader("🔗 App collegate")

    st.markdown(
        """
        <div class="connected-app">
            <h4>🟢 Intervals.icu</h4>
            <p>
                Collegato e sincronizzato.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="connected-app">
            <h4>⚪ Garmin</h4>
            <p>
                Integrazione prevista.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="connected-app">
            <h4>⚪ Strava</h4>
            <p>
                Integrazione prevista.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="connected-app">
            <h4>⚪ MyWhoosh</h4>
            <p>
                Integrazione prevista.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# SELECTED WORKOUT
# =========================

if st.session_state.selected_event is not None:

    selected = find_event_by_id(
        st.session_state.selected_event
    )

    if selected:

        show_workout_detail(
            selected
        )


# =========================
# EDIT FORM
# =========================

if st.session_state.edit_event is not None:

    show_edit_form(
        st.session_state.edit_event
    )
