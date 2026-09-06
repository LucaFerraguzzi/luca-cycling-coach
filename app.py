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

if "activities_cache" not in st.session_state:
    st.session_state.activities_cache = None

if "calendar_week_offset" not in st.session_state:
    st.session_state.calendar_week_offset = 0

if "coach_message" not in st.session_state:
    st.session_state.coach_message = None

if "coach_chat" not in st.session_state:
    st.session_state.coach_chat = []

if "coach_start_date" not in st.session_state:
    st.session_state.coach_start_date = None

if "coach_blackout_dates" not in st.session_state:
    st.session_state.coach_blackout_dates = set()

if "coach_outdoor_until" not in st.session_state:
    st.session_state.coach_outdoor_until = None

if "coach_mode_week" not in st.session_state:
    st.session_state.coach_mode_week = {
        0: "Indoor",
        1: "Indoor",
        3: "Indoor",
        4: "Indoor",
        5: "Outdoor"
    }

if "coach_plan_horizon" not in st.session_state:
    st.session_state.coach_plan_horizon = 11

if "coach_preview" not in st.session_state:
    st.session_state.coach_preview = None

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


def get_intervals_activities(days=90):
    today = date.today()
    oldest = today - timedelta(days=days)

    url = f"{BASE_URL}/athlete/{INTERVALS_ATHLETE_ID}/activities"
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
        if not isinstance(data, list):
            return []
        return data
    except requests.exceptions.RequestException:
        return []


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
    description,
    indoor=None,
    target=None
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

    if indoor is not None:
        payload["indoor"] = bool(indoor)
    if target is not None:
        payload["target"] = target

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
# EVENT MANAGEMENT
# =========================

