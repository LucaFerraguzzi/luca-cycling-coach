import streamlit as st
import requests
from datetime import date, datetime, timedelta

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Luca Cycling Coach",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================

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

section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {
    background-color: white !important;
    color: #111827 !important;
}

h1, h2, h3, h4 {
    color: #111827 !important;
}

.stButton > button {
    background-color: #111827 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #374151 !important;
    color: white !important;
}

.workout-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    margin-bottom: 12px;
}

.workout-title {
    font-size: 19px;
    font-weight: 700;
    color: #111827;
}

.workout-meta {
    color: #4b5563;
    font-size: 14px;
    margin-top: 6px;
}

.day-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    padding: 14px;
    min-height: 170px;
}

.day-title {
    font-weight: 700;
    color: #111827;
    margin-bottom: 10px;
}

.rest-day {
    color: #9ca3af;
}

.detail-box {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 22px;
    margin-top: 20px;
}

.sync-box {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 10px;
    padding: 12px 15px;
    color: #065f46;
    margin-bottom: 20px;
}

.warning-box {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 10px;
    padding: 15px;
    color: #9a3412;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

if "editing_event" not in st.session_state:
    st.session_state.editing_event = None

if "calendar_week" not in st.session_state:
    st.session_state.calendar_week = date.today()

# ============================================================
# CREDENTIALS
# ============================================================

def get_intervals_credentials():
    try:
        athlete_id = st.secrets["INTERVALS_ATHLETE_ID"]
        api_key = st.secrets["INTERVALS_API_KEY"]
        return athlete_id, api_key
    except Exception:
        return None, None


# ============================================================
# LETTURA INTERVALS.ICU
# ============================================================

@st.cache_data(ttl=60)
def fetch_intervals_events(
    athlete_id,
    api_key,
    oldest,
    newest
):
    url = (
        f"https://intervals.icu/api/v1/athlete/"
        f"{athlete_id}/events"
    )

    params = {
        "oldest": oldest,
        "newest": newest
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=("API_KEY", api_key),
            timeout=15
        )

        if response.status_code == 200:
            return response.json(), None

        return [], (
            f"Errore Intervals.icu "
            f"{response.status_code}: "
            f"{response.text[:300]}"
        )

    except requests.exceptions.RequestException as e:
        return [], f"Errore di connessione: {e}"


def get_events_for_range(oldest, newest):

    athlete_id, api_key = get_intervals_credentials()

    if not athlete_id or not api_key:
        return [], False, (
            "Credenziali Intervals.icu non configurate."
        )

    events, error = fetch_intervals_events(
        athlete_id,
        api_key,
        oldest.isoformat(),
        newest.isoformat()
    )

    if error:
        return [], False, error

    return events, True, None


# ============================================================
# SCRITTURA INTERVALS.ICU
# ============================================================

def update_intervals_event(
    event_id,
    athlete_id,
    api_key,
    payload
):
    url = (
        f"https://intervals.icu/api/v1/athlete/"
        f"{athlete_id}/events/{event_id}"
    )

    try:
        response = requests.put(
            url,
            auth=("API_KEY", api_key),
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if response.status_code in [200, 201]:
            return True, response.json()

        return False, (
            f"Errore Intervals.icu "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    except requests.exceptions.RequestException as e:
        return False, f"Errore di connessione: {e}"


# ============================================================
# UTILITY
# ============================================================

DAY_NAMES = [
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica"
]


def get_monday(day):
    return day - timedelta(days=day.weekday())


def get_event_date(event):

    value = event.get("start_date_local")

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "")
        ).date()
    except Exception:
        return None


def format_date(value):

    if not value:
        return "—"

    try:
        return datetime.fromisoformat(
            value.replace("Z", "")
        ).strftime("%d/%m/%Y")
    except Exception:
        return str(value)[:10]


def format_time(value):

    if not value:
        return "—"

    try:
        return datetime.fromisoformat(
            value.replace("Z", "")
        ).strftime("%H:%M")
    except Exception:
        return "—"


def format_duration(seconds):

    if not seconds:
        return "—"

    minutes = round(float(seconds) / 60)

    if minutes < 60:
        return f"{minutes} min"

    hours = minutes // 60
    mins = minutes % 60

    if mins == 0:
        return f"{hours}h"

    return f"{hours}h {mins}m"


def format_load(event):

    value = event.get("icu_training_load")

    if value is None:
        value = event.get("load_target")

    if value is None:
        return "—"

    try:
        return str(round(float(value)))
    except Exception:
        return str(value)


def get_workout_events(events):

    return [
        event
        for event in events
        if event.get("category") == "WORKOUT"
    ]


def get_steps(event):

    workout_doc = event.get("workout_doc")

    if not workout_doc:
        return []

    return workout_doc.get("steps", [])


def describe_step(step, level=0):

    lines = []

    prefix = "  " * level

    if step.get("text"):
        lines.append(
            f"{prefix}{step['text']}"
        )

    if step.get("duration"):
        minutes = round(
            float(step["duration"]) / 60
        )
        lines.append(
            f"{prefix}• {minutes} min"
        )

    if step.get("reps"):
        lines.append(
            f"{prefix}• {step['reps']}x"
        )

    if step.get("power"):
        power = step["power"]

        if isinstance(power, dict):
            value = power.get("value")
            units = power.get("units", "")

            if value is not None:
                lines.append(
                    f"{prefix}• Potenza: "
                    f"{value} {units}"
                )

    if step.get("hr"):
        hr = step["hr"]

        if isinstance(hr, dict):
            value = hr.get("value")
            units = hr.get("units", "")

            if value is not None:
                lines.append(
                    f"{prefix}• FC: "
                    f"{value} {units}"
                )

    for child in step.get("steps", []):
        lines.extend(
            describe_step(
                child,
                level + 1
            )
        )

    return lines


# ============================================================
# MODIFICA ALLENAMENTO
# ============================================================

def show_edit_form(event):

    st.markdown(
        '<div class="detail-box">',
        unsafe_allow_html=True
    )

    st.subheader("✏️ Modifica allenamento")

    event_id = event.get("id")

    original_name = event.get(
        "name",
        "Allenamento"
    )

    original_date = get_event_date(event)

    original_time = format_time(
        event.get("start_date_local")
    )

    original_description = event.get(
        "description",
        ""
    )

    new_name = st.text_input(
        "Nome allenamento",
        value=original_name,
        key=f"edit_name_{event_id}"
    )

    new_date = st.date_input(
        "Data",
        value=original_date or date.today(),
        key=f"edit_date_{event_id}"
    )

    time_options = []

    for hour in range(0, 24):
        for minute in [0, 15, 30, 45]:
            time_options.append(
                f"{hour:02d}:{minute:02d}"
            )

    if original_time in time_options:
        default_index = time_options.index(
            original_time
        )
    else:
        default_index = 36

    new_time = st.selectbox(
        "Ora",
        time_options,
        index=default_index,
        key=f"edit_time_{event_id}"
    )

    original_duration = event.get(
        "moving_time",
        3600
    )

    duration_minutes = st.number_input(
        "Durata (minuti)",
        min_value=1,
        max_value=1440,
        value=max(
            1,
            round(
                float(original_duration) / 60
            )
        ),
        step=5,
        key=f"edit_duration_{event_id}"
    )

    new_description = st.text_area(
        "Descrizione / struttura",
        value=original_description,
        height=220,
        key=f"edit_description_{event_id}"
    )

    st.caption(
        "Puoi usare anche la sintassi workout di "
        "Intervals.icu nella descrizione."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Salva su Intervals.icu",
            key=f"save_{event_id}",
            use_container_width=True
        ):

            athlete_id, api_key = (
                get_intervals_credentials()
            )

            if not athlete_id or not api_key:

                st.error(
                    "Credenziali Intervals.icu mancanti."
                )
                return

            new_start = (
                f"{new_date.isoformat()}"
                f"T{new_time}:00"
            )

            new_end = (
                datetime.fromisoformat(
                    new_start
                )
                + timedelta(
                    minutes=duration_minutes
                )
            ).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )

            payload = {
                "name": new_name,
                "start_date_local": new_start,
                "end_date_local": new_end,
                "moving_time": duration_minutes * 60,
                "description": new_description
            }

            with st.spinner(
                "Salvataggio su Intervals.icu..."
            ):

                success, result = (
                    update_intervals_event(
                        event_id,
                        athlete_id,
                        api_key,
                        payload
                    )
                )

            if success:

                fetch_intervals_events.clear()

                st.session_state.editing_event = None
                st.session_state.selected_event = None

                st.success(
                    "✅ Allenamento aggiornato "
                    "su Intervals.icu!"
                )

                st.rerun()

            else:

                st.error(result)

    with col2:

        if st.button(
            "Annulla",
            key=f"cancel_{event_id}",
            use_container_width=True
        ):

            st.session_state.editing_event = None
            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# DETTAGLIO ALLENAMENTO
