import streamlit as st
import requests
from datetime import date, datetime, timedelta

# ============================================================
# CONFIGURAZIONE
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

    /* APP */
    .stApp {
        background-color: #f5f7fa;
        color: #111827;
    }

    /* SIDEBAR */
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

    /* TITOLI */
    h1, h2, h3, h4 {
        color: #111827 !important;
    }

    p, span, label, div {
        color: inherit;
    }

    /* BUTTON */
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

    /* CARD */
    .workout-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .workout-date {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 4px;
    }

    .workout-title {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }

    .workout-meta {
        color: #4b5563;
        font-size: 14px;
    }

    .day-card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        padding: 15px;
        min-height: 150px;
    }

    .day-title {
        font-weight: 700;
        font-size: 15px;
        color: #111827;
        margin-bottom: 10px;
    }

    .rest-day {
        color: #9ca3af;
        font-size: 14px;
    }

    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        text-align: center;
    }

    .small-label {
        font-size: 13px;
        color: #6b7280;
    }

    .big-number {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
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
        margin-bottom: 20px;
    }

    .detail-box {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 22px;
        margin-top: 20px;
    }

</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

if "calendar_week" not in st.session_state:
    st.session_state.calendar_week = date.today()

if "events_cache" not in st.session_state:
    st.session_state.events_cache = {}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🚴 Luca Cycling Coach")
    st.caption("Il tuo allenatore ciclistico")

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
        "FC max",
        min_value=100,
        max_value=230,
        value=190,
        step=1
    )

    obiettivo = st.selectbox(
        "Obiettivo",
        [
            "Migliorare forma generale",
            "Migliorare in salita",
            "Aumentare FTP",
            "Preparare una gara",
            "Aumentare resistenza"
        ]
    )

    giorni = st.multiselect(
        "Giorni disponibili",
        ["Lunedì", "Martedì", "Giovedì", "Venerdì", "Sabato"],
        default=["Lunedì", "Martedì", "Giovedì", "Venerdì", "Sabato"]
    )

# ============================================================
# FUNZIONI INTERVALS.ICU
# ============================================================

def get_intervals_credentials():

    try:
        athlete_id = st.secrets["INTERVALS_ATHLETE_ID"]
        api_key = st.secrets["INTERVALS_API_KEY"]

        return athlete_id, api_key

    except Exception:
        return None, None


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
            f"({response.status_code}): "
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


def get_week_events(monday):

    sunday = monday + timedelta(days=6)

    return get_events_for_range(
        monday,
        sunday
    )


def get_workout_events(events):

    return [
        event
        for event in events
        if event.get("category") == "WORKOUT"
    ]


# ============================================================
# FUNZIONI UTILITY
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


def format_date(date_string):

    if not date_string:
        return ""

    try:
        dt = datetime.fromisoformat(
            date_string.replace("Z", "")
        )

        return dt.strftime("%d/%m/%Y")

    except Exception:
        return date_string[:10]


def format_time(date_string):

    if not date_string:
        return ""

    try:
        dt = datetime.fromisoformat(
            date_string.replace("Z", "")
        )

        return dt.strftime("%H:%M")

    except Exception:
        return ""


def format_duration(seconds):

    if not seconds:
        return "—"

    minutes = round(seconds / 60)

    if minutes < 60:
        return f"{minutes} min"

    hours = minutes // 60
    mins = minutes % 60

    if mins == 0:
        return f"{hours}h"

    return f"{hours}h {mins}m"


def format_load(event):

    load = event.get("icu_training_load")

    if load is None:
        load = event.get("load_target")

    if load is None:
        return "—"

    try:
        return str(round(float(load)))

    except Exception:
        return str(load)


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


def get_event_steps(event):

    workout_doc = event.get("workout_doc")

    if not workout_doc:
        return []

    steps = workout_doc.get("steps", [])

    return steps