def delete_intervals_event(event_id):
    url = f"{BASE_URL}/athlete/{INTERVALS_ATHLETE_ID}/events/{event_id}"
    try:
        response = requests.delete(
            url,
            auth=intervals_auth(),
            timeout=20
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Errore durante l'eliminazione su Intervals.icu: {e}")
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


def refresh_activities():
    st.session_state.activities_cache = get_intervals_activities(180)


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


def coach_state(fitness, fatigue, form, fitness_trend=None):
    if fitness is None or fatigue is None or form is None:
        return "unknown"

    if form < -20:
        return "overreaching"

    if form < -10:
        return "loaded"

    if form > 15:
        return "recovery"

    if fitness_trend is not None and fitness_trend < -2.0:
        return "detraining"

    if fitness_trend is not None and fitness_trend > 2.0:
        return "training"

    return "maintenance"


def calculate_hr_training_load(activity, hr_max):
    """Stima del carico quando non è disponibile la potenza.

    Preferisce il training load già calcolato da Intervals.icu;
    altrimenti usa durata + FC media + FC max come stima HR-based.
    """
    existing = activity.get("icu_training_load")
    if existing is not None:
        try:
            return float(existing)
        except (TypeError, ValueError):
            pass

    moving_time = activity.get("moving_time") or activity.get("elapsed_time")
    avg_hr = activity.get("average_hr") or activity.get("avg_hr")

    if not moving_time or not avg_hr or not hr_max:
        return 0.0

    minutes = float(moving_time) / 60.0
    intensity = min(1.0, max(0.0, float(avg_hr) / float(hr_max)))

    # Carico semplice e robusto basato sulla FC: aumenta con durata
    # e intensità relativa, senza richiedere un misuratore di potenza.
    relative = max(0.05, (intensity - 0.50) / 0.50)
    return minutes * relative * 0.75


def calculate_coach_load_metrics(activities, hr_max):
    """Calcola Fitness/Fatigue/Form del Coach anche senza watt.

    Usa i carichi delle attività degli ultimi 90 giorni e due medie
    esponenziali con costanti 42 e 7 giorni, analoghe al modello
    Fitness/Fatigue.
    """
    today = date.today()
    daily = {}

    for activity in activities:
        if str(activity.get("type", "")).lower() not in {"ride", "cycling", "virtualride"}:
            continue
        start = parse_event_datetime(activity.get("start_date_local"))
        if not start:
            continue
        d = start.date()
        if d > today:
            continue
        load = calculate_hr_training_load(activity, hr_max)
        if load > 0:
            daily[d] = daily.get(d, 0.0) + load

    # Seed a zero-load day before the historical window.
    ctl = 0.0
    atl = 0.0
    history = []

    for days_ago in range(90, -1, -1):
        d = today - timedelta(days=days_ago)
        load = daily.get(d, 0.0)
        ctl += (load - ctl) / 42.0
        atl += (load - atl) / 7.0
        history.append({"date": d, "ctl": ctl, "atl": atl})

    if not history:
        return None, None, None, None, []

    current = history[-1]
    old = history[-15] if len(history) >= 15 else history[0]
    trend = current["ctl"] - old["ctl"]
    form = current["ctl"] - current["atl"]

    return current["ctl"], current["atl"], form, trend, history


def state_label(state):
    labels = {
        "detraining": "🔵 Detraining",
        "training": "🟢 Training",
        "maintenance": "🟡 Mantenimento",
        "loaded": "🟠 Carico elevato",
        "overreaching": "🔴 Overreaching",
        "recovery": "🟢 Recupero / fresco",
        "unknown": "⚪ Dati insufficienti"
    }
    return labels.get(state, state)


def zone_power(ftp, percent):
    return round(ftp * percent / 100)


def zone_hr_name(zone):
    return zone


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


def generate_outdoor_workout(workout_type, duration, hr_max):
    """Workout outdoor espresso esclusivamente in zone FC.

    Non mostra bpm nel workout: l'atleta segue le proprie zone FC
    configurate sul dispositivo.
    """
    if workout_type == "Endurance":
        return (
            "Riscaldamento: 15' in Z1-Z2.\n"
            f"Endurance: {max(20, duration - 30)}' prevalentemente in Z2.\n"
            "Mantieni la FC stabile e lascia salire gradualmente la FC.\n"
            "Defaticamento: 15' in Z1-Z2."
        )

    if workout_type == "Tempo":
        return (
            "Riscaldamento: 15' in Z2.\n"
            "3 x 8' in Z3.\n"
            "Recupero: 4' in Z1-Z2 tra le ripetute.\n"
            "Completa il resto in Z2.\n"
            "Defaticamento finale in Z1-Z2."
        )

    if workout_type == "Sweet Spot":
        return (
            "Riscaldamento: 15' in Z2.\n"
            "3 x 8' in Z3 alta / vicino alla soglia.\n"
            "Recupero: 4' in Z1-Z2.\n"
            "La FC ha inerzia: non inseguire il target nei primi secondi.\n"
            "Defaticamento finale in Z1-Z2."
        )

    if workout_type == "Threshold":
        return (
            "Riscaldamento: 15' progressivo in Z2.\n"
            "3 x 8' in Z4, ritmo regolare e controllato.\n"
            "Recupero: 4' in Z1-Z2.\n"
            "Non partire sopra il target: lascia salire la FC progressivamente.\n"
            "Defaticamento in Z1-Z2."
        )

    if workout_type == "VO2max":
        return (
            "Riscaldamento: 20' progressivo da Z1 a Z2.\n"
            "5 x 3' ad alta intensità, puntando alla Z5 nella parte finale di ogni ripetuta.\n"
            "Recupero: 3' in Z1-Z2.\n"
            "La FC è un riferimento ritardato: non accelerare solo per raggiungere subito Z5.\n"
            "Defaticamento finale in Z1-Z2."
        )

    if workout_type == "Recovery":
        return (
            "45-60' molto facili in Z1-Z2.\n"
            "Nessuna salita tirata e nessun intervallo.\n"
            "Obiettivo: recuperare, non allenare l'intensità."
        )

    return (
        f"Riscaldamento: 15' in Z2.\n"
        f"{max(30, duration - 30)}' prevalentemente in Z2.\n"
        "Defaticamento: 15' in Z1-Z2."
    )


def choose_workout_type(day_index, state, goal):
    # Se il carico è alto, il Coach protegge il recupero.
    if state in {"overreaching", "loaded"}:
        return "Recovery"
    if state == "recovery" and day_index in {1, 3}:
        return "Endurance"

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
    goal,
    fitness_trend=None
):
    state = coach_state(
        fitness,
        fatigue,
        form,
        fitness_trend
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
# CONVERSATIONAL COACH
# =========================

COACH_WEEKDAY_MAP = {
    0: "Lunedì",
    1: "Martedì",
    2: "Mercoledì",
    3: "Giovedì",
    4: "Venerdì",
    5: "Sabato",
    6: "Domenica"
}

COACH_WORKOUT_TYPES = [
    "Endurance", "Tempo", "Sweet Spot", "Threshold", "VO2max", "Recovery"
]


def parse_italian_date(day_text, month_text=None, year=None):
    try:
        day_num = int(day_text)
        months = {
            "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
            "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
            "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
        }
        if month_text:
            month_num = months.get(month_text.lower())
        else:
            month_num = date.today().month
        if not month_num:
            return None
        return date(year or date.today().year, month_num, day_num)
    except Exception:
        return None


def parse_coach_dates(text):
    """Riconosce i principali modi naturali con cui Luca indica date."""
    t = text.lower().replace("–", "-").replace("—", "-")
    months = r"gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre"
    dates = []

    import re

    # 9-10 settembre / 9 al 10 settembre
    m = re.search(r"\b(\d{1,2})\s*(?:-|al|a)\s*(\d{1,2})\s+(" + months + r")\b", t)
    if m:
        d1 = parse_italian_date(m.group(1), m.group(3))
        d2 = parse_italian_date(m.group(2), m.group(3))
        if d1 and d2 and d2 >= d1:
            return [d1 + timedelta(days=i) for i in range((d2 - d1).days + 1)]

    # 9 e 10 settembre
    m = re.search(r"\b(\d{1,2})\s*(?:e|,|/)\s*(\d{1,2})\s+(" + months + r")\b", t)
    if m:
        d1 = parse_italian_date(m.group(1), m.group(3))
        d2 = parse_italian_date(m.group(2), m.group(3))
        if d1 and d2:
            return [d1, d2]

    # Singola data con mese
    for m in re.finditer(r"\b(\d{1,2})\s+(" + months + r")\b", t):
        d = parse_italian_date(m.group(1), m.group(2))
        if d:
            dates.append(d)

    # Solo giorno numerico, utile quando il mese è già evidente dal contesto
    if not dates:
        for m in re.finditer(r"\b(\d{1,2})[/-](\d{1,2})\b", t):
            try:
                dates.append(date(date.today().year, int(m.group(2)), int(m.group(1))))
            except Exception:
                pass

    # deduplica mantenendo l'ordine
    result = []
    for d in dates:
        if d not in result:
            result.append(d)
    return result


def workout_type_from_event(event):
    name = str(event.get("name", ""))
    for workout_type in COACH_WORKOUT_TYPES:
        if workout_type.lower() in name.lower():
            return workout_type
    return "Endurance"


def mode_for_date(target_date):
    outdoor_until = st.session_state.get("coach_outdoor_until")
    if outdoor_until and target_date <= outdoor_until:
        return "Outdoor"
    return st.session_state.coach_mode_week.get(target_date.weekday(), "Indoor")


def rolling_plan(start_date, horizon_days=11):
    """Genera almeno una settimana, preferibilmente 1.5 settimane."""
    state = coach_state(fitness, fatigue, form, fitness_trend)
    plan = []
    available_weekdays = {0, 1, 3, 4, 5}

    for offset in range(horizon_days):
        current_date = start_date + timedelta(days=offset)
        if current_date.weekday() not in available_weekdays:
            continue
        if current_date in st.session_state.coach_blackout_dates:
            continue

        # Il giorno della settimana determina la funzione fisiologica.
        day_index = current_date.weekday()
        workout_type = choose_workout_type(day_index, state, goal)
        if day_index == 5:
            workout_type = "Endurance"

        duration = {0: 90, 1: 90, 3: 60, 4: 60, 5: 180}[day_index]
        mode = mode_for_date(current_date)

        if mode == "Indoor":
            description = generate_indoor_workout(workout_type, duration, ftp)
            target = "POWER"
            indoor = True
        else:
            description = generate_outdoor_workout(workout_type, duration, hr_max)
            target = "HR"
            indoor = False

        plan.append({
            "date": current_date,
            "duration": duration,
            "name": f"{mode} • {workout_type}",
            "type": workout_type,
            "mode": mode,
            "description": description,
            "target": target,
            "indoor": indoor
        })

    return plan, state


def create_rolling_plan(start_date=None, horizon_days=11):
    """Prepara il piano senza caricarlo: il Coach lo mostra prima dell'upload."""
    start_date = start_date or date.today()
    plan, state = rolling_plan(start_date, horizon_days)
    current_events = st.session_state.events_cache or []
    pending = []
    skipped = []
    for workout in plan:
        if event_exists_on_date(current_events, workout["date"]):
            skipped.append(workout["date"])
        else:
            pending.append(workout)
    st.session_state.coach_preview = {
        "plan": pending,
        "state": state,
        "skipped": skipped,
        "start": start_date,
    }
    return pending, state, [], skipped


def upload_coach_preview():
    preview = st.session_state.get("coach_preview")
    if not preview:
        return [], []
    created, skipped = create_coach_week(
        preview["plan"],
        st.session_state.events_cache or []
    )
    refresh_events()
    st.session_state.coach_preview = None
    return created, skipped


def ensure_coach_horizon():
    """Non carica automaticamente: prepara solo una nuova anteprima quando serve."""
    start = st.session_state.get("coach_start_date")
    if not start:
        return 0
    future = [
        e for e in (st.session_state.events_cache or [])
        if (parse_event_datetime(e.get("start_date_local"))
            and parse_event_datetime(e.get("start_date_local")).date() >= date.today())
    ]
    coach_events = [
        e for e in future
        if str(e.get("name", "")).lower().startswith(("indoor", "outdoor"))
    ]
    if len(coach_events) < 5 and not st.session_state.get("coach_preview"):
        create_rolling_plan(max(start, date.today()), st.session_state.coach_plan_horizon)
    return 0


def delete_workouts_on_dates(dates):
    deleted = []
    not_deleted = []
    current_events = st.session_state.events_cache or []

    for event in current_events:
        start = parse_event_datetime(event.get("start_date_local"))
        if not start or start.date() not in dates:
            continue
        if start.date() < date.today() or is_event_completed(event):
            continue
        if delete_intervals_event(event.get("id")):
            deleted.append(start.date())
        else:
            not_deleted.append(start.date())

    refresh_events()
    return sorted(set(deleted)), sorted(set(not_deleted))


def replan_after_changes(start_date=None):
    """Riempi automaticamente i giorni futuri liberi senza sovrascrivere gli allenamenti."""
    start_date = start_date or date.today()
    return create_rolling_plan(start_date, st.session_state.coach_plan_horizon)


def switch_event_mode(event, new_mode):
    start = parse_event_datetime(event.get("start_date_local"))
    if not start or start.date() < date.today() or is_event_completed(event):
        return False

    workout_type = workout_type_from_event(event)
    duration = get_event_duration(event)
    if new_mode == "Indoor":
        description = generate_indoor_workout(workout_type, duration, ftp)
        target = "POWER"
        indoor = True
    else:
        description = generate_outdoor_workout(workout_type, duration, hr_max)
        target = "HR"
        indoor = False

    return update_intervals_event(
        event_id=event.get("id"),
        name=f"{new_mode} • {workout_type}",
        start_datetime=start,
        end_datetime=start + timedelta(minutes=duration),
        description=description,
        indoor=indoor,
        target=target
    )


def switch_today_mode(new_mode):
    today = date.today()
    candidates = []
    for event in st.session_state.events_cache or []:
        start = parse_event_datetime(event.get("start_date_local"))
        if start and start.date() == today and not is_event_completed(event):
            candidates.append(event)

    if not candidates:
        return False, "Oggi non c'è un allenamento futuro da convertire."

    event = sorted(candidates, key=lambda e: e.get("start_date_local", ""))[0]
    ok = switch_event_mode(event, new_mode)
    if ok:
        refresh_events()
        return True, f"Ho convertito l'allenamento di oggi in {new_mode}."
    return False, "Non sono riuscito a modificare l'allenamento di oggi."


def apply_outdoor_until(until_date):
    st.session_state.coach_outdoor_until = until_date
    changed = 0
    for event in list(st.session_state.events_cache or []):
        start = parse_event_datetime(event.get("start_date_local"))
        if not start or start.date() < date.today() or start.date() > until_date:
            continue
        if is_event_completed(event):
            continue
        if switch_event_mode(event, "Outdoor"):
            changed += 1
    refresh_events()
    return changed


def coach_process_message(message):
    """Interpreta richieste operative comuni senza richiedere comandi rigidi."""
    import re
    text = message.strip()
    t = text.lower()
    responses = []

    # 1) Inizio allenamento serio
    dates = parse_coach_dates(text)
    if ("iniz" in t or "cominci" in t or "part" in t) and ("allen" in t or "ser" in t) and dates:
        start = dates[0]
        st.session_state.coach_start_date = start
        plan, state, created, skipped = replan_after_changes(start)
        responses.append(
            f"Perfetto. Considero **{start.strftime('%d/%m/%Y')}** come inizio del blocco serio. "
            f"Ho pianificato circa {st.session_state.coach_plan_horizon} giorni, rispettando stato, recupero e disponibilità. "
            f"Ho preparato **{len(plan)} allenamenti** in anteprima: controllali qui sotto e poi potrai caricarli su Intervals.icu."
        )

    # 2) Periodo outdoor-only
    if ("solo" in t and "outdoor" in t) or ("fino al" in t and "outdoor" in t):
        until_dates = dates
        if until_dates:
            until = max(until_dates)
            changed = apply_outdoor_until(until)
            _, _, created, _ = replan_after_changes(date.today())
            responses.append(
                f"Va bene: fino al **{until.strftime('%d/%m/%Y')}** imposto solo allenamenti Outdoor. "
                f"Ho convertito {changed} allenamenti esistenti e aggiunto {len(created)} sessioni mancanti."
            )

    # 3) Giorni fuori / niente allenamento
    if any(k in t for k in ["sono fuori", "non ci sono", "sono via", "non posso allenarmi", "fuori città"]):
        if dates:
            blackout = set(dates)
            st.session_state.coach_blackout_dates.update(blackout)
            deleted, failed = delete_workouts_on_dates(blackout)
            _, _, created, _ = replan_after_changes(max(date.today(), min(blackout) + timedelta(days=1)))
            date_text = ", ".join(d.strftime('%d/%m') for d in dates)
            response = f"Segnato: niente allenamento il **{date_text}**."
            if deleted:
                response += f" Ho eliminato {len(deleted)} allenamenti e preparato in anteprima i giorni successivi ({len(plan)} nuovi)."
            else:
                response += " Ho adattato il calendario successivo senza sovrascrivere gli allenamenti già presenti."
            if failed:
                response += " Alcuni allenamenti non sono stati eliminati per un errore di sincronizzazione."
            responses.append(response)

    # 4) Cambio di oggi outdoor <-> indoor
    if "oggi" in t and "indoor" in t and "outdoor" in t:
        new_mode = "Indoor" if ("outdoor ad indoor" in t or "outdoor a indoor" in t) else "Outdoor"
        ok, response = switch_today_mode(new_mode)
        responses.append(response)

    # 5) Richiesta esplicita di programmazione / ripianificazione
    if not responses and any(k in t for k in ["programma", "pianifica", "ripianifica", "crea gli allenamenti", "preparami"]):
        start = st.session_state.coach_start_date or date.today()
        _, state, created, skipped = replan_after_changes(start)
        responses.append(
            f"Fatto. Ho controllato i prossimi {st.session_state.coach_plan_horizon} giorni e preparato {len(plan)} allenamenti mancanti in anteprima. "
            f"Stato attuale: **{state_label(state)}**."
        )

    if not responses:
        responses.append(
            "Ti seguo. Per ora posso gestire direttamente richieste come: "
            "iniziare da una certa data, giorni in cui sei fuori, periodo solo Outdoor/Indoor, "
            "ripianificazione e cambio dell'allenamento di oggi tra Indoor e Outdoor. "
            "Esempio: *Dal 7 settembre cominciamo seriamente; il 9 e 10 sono fuori; fino al 13 solo Outdoor.*"
        )

    return "\n\n".join(responses)


# =========================
# LOAD DATA
# =========================

if st.session_state.events_cache is None:
    refresh_events()

if st.session_state.wellness_cache is None:
    refresh_wellness()

if st.session_state.activities_cache is None:
    refresh_activities()

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

activities = st.session_state.activities_cache or []

# Coach metrics: calcolate autonomamente anche senza watt.
fitness, fatigue, form, fitness_trend, coach_history = calculate_coach_load_metrics(
    activities, hr_max
)

# Se il calcolo HR non produce dati sufficienti, usiamo il riferimento
# di Intervals.icu come fallback.
if fitness is None and wellness:
    fitness = wellness.get("ctl") or wellness.get("ctlLoad")
if fatigue is None and wellness:
    fatigue = wellness.get("atl") or wellness.get("atlLoad")
if form is None and fitness is not None and fatigue is not None:
    form = fitness - fatigue

coach_status = coach_state(
    fitness, fatigue, form, fitness_trend
)

# Se il blocco del Coach è già stato avviato, mantiene automaticamente
# una finestra futura di circa 1.5 settimane senza sovrascrivere gli eventi esistenti.
# Il Coach non carica più automaticamente gli allenamenti su Intervals.icu:
# prima prepara una preview, poi l'utente decide quando inviarla.


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

    st.markdown(
        f"""<div class="coach-box">
        <h3>🚦 Stato attuale</h3>
        <p style="font-size:1.25rem;"><b>{state_label(coach_status)}</b></p>
        <p>Il Coach valuta l'andamento del carico, non solo la potenza: può quindi funzionare anche quando gli allenamenti non hanno watt.</p>
        </div>""",
        unsafe_allow_html=True
    )

    st.divider()

    if st.button(
        "🔄 Aggiorna dati",
        key="dashboard_refresh"
    ):
        refresh_events()
        refresh_wellness()
        refresh_activities()
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
        "Vista mensile dei tuoi allenamenti, sincronizzata con Intervals.icu."
    )

    # Stato mese corrente
    if "calendar_month_offset" not in st.session_state:
        st.session_state.calendar_month_offset = 0

    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    month_date = (first_of_month + timedelta(days=32 * st.session_state.calendar_month_offset)).replace(day=1)
    month_names = [
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]

    nav1, nav2, nav3 = st.columns([1, 4, 1])
    with nav1:
        if st.button("← Mese precedente", key="calendar_prev_month"):
            st.session_state.calendar_month_offset -= 1
            st.session_state.selected_event = None
            st.rerun()
    with nav2:
        st.markdown(
            f"<h2 style='text-align:center;margin:0'>{month_names[month_date.month-1]} {month_date.year}</h2>",
            unsafe_allow_html=True
        )
    with nav3:
        if st.button("Mese successivo →", key="calendar_next_month"):
            st.session_state.calendar_month_offset += 1
            st.session_state.selected_event = None
            st.rerun()

    st.write("")
    if st.button("📍 Torna a oggi", key="calendar_today"):
        st.session_state.calendar_month_offset = 0
        st.rerun()

    if st.button("🔄 Aggiorna calendario", key="refresh_calendar_month"):
        refresh_events()
        st.rerun()

    # Raggruppa gli allenamenti per giorno
    events_by_day = {}
    for event in events:
        start = parse_event_datetime(event.get("start_date_local"))
        if start and start.year == month_date.year and start.month == month_date.month:
            events_by_day.setdefault(start.date(), []).append(event)

    import calendar as pycalendar
    cal = pycalendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(month_date.year, month_date.month)

    st.markdown("""
    <style>
    .month-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:6px; margin-top:10px; }
    .day-head { text-align:center; font-weight:700; padding:8px 2px; color:#374151; }
    .day-cell { min-height:115px; border:1px solid #e5e7eb; border-radius:10px; padding:8px; background:#fff; }
    .day-out { background:#f9fafb; color:#9ca3af; }
    .day-number { font-weight:700; font-size:14px; margin-bottom:6px; }
    .today-dot { display:inline-block; border-radius:50%; width:25px; height:25px; line-height:25px; text-align:center; background:#111827; color:white; }
    .event-dot { margin:4px 0; padding:5px 7px; border-radius:7px; background:#f3f4f6; font-size:12px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
    .event-dot.completed { background:#ecfdf5; }
    </style>
    """, unsafe_allow_html=True)

    headers = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    header_html = "<div class='month-grid'>" + "".join(f"<div class='day-head'>{h}</div>" for h in headers) + "</div>"
    st.markdown(header_html, unsafe_allow_html=True)

    # HTML griglia + pulsanti Streamlit sotto ogni cella con eventi.
    for week_index, week in enumerate(weeks):
        cols = st.columns(7, gap="small")
        for col_index, day in enumerate(week):
            with cols[col_index]:
                in_month = day.month == month_date.month
                day_events = sorted(events_by_day.get(day, []), key=lambda e: e.get("start_date_local", ""))
                number_html = f"<span class='{'today-dot' if day == today else ''}'>{day.day}</span>"
                if not in_month:
                    st.markdown(f"<div style='color:#9ca3af;font-weight:700'>{number_html}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-weight:700;margin-bottom:4px'>{number_html}</div>", unsafe_allow_html=True)
                for ev_index, event in enumerate(day_events):
                    completed = is_event_completed(event)
                    icon = "✓" if completed else "•"
                    start_dt = parse_event_datetime(event.get("start_date_local"))
                    time_text = start_dt.strftime("%H:%M") if start_dt else ""
                    name = event.get("name", "Allenamento")
                    short_name = name.replace("Indoor • ", "🏠 ").replace("Outdoor • ", "🌳 ")
                    if completed:
                        short_name = "✓ " + short_name
                    st.markdown(
                        f"<div class='event-dot {'completed' if completed else ''}' title='{name}'>{time_text} {short_name}</div>",
                        unsafe_allow_html=True
                    )
                    if st.button("Apri", key=f"month_event_{event.get('id')}_{week_index}_{ev_index}", use_container_width=True):
                        st.session_state.selected_event = event.get("id")
                        st.rerun()
                if not day_events and in_month:
                    st.caption(" ")

    st.divider()
    st.caption("• = allenamento programmato   ✓ = completato   🏠 = Indoor   🌳 = Outdoor")


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

    st.subheader("🚦 Stato del carico")
    st.success(state_label(coach_status)) if coach_status in {"training", "recovery"} else st.warning(state_label(coach_status))
    if fitness_trend is not None:
        st.caption(f"Trend Fitness del Coach negli ultimi ~14 giorni: {fitness_trend:+.1f}")

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
        "Scrivimi normalmente cosa vuoi cambiare: il Coach aggiorna il calendario su Intervals.icu."
    )

    state = coach_state(fitness, fatigue, form, fitness_trend)

    st.markdown(
        f"""
        <div class="coach-box">
            <h3>🧠 Il tuo Coach</h3>
            <p><b>Stato:</b> {state_label(state)}</p>
            <p><b>Fitness:</b> {f"{fitness:.0f}" if fitness is not None else "—"}
            &nbsp;&nbsp; <b>Fatigue:</b> {f"{fatigue:.0f}" if fatigue is not None else "—"}
            &nbsp;&nbsp; <b>Form:</b> {f"{form:+.0f}" if form is not None else "—"}</p>
            <p>Il Coach lavora con una finestra mobile di circa 1 settimana e mezza e la aggiorna mano a mano.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("💬 Parla con il Coach")
    st.caption(
        "Non servono comandi precisi. Puoi scrivere come parleresti a un allenatore. "
        "Le modifiche vengono applicate direttamente al calendario."
    )

    examples = [
        "Dal 7 settembre cominciamo gli allenamenti seri",
        "Il 9 e 10 settembre sono fuori, elimina gli allenamenti e ripianifica",
        "Fino al 13 settembre solo allenamenti outdoor",
        "Cambia l'allenamento di oggi da outdoor a indoor"
    ]

    for example in examples:
        st.caption(f"💡 {example}")

    for role, content in st.session_state.coach_chat:
        with st.chat_message(role):
            st.markdown(content)

    message = st.chat_input("Scrivi al Coach…")

    if message:
        st.session_state.coach_chat.append(("user", message))
        response = coach_process_message(message)
        st.session_state.coach_chat.append(("assistant", response))
        st.rerun()

    preview_data = st.session_state.get("coach_preview")
    if preview_data:
        st.divider()
        st.subheader("👀 Anteprima allenamenti del Coach")
        st.caption("Il Coach li ha preparati ma NON li ha ancora caricati su Intervals.icu.")
        for workout in preview_data["plan"]:
            icon = "🏠" if workout["mode"] == "Indoor" else "🌳"
            with st.container(border=True):
                st.markdown(f"### {icon} {workout['name']}")
                st.write(f"**{COACH_WEEKDAY_MAP[workout['date'].weekday()]} {workout['date'].strftime('%d/%m/%Y')}** • {workout['duration']} min")
                st.markdown(f"<div class='workout-description'>{workout['description']}</div>", unsafe_allow_html=True)
        if preview_data["skipped"]:
            skipped_text = ", ".join(d.strftime("%d/%m") for d in preview_data["skipped"])
            st.info(f"Giorni già occupati e quindi non modificati: {skipped_text}")
        if st.button("🚀 Carica questi allenamenti su Intervals.icu", key="upload_coach_preview", use_container_width=True):
            created, skipped = upload_coach_preview()
            st.success(f"Caricati {len(created)} allenamenti su Intervals.icu.")
            if skipped:
                st.info("Alcuni giorni erano già occupati e sono stati saltati.")
            st.rerun()

    st.divider()
    st.subheader("⚙️ Regole attuali del piano")

    start_text = (
        st.session_state.coach_start_date.strftime("%d/%m/%Y")
        if st.session_state.coach_start_date else "Non impostata"
    )
    outdoor_until_text = (
        st.session_state.coach_outdoor_until.strftime("%d/%m/%Y")
        if st.session_state.coach_outdoor_until else "Nessun limite"
    )

    st.write(f"**Inizio blocco serio:** {start_text}")
    st.write(f"**Solo Outdoor fino a:** {outdoor_until_text}")
    st.write(f"**Finestra di programmazione:** {st.session_state.coach_plan_horizon} giorni")

    if st.session_state.coach_blackout_dates:
        blackout_text = ", ".join(
            d.strftime("%d/%m")
            for d in sorted(st.session_state.coach_blackout_dates)
            if d >= date.today()
        )
        st.write(f"**Giorni bloccati:** {blackout_text or 'nessuno'}")
    else:
        st.write("**Giorni bloccati:** nessuno")

    st.caption(
        "Settimana tipo attuale: lunedì e martedì Indoor, mercoledì riposo, "
        "giovedì e venerdì Indoor, sabato Outdoor, domenica riposo. "
        "Il Coach può cambiarla in base a ciò che gli chiedi."
    )

    if st.button("🔄 Controlla e completa i prossimi allenamenti", key="coach_replan_button"):
        start = st.session_state.coach_start_date or date.today()
        _, state, created, _ = replan_after_changes(start)
        st.success(
            f"Anteprima pronta: {len(st.session_state.get('coach_preview', {}).get('plan', []))} allenamenti da controllare. Stato: {state_label(state)}."
        )

    if st.session_state.coach_chat:
        if st.button("🗑️ Cancella conversazione", key="clear_coach_chat"):
            st.session_state.coach_chat = []
            st.rerun()

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