# ============================================================

def show_event_detail(event):

    if not event:
        return

    if (
        st.session_state.editing_event
        and st.session_state.editing_event.get("id")
        == event.get("id")
    ):

        show_edit_form(event)
        return

    st.markdown(
        '<div class="detail-box">',
        unsafe_allow_html=True
    )

    st.subheader(
        f"🚴 {event.get('name', 'Allenamento')}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Data",
            format_date(
                event.get("start_date_local")
            )
        )

    with col2:
        st.metric(
            "Ora",
            format_time(
                event.get("start_date_local")
            )
        )

    with col3:
        st.metric(
            "Durata",
            format_duration(
                event.get("moving_time")
            )
        )

    with col4:
        st.metric(
            "Carico",
            format_load(event)
        )

    st.divider()

    if event.get("description"):

        st.markdown("### 📝 Descrizione")

        st.text(
            event.get("description")
        )

    steps = get_steps(event)

    if steps:

        st.markdown("### 🏋️ Struttura")

        for step in steps:

            for line in describe_step(step):

                st.markdown(
                    line
                )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "✏️ Modifica allenamento",
            key=f"edit_{event.get('id')}",
            use_container_width=True
        ):

            st.session_state.editing_event = event
            st.rerun()

    with col2:

        if st.button(
            "Chiudi",
            key=f"close_{event.get('id')}",
            use_container_width=True
        ):

            st.session_state.selected_event = None
            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    st.title("🏠 Dashboard")

    st.write(
        "Il tuo centro di controllo per il ciclismo."
    )

    athlete_id, api_key = (
        get_intervals_credentials()
    )

    if athlete_id and api_key:

        st.markdown(
            '<div class="sync-box">'
            '🟢 <strong>Intervals.icu collegato</strong>'
            ' — calendario sincronizzato.'
            '</div>',
            unsafe_allow_html=True
        )

    else:

        st.warning(
            "Intervals.icu non è configurato."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("FTP", "160 W")

    with col2:
        st.metric("Peso", "50 kg")

    with col3:
        st.metric("Obiettivo", "Salita")

    with col4:
        st.metric("Giorni", "5")

    today = date.today()

    st.markdown("## 📅 Allenamento di oggi")

    events, success, error = (
        get_events_for_range(
            today,
            today
        )
    )

    if not success:

        st.warning(error)

    else:

        workouts = get_workout_events(events)

        if not workouts:

            st.info(
                "Nessun allenamento pianificato oggi."
            )

        for event in workouts:

            st.markdown(
                '<div class="workout-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="workout-title">'
                f'🚴 {event.get("name", "Allenamento")}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="workout-meta">'
                f'⏱ {format_duration(event.get("moving_time"))}'
                f' &nbsp; • &nbsp; '
                f'📈 Carico {format_load(event)}'
                f'</div>',
                unsafe_allow_html=True
            )

            if st.button(
                "Dettagli",
                key=f"dash_{event.get('id')}"
            ):

                st.session_state.selected_event = event
                st.session_state.editing_event = None
                st.rerun()

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

    if st.session_state.selected_event:

        show_event_detail(
            st.session_state.selected_event
        )


# ============================================================
# CALENDARIO
# ============================================================

def show_calendar():

    st.title("📅 Calendario")

    st.write(
        "Calendario reale sincronizzato con "
        "Intervals.icu."
    )

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col1:

        if st.button("⬅️ Precedente"):

            st.session_state.calendar_week -= timedelta(
                days=7
            )

            st.rerun()

    with col2:

        monday = st.session_state.calendar_week
        sunday = monday + timedelta(days=6)

        st.markdown(
            f"<h3 style='text-align:center'>"
            f"{monday.strftime('%d/%m')} → "
            f"{sunday.strftime('%d/%m/%Y')}"
            f"</h3>",
            unsafe_allow_html=True
        )

    with col3:

        if st.button("Successiva ➡️"):

            st.session_state.calendar_week += timedelta(
                days=7
            )

            st.rerun()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📍 Questa settimana",
            use_container_width=True
        ):

            st.session_state.calendar_week = (
                get_monday(date.today())
            )

            st.rerun()

    with col2:

        if st.button(
            "🔄 Aggiorna Intervals.icu",
            use_container_width=True
        ):

            fetch_intervals_events.clear()
            st.rerun()

    st.divider()

    monday = st.session_state.calendar_week
    sunday = monday + timedelta(days=6)

    events, success, error = (
        get_events_for_range(
            monday,
            sunday
        )
    )

    if not success:

        st.error(error)
        return

    workouts = get_workout_events(events)

    columns = st.columns(7)

    for index in range(7):

        current_day = (
            monday + timedelta(days=index)
        )

        day_events = [
            event
            for event in workouts
            if get_event_date(event)
            == current_day
        ]

        with columns[index]:

            st.markdown(
                '<div class="day-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="day-title">'
                f'{DAY_NAMES[index]}<br>'
                f'{current_day.strftime("%d/%m")}'
                f'</div>',
                unsafe_allow_html=True
            )

            if not day_events:

                st.markdown(
                    '<div class="rest-day">'
                    '😴 Riposo'
                    '</div>',
                    unsafe_allow_html=True
                )

            for event in day_events:

                st.markdown(
                    f"**🚴 {event.get('name', 'Allenamento')}**"
                )

                st.caption(
                    f"⏱ {format_duration(event.get('moving_time'))}"
                )

                st.caption(
                    f"📈 Carico: {format_load(event)}"
                )

                if st.button(
                    "Apri",
                    key=f"cal_{event.get('id')}",
                    use_container_width=True
                ):

                    st.session_state.selected_event = event
                    st.session_state.editing_event = None
                    st.rerun()

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

    st.markdown("## 📊 Riepilogo")

    total_seconds = sum(
        event.get("moving_time", 0) or 0
        for event in workouts
    )

    total_load = 0

    for event in workouts:

        value = event.get(
            "icu_training_load"
        )

        if value:

            try:
                total_load += float(value)
            except Exception:
                pass

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Allenamenti",
            len(workouts)
        )

    with col2:
        st.metric(
            "Tempo",
            format_duration(total_seconds)
        )

    with col3:
        st.metric(
            "Carico",
            round(total_load)
        )

    if st.session_state.selected_event:

        show_event_detail(
            st.session_state.selected_event
        )