def describe_step(step, level=0):

    lines = []

    prefix = "  " * level

    if "text" in step:
        lines.append(
            f"{prefix}{step['text']}"
        )

    duration = step.get("duration")

    if duration:

        minutes = round(duration / 60)

        lines.append(
            f"{prefix}• {minutes} min"
        )

    if "reps" in step:

        lines.append(
            f"{prefix}• Ripetizioni: {step['reps']}"
        )

    if "power" in step:

        power = step["power"]

        if isinstance(power, dict):

            value = power.get("value")
            units = power.get("units", "")

            if value is not None:
                lines.append(
                    f"{prefix}• Potenza: {value} {units}"
                )

    if "hr" in step:

        hr = step["hr"]

        if isinstance(hr, dict):

            value = hr.get("value")
            units = hr.get("units", "")

            if value is not None:
                lines.append(
                    f"{prefix}• FC: {value} {units}"
                )

    if "pace" in step:

        pace = step["pace"]

        if isinstance(pace, dict):

            start = pace.get("start")
            end = pace.get("end")

            if start is not None:
                lines.append(
                    f"{prefix}• Ritmo: {start} → {end}"
                )

    if "steps" in step:

        for substep in step["steps"]:

            lines.extend(
                describe_step(
                    substep,
                    level + 1
                )
            )

    return lines


def find_event_for_date(events, target_date):

    matches = []

    for event in get_workout_events(events):

        event_date = get_event_date(event)

        if event_date == target_date:
            matches.append(event)

    return matches


# ============================================================
# DETTAGLIO ALLENAMENTO
# ============================================================