# ============================================================
# ALLENAMENTI
# ============================================================

def show_workouts():

    st.title("🚴 Allenamenti")

    today = date.today()

    events, success, error = (
        get_events_for_range(
            today - timedelta(days=30),
            today + timedelta(days=30)
        )
    )

    if not success:

        st.error(error)
        return

    workouts = get_workout_events(events)

    workouts.sort(
        key=lambda x: x.get(
            "start_date_local",
            ""
        )
    )

    for event in workouts:

        st.markdown(
            '<div class="workout-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="workout-title">'
            f'{event.get("name", "Allenamento")}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="workout-meta">'
            f'📅 {format_date(event.get("start_date_local"))}'
            f' &nbsp; • &nbsp; '
            f'⏱ {format_duration(event.get("moving_time"))}'
            f' &nbsp; • &nbsp; '
            f'📈 {format_load(event)}'
            f'</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "Apri",
            key=f"work_{event.get('id')}"
        ):

            st.session_state.selected_event = event
            st.session_state.editing_event = None
            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    if st.session_state.selected_event:

        show_event_detail(
            st.session_state.selected_event
        )


# ============================================================
# ANALISI
# ============================================================

def show_analysis():

    st.title("📊 Analisi")

    st.info(
        "Qui collegheremo le attività realmente "
        "svolte e il carico di Intervals.icu."
    )

    st.markdown("""
### Prossimamente

- 🚴 Allenamenti completati
- ❤️ Frequenza cardiaca
- ⚡ Potenza
- 📈 Carico
- 🧠 Fatica
- 📊 Fitness
- 🔋 Form
- 🏔️ Prestazioni in salita
""")