def show_event_detail(event):

    if not event:
        return

    st.markdown(
        '<div class="detail-box">',
        unsafe_allow_html=True
    )

    name = event.get(
        "name",
        "Allenamento"
    )

    st.markdown(
        f"## 🚴 {name}"
    )

    start = event.get("start_date_local")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Data",
            format_date(start)
        )

    with col2:
        st.metric(
            "Ora",
            format_time(start) or "—"
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

    description = event.get("description")

    if description:

        st.markdown("### Descrizione")

        st.markdown(
            description
        )

    steps = get_event_steps(event)

    if steps:

        st.markdown("### Struttura")

        for step in steps:

            lines = describe_step(step)

            for line in lines:
                st.markdown(line)

    paired_activity = event.get(
        "paired_activity_id"
    )

    if paired_activity:

        st.success(
            "Questo allenamento risulta collegato "
            "a un'attività completata su Intervals.icu."
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

def show_footer():

    st.divider()

    st.caption(
        "Luca Cycling Coach • "
        "Calendario sincronizzato con Intervals.icu"
    )


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    st.title("🏠 Dashboard")

    st.markdown(
        "Il tuo centro di controllo per il ciclismo."
    )

    athlete_id, api_key = get_intervals_credentials()

    if not athlete_id or not api_key:

        st.warning(
            "⚠️ Intervals.icu non è ancora collegato. "
            "Configura le API key nei Secrets di Streamlit."
        )

    else:

        st.markdown(
            '<div class="sync-box">'
            '🟢 <strong>Intervals.icu collegato</strong> — '
            'il calendario viene letto direttamente dal tuo account.'
            '</div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # METRICHE
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            '<div class="metric-card">'
            '<div class="small-label">FTP</div>'
            f'<div class="big-number">{ftp} W</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="metric-card">'
            '<div class="small-label">Peso</div>'
            f'<div class="big-number">{weight:.1f} kg</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            '<div class="metric-card">'
            '<div class="small-label">Obiettivo</div>'
            f'<div class="big-number">🚴</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            '<div class="metric-card">'
            '<div class="small-label">Giorni allenamento</div>'
            f'<div class="big-number">{len(giorni)}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("## 📅 Allenamento di oggi")

    today = date.today()

    events, success, error = get_events_for_range(
        today,
        today
    )

    if success:

        today_workouts = get_workout_events(events)

        if today_workouts:

            for event in today_workouts:

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
                    f'{format_duration(event.get("moving_time"))}'
                    f' &nbsp; • &nbsp; '
                    f'Carico: {format_load(event)}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    "Dettagli",
                    key=f"dashboard_{event.get('id')}"
                ):

                    st.session_state.selected_event = event
                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "Nessun allenamento pianificato per oggi."
            )

    else:

        if error:
            st.warning(error)

    # --------------------------------------------------------
    # DETTAGLIO SELEZIONATO
    # --------------------------------------------------------

    if st.session_state.selected_event:

        show_event_detail(
            st.session_state.selected_event
        )

    # --------------------------------------------------------
    # PROSSIMI ALLENAMENTI
    # --------------------------------------------------------

    st.markdown("## 🔜 Prossimi allenamenti")

    monday = get_monday(today)
    sunday = monday + timedelta(days=13)

    events, success, error = get_events_for_range(
        monday,
        sunday
    )

    if success:

        future = []

        for event in get_workout_events(events):

            event_date = get_event_date(event)

            if event_date and event_date >= today:
                future.append(event)

        future.sort(
            key=lambda x: x.get(
                "start_date_local",
                ""
            )
        )

        for event in future[:5]:

            col1, col2, col3 = st.columns(
                [1.5, 4, 1]
            )

            with col1:

                st.write(
                    format_date(
                        event.get("start_date_local")
                    )
                )

            with col2:

                st.write(
                    f"**{event.get('name', 'Allenamento')}**"
                )

            with col3:

                if st.button(
                    "Apri",
                    key=f"dashboard_future_{event.get('id')}"
                ):

                    st.session_state.selected_event = event
                    st.rerun()

    show_footer()


# ============================================================
# CALENDARIO
# ============================================================

def show_calendar():

    st.title("📅 Calendario")

    st.markdown(
        "Qui vengono mostrati gli allenamenti reali "
        "presenti su **Intervals.icu**."
    )

    # --------------------------------------------------------
    # NAVIGAZIONE SETTIMANA
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col1:

        if st.button(
            "⬅️ Settimana precedente"
        ):

            st.session_state.calendar_week -= timedelta(
                days=7
            )

            st.rerun()

    with col2:

        st.markdown(
            f"<h3 style='text-align:center;'>"
            f"{st.session_state.calendar_week.strftime('%d/%m/%Y')}"
            f" → "
            f"{(st.session_state.calendar_week + timedelta(days=6)).strftime('%d/%m/%Y')}"
            f"</h3>",
            unsafe_allow_html=True
        )

    with col3:

        if st.button(
            "Settimana successiva ➡️"
        ):

            st.session_state.calendar_week += timedelta(
                days=7
            )

            st.rerun()

    if st.button("📍 Torna a questa settimana"):

        st.session_state.calendar_week = get_monday(
            date.today()
        )

        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # AGGIORNAMENTO
    # --------------------------------------------------------

    if st.button("🔄 Aggiorna da Intervals.icu"):

        fetch_intervals_events.clear()

        st.rerun()

    monday = st.session_state.calendar_week
    sunday = monday + timedelta(days=6)

    events, success, error = get_events_for_range(
        monday,
        sunday
    )

    if not success:

        st.markdown(
            '<div class="warning-box">'
            '⚠️ Impossibile leggere il calendario di Intervals.icu.'
            '</div>',
            unsafe_allow_html=True
        )

        if error:
            st.code(error)

        show_footer()
        return

    workouts = get_workout_events(events)

    # --------------------------------------------------------
    # CALENDARIO 7 GIORNI
    # --------------------------------------------------------

    columns = st.columns(7)

    for i in range(7):

        current_day = monday + timedelta(days=i)

        day_events = find_event_for_date(
            workouts,
            current_day
        )

        with columns[i]:

            st.markdown(
                '<div class="day-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="day-title">'
                f'{DAY_NAMES[i]}<br>'
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

            else:

                for event in day_events:

                    st.markdown(
                        f"**🚴 {event.get('name', 'Allenamento')}**"
                    )

                    st.caption(
                        f"⏱ {format_duration(event.get('moving_time'))}"
                    )

                    load = format_load(event)

                    if load != "—":

                        st.caption(
                            f"📈 Carico: {load}"
                        )

                    if st.button(
                        "Apri",
                        key=f"calendar_{event.get('id')}"
                    ):

                        st.session_state.selected_event = event
                        st.rerun()

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # RIEPILOGO SETTIMANA
    # --------------------------------------------------------

    st.markdown("## 📊 Riepilogo settimana")

    total_minutes = 0
    total_load = 0
    workout_count = len(workouts)

    for event in workouts:

        moving_time = event.get("moving_time")

        if moving_time:
            total_minutes += moving_time / 60

        load = event.get("icu_training_load")

        if load:
            try:
                total_load += float(load)
            except Exception:
                pass

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Allenamenti",
            workout_count
        )

    with col2:

        st.metric(
            "Tempo totale",
            format_duration(
                total_minutes * 60
            )
        )

    with col3:

        st.metric(
            "Carico totale",
            round(total_load)
        )

    # --------------------------------------------------------
    # DETTAGLIO
    # --------------------------------------------------------

    if st.session_state.selected_event:

        show_event_detail(
            st.session_state.selected_event
        )

    show_footer()


# ============================================================
# ALLENAMENTI
# ============================================================

def show_workouts():

    st.title("🚴 Allenamenti")

    st.markdown(
        "Gli allenamenti vengono presi direttamente "
        "dal calendario Intervals.icu."
    )

    today = date.today()

    start = today - timedelta(days=30)
    end = today + timedelta(days=30)

    events, success, error = get_events_for_range(
        start,
        end
    )

    if not success:

        st.warning(error)
        show_footer()
        return

    workouts = get_workout_events(events)

    workouts.sort(
        key=lambda x: x.get(
            "start_date_local",
            ""
        ),
        reverse=True
    )

    if not workouts:

        st.info(
            "Nessun allenamento trovato."
        )

    for event in workouts:

        st.markdown(
            '<div class="workout-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="workout-date">'
            f'{format_date(event.get("start_date_local"))}'
            f'</div>',
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
            f'⏱ {format_duration(event.get("moving_time"))}'
            f' &nbsp; • &nbsp; '
            f'📈 Carico {format_load(event)}'
            f'</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "Dettagli",
            key=f"workouts_{event.get('id')}"
        ):

            st.session_state.selected_event = event
            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    if st.session_state.selected_event:

        show_event_detail(
            st.session_state.selected_event
        )

    show_footer()


# ============================================================
# ANALISI
# ============================================================

def show_analysis():

    st.title("📊 Analisi")

    st.info(
        "Questa sezione verrà collegata alle attività "
        "reali di Intervals.icu nella prossima fase."
    )

    st.markdown("""
    ### Cosa analizzeremo

    - 🚴 Allenamenti completati
    - ❤️ Frequenza cardiaca
    - ⚡ Potenza
    - 📈 Carico
    - 🧠 Fatica
    - 📊 Fitness
    - 🔋 Form
    - 🏔️ Prestazioni in salita
    """)

    show_footer()


# ============================================================
# AI COACH
# ============================================================

def show_ai_coach():

    st.title("🤖 AI Coach")

    st.markdown(
        "Il coach analizzerà progressivamente "
        "allenamenti, calendario e carico."
    )

    st.info(
        "🚧 AI Coach completo in costruzione."
    )

    st.markdown("""
    ### In futuro il coach potrà:

    **1. Analizzare**
    - allenamenti completati
    - carico
    - fatica
    - recupero
    - andamento della forma

    **2. Valutare**
    - se hai rispettato il piano
    - se hai spinto troppo
    - se sei affaticato
    - se stai migliorando

    **3. Modificare**
    - allenamento del giorno
    - allenamenti successivi
    - volume
    - intensità
    - recuperi

    **4. Scrivere nuovamente su Intervals.icu**
    """)

    show_footer()


# ============================================================
# PROFILO
# ============================================================

def show_profile():

    st.title("👤 Profilo")

    st.markdown("### Dati atleta")

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
        f"**Obiettivo:** {obiettivo}"
    )

    st.write(
        f"**Giorni disponibili:** "
        f"{', '.join(giorni) if giorni else 'Nessuno'}"
    )

    st.divider()

    st.markdown("### Intervals.icu")

    athlete_id, api_key = get_intervals_credentials()

    if athlete_id and api_key:

        st.success(
            "🟢 Account Intervals.icu collegato"
        )

        st.caption(
            "La tua API key viene utilizzata "
            "solo dal server Streamlit e non viene mostrata."
        )

    else:

        st.warning(
            "🔴 Intervals.icu non collegato"
        )

    show_footer()


# ============================================================
# NAVIGAZIONE PRINCIPALE
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