# ============================================================
# AI COACH
# ============================================================

def show_ai_coach():

    st.title("🤖 AI Coach")

    st.info(
        "Il vero AI Coach arriverà dopo aver completato "
        "l'analisi degli allenamenti."
    )

    st.markdown("""
### Obiettivo finale

Il Coach dovrà:

1. Leggere il calendario Intervals.icu
2. Leggere gli allenamenti realmente svolti
3. Confrontare pianificato vs eseguito
4. Valutare fatica e recupero
5. Decidere se modificare il piano
6. Modificare automaticamente Intervals.icu

Questa è la struttura che stiamo costruendo.
""")


# ============================================================
# PROFILO
# ============================================================

def show_profile():

    st.title("👤 Profilo")

    st.write("### Intervals.icu")

    athlete_id, api_key = (
        get_intervals_credentials()
    )

    if athlete_id and api_key:

        st.success(
            "🟢 Intervals.icu collegato"
        )

    else:

        st.error(
            "🔴 Intervals.icu non collegato"
        )

    st.info(
        "Le credenziali sono conservate nei "
        "Secrets di Streamlit."
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🚴 Luca Cycling Coach")

    st.caption(
        "Il tuo allenatore ciclistico"
    )

    st.divider()

    pagina = st.radio(
        "Menu",
        [
            "🏠 Dashboard",
            "📅 Calendario",
            "🚴 Allenamenti",
            "📊 Analisi",
            "🤖 AI Coach",
            "👤 Profilo"
        ],
        key="main_navigation"
    )

    st.divider()

    st.markdown("### Profilo atleta")

    st.number_input(
        "Peso (kg)",
        30.0,
        150.0,
        50.0,
        0.5
    )

    st.number_input(
        "FTP (W)",
        50,
        500,
        160,
        1
    )

    st.number_input(
        "FC max",
        100,
        230,
        190,
        1
    )

    st.selectbox(
        "Obiettivo",
        [
            "Migliorare forma generale",
            "Migliorare in salita",
            "Aumentare FTP",
            "Preparare una gara",
            "Aumentare resistenza"
        ]
    )


# ============================================================
# ROUTING
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
