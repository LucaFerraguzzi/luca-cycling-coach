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
""" <style>

```
/* ======================================================
   SFONDO GENERALE
   ====================================================== */

.stApp {
    background-color: #f7f8fa !important;
}

/* ======================================================
   TESTO GENERALE - NERO
   ====================================================== */

.main,
.main *,
.block-container,
.block-container *,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] * {
    color: #111111 !important;
}

/* Titoli */
h1,
h2,
h3,
h4,
h5,
h6 {
    color: #111111 !important;
}

/* Paragrafi */
p,
span,
label,
li,
td,
th,
div {
    color: #111111;
}

/* ======================================================
   SIDEBAR
   ====================================================== */

section[data-testid="stSidebar"] {
    background-color: #111827 !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] input {
    color: #111111 !important;
    background-color: #ffffff !important;
}

section[data-testid="stSidebar"] textarea {
    color: #111111 !important;
    background-color: #ffffff !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #111111 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #111111 !important;
}

section[data-testid="stSidebar"] [role="option"] {
    background-color: #ffffff !important;
    color: #111111 !important;
}

section[data-testid="stSidebar"] [role="option"] * {
    color: #111111 !important;
}

/* Radio sidebar */
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label * {
    color: #ffffff !important;
}

/* ======================================================
   INPUT
   ====================================================== */

input,
textarea {
    color: #111111 !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #111111 !important;
}

input::placeholder,
textarea::placeholder {
    color: #666666 !important;
    -webkit-text-fill-color: #666666 !important;
}

/* Selectbox */
[data-baseweb="select"] {
    background-color: #ffffff !important;
}

[data-baseweb="select"] * {
    color: #111111 !important;
}

/* ======================================================
   METRICHE
   ====================================================== */

[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    padding: 14px !important;
}

[data-testid="stMetric"] * {
    color: #111111 !important;
}

[data-testid="stMetricLabel"] {
    color: #444444 !important;
}

[data-testid="stMetricValue"] {
    color: #111111 !important;
}

[data-testid="stMetricDelta"] {
    color: #111111 !important;
}

/* ======================================================
   INFO / WARNING / SUCCESS / ERROR
   ====================================================== */

[data-testid="stAlert"] {
    color: #111111 !important;
}

[data-testid="stAlert"] * {
    color: #111111 !important;
}

[data-testid="stAlert"] p {
    color: #111111 !important;
}

/* ======================================================
   CONTAINER
   ====================================================== */

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border-color: #e5e7eb !important;
}

[data-testid="stVerticalBlockBorderWrapper"] * {
    color: #111111 !important;
}

/* ======================================================
   EXPANDER
   ====================================================== */

[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] * {
    color: #111111 !important;
}

/* ======================================================
   BOTTONI
   ====================================================== */

.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.stButton button p {
    color: #111111 !important;
}

.stButton button span {
    color: #111111 !important;
}

/* ======================================================
   FORM
   ====================================================== */

[data-testid="stForm"] {
    background-color: #ffffff !important;
    border-radius: 14px !important;
}

[data-testid="stForm"] * {
    color: #111111 !important;
}

/* ======================================================
   TESTO MARKDOWN
   ====================================================== */

[data-testid="stMarkdownContainer"] {
    color: #111111 !important;
}

[data-testid="stMarkdownContainer"] * {
    color: #111111 !important;
}

/* ======================================================
   CAPTION
   ====================================================== */

[data-testid="stCaptionContainer"] {
    color: #444444 !important;
}

[data-testid="stCaptionContainer"] * {
    color: #444444 !important;
}

</style>
""",
unsafe_allow_html=True,
```

)

# ============================================================

# INTERVALS.ICU API

# ============================================================

try:
INTERVALS_ATHLETE_ID = st.secrets["INTERVALS_ATHLETE_ID"]
INTERVALS_API_KEY = st.secrets["INTERVALS_API_KEY"]

except Exception:
st.error(
"Non trovo INTERVALS_ATHLETE_ID e INTERVALS_API_KEY "
"nei Secrets di Streamlit."
)
st.stop()

BASE_URL = "https://intervals.icu/api/v1"

def intervals_auth():
return ("API_KEY", INTERVALS_API_KEY)

# ============================================================

# RECUPERA ALLENAMENTI DA INTERVALS.ICU

# ============================================================

def get_intervals_events(start_date, end_date):

```
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

    events = [
        event
        for event in data
        if event.get("category") == "WORKOUT"
    ]

    return events

except Exception as e:

    st.error(
        f"Errore durante il collegamento a Intervals.icu: {e}"
    )

    return []
```

# ============================================================

# MODIFICA ALLENAMENTO

# ============================================================

def update_intervals_event(
event_id,
name,
start_datetime,
end_datetime,
description,
):

```
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

    st.error(
        f"Errore durante il salvataggio: {e}"
    )

    return False
```

# ============================================================

# FUNZIONI DATA

# ============================================================

def parse_event_datetime(event):

```
value = event.get("start_date_local")

if not value:
    return None

try:

    return datetime.fromisoformat(
        value.replace("Z", "")
    )

except Exception:

    return None
```

def format_duration(minutes):

```
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
```

def get_event_duration(event):

```
start = parse_event_datetime(event)

end_value = event.get("end_date_local")

if start and end_value:

    try:

        end = datetime.fromisoformat(
            end_value.replace("Z", "")
        )

        return max(
            1,
            int(
                (end - start).total_seconds() / 60
            )
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
```

# ============================================================

# DATA CORRENTE

# ============================================================

today = date.today()

month_start = today.replace(day=1)

if today.month == 12:

```
next_month = date(
    today.year + 1,
    1,
    1,
)
```

else:

```
next_month = date(
    today.year,
    today.month + 1,
    1,
)
```

month_end = next_month - timedelta(days=1)

# ============================================================

# CARICA EVENTI

# ============================================================

if st.session_state.events_cache is None:

```
st.session_state.events_cache = get_intervals_events(
    month_start,
    month_end,
)
```

events = st.session_state.events_cache

# ============================================================

# SIDEBAR

# ============================================================

with st.sidebar:

```
st.title("🚴 Luca Cycling Coach")

st.caption("Il tuo coach per il ciclismo")

st.divider()

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

st.subheader("Profilo")

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

st.caption(
    "🔗 Calendario sincronizzato con Intervals.icu"
)
```

# ============================================================

# FUNZIONI UTILI

# ============================================================

def find_event_by_id(event_id):

```
for event in events:

    if str(event.get("id")) == str(event_id):

        return event

return None
```

def show_page_title(title, subtitle):

```
st.title(title)

st.caption(subtitle)
```

# ============================================================

# DETTAGLI ALLENAMENTO

# ============================================================

def show_workout_detail(event):

```
if not event:
    return

st.divider()

st.subheader(
    f"🚴 {event.get('name', 'Allenamento')}"
)

start = parse_event_datetime(event)

duration = get_event_duration(event)

if start:

    st.write(
        f"📅 {start.strftime('%d/%m/%Y')}   "
        f"🕐 {start.strftime('%H:%M')}   "
        f"⏱️ {format_duration(duration)}"
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

        load = event.get(
            "icu_training_load"
        )

    st.metric(
        "Carico",
        str(round(load))
        if load is not None
        else "—",
    )

st.markdown("### 📋 Riepilogo")

summary = event.get("name")

if summary:

    st.info(summary)

else:

    st.info(
        "Nessun riepilogo disponibile."
    )

st.markdown("### 📝 Descrizione allenamento")

description = event.get(
    "description",
    "",
)

if description:

    st.text(description)

else:

    st.info(
        "Nessuna descrizione disponibile."
    )
```

# ============================================================

# MODIFICA ALLENAMENTO

# ============================================================

def show_edit_form(event):

```
if not event:
    return

st.divider()

st.subheader("✏️ Modifica allenamento")

start = parse_event_datetime(event)

if start is None:

    start = datetime.now()

duration = get_event_duration(event)

if duration is None:

    duration = 60

with st.form("edit_workout_form"):

    new_name = st.text_input(
        "Nome allenamento",
        value=event.get(
            "name",
            "",
        ),
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
        + timedelta(
            minutes=int(new_duration)
        )
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

        st.session_state.selected_event = event.get(
            "id"
        )

        st.rerun()
```

# ============================================================

# DASHBOARD

# ============================================================

def show_dashboard():

```
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

st.subheader("📅 Allenamento di oggi")

if today_events:

    for event in today_events:

        start = parse_event_datetime(event)

        duration = get_event_duration(event)

        with st.container(border=True):

            st.markdown(
                f"### 🚴 {event.get('name', 'Allenamento')}"
            )

            st.write(
                f"🕐 {start.strftime('%H:%M')}"
                if start
                else ""
            )

            st.write(
                f"⏱️ {format_duration(duration)}"
            )

            if st.button(
                "Dettagli",
                key=f"dashboard_detail_{event.get('id')}",
            ):

                st.session_state.selected_event = (
                    event.get("id")
                )

                st.rerun()

else:

    st.info(
        "Nessun allenamento programmato per oggi."
    )

st.subheader("🔜 Prossimi allenamenti")

upcoming = []

for event in events:

    start = parse_event_datetime(event)

    if start and start.date() >= today:

        upcoming.append(event)

upcoming.sort(
    key=lambda x:
    parse_event_datetime(x)
    or datetime.max
)

for event in upcoming[:5]:

    start = parse_event_datetime(event)

    duration = get_event_duration(event)

    with st.container(border=True):

        if start:

            st.caption(
                start.strftime(
                    "%A %d/%m/%Y · %H:%M"
                )
            )

        st.markdown(
            f"### 🚴 {event.get('name', 'Allenamento')}"
        )

        st.write(
            f"⏱️ {format_duration(duration)}"
        )

        if st.button(
            "Apri allenamento",
            key=f"dashboard_open_{event.get('id')}",
        ):

            st.session_state.selected_event = (
                event.get("id")
            )

            st.rerun()
```

# ============================================================

# CALENDARIO

# ============================================================

def show_calendar():

```
show_page_title(
    "Calendario",
    "Gli allenamenti programmati su Intervals.icu.",
)

if not events:

    st.warning(
        "Non sono stati trovati allenamenti "
        "su Intervals.icu."
    )

    return

st.subheader("📅 Allenamenti programmati")

sorted_events = sorted(
    events,
    key=lambda x:
    parse_event_datetime(x)
    or datetime.max,
)

for event in sorted_events:

    start = parse_event_datetime(event)

    if not start:

        continue

    duration = get_event_duration(event)

    with st.container(border=True):

        col1, col2, col3 = st.columns(
            [1.4, 4, 1]
        )

        with col1:

            st.markdown(
                f"**{start.strftime('%a %d/%m')}**"
            )

            st.caption(
                start.strftime("%H:%M")
            )

        with col2:

            st.markdown(
                f"### {event.get('name', 'Allenamento')}"
            )

            st.write(
                f"🚴 {event.get('type', 'Ride')} "
                f"· ⏱️ {format_duration(duration)}"
            )

        with col3:

            if st.button(
                "Apri",
                key=f"calendar_open_{event.get('id')}",
                use_container_width=True,
            ):

                st.session_state.selected_event = (
                    event.get("id")
                )

                st.rerun()
```

# ============================================================

# ALLENAMENTI

# ============================================================

def show_workouts():

```
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
    key=lambda x:
    parse_event_datetime(x)
    or datetime.max,
)

for event in sorted_events:

    start = parse_event_datetime(event)

    duration = get_event_duration(event)

    with st.container(border=True):

        if start:

            st.caption(
                start.strftime(
                    "%d/%m/%Y · %H:%M"
                )
            )

        st.markdown(
            f"### 🚴 {event.get('name', 'Allenamento')}"
        )

        st.write(
            f"{event.get('type', 'Ride')} "
            f"· ⏱️ {format_duration(duration)}"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "👁 Dettagli",
                key=f"workout_detail_{event.get('id')}",
                use_container_width=True,
            ):

                st.session_state.selected_event = (
                    event.get("id")
                )

                st.rerun()

        with col2:

            if st.button(
                "✏️ Modifica",
                key=f"workout_edit_{event.get('id')}",
                use_container_width=True,
            ):

                st.session_state.edit_event = (
                    event.get("id")
                )

                st.session_state.selected_event = (
                    event.get("id")
                )

                st.rerun()
```

# ============================================================

# ANALISI

# ============================================================

def show_analysis():

```
show_page_title(
    "Analisi",
    "Analisi progressiva dei tuoi allenamenti.",
)

st.info(
    "📊 La parte avanzata dell'analisi verrà "
    "collegata alle attività completate "
    "e ai dati di Intervals.icu."
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

with st.container(border=True):

    st.subheader(
        "🔍 Prossimo step"
    )

    st.write(
        "L'app potrà leggere le attività completate, "
        "confrontarle con gli allenamenti programmati "
        "e valutare fatica, carico e progressione."
    )
```

# ============================================================

# AI COACH

# ============================================================

def show_ai_coach():

```
show_page_title(
    "AI Coach",
    "Il futuro coach intelligente di Luca Cycling Coach.",
)

with st.container(border=True):

    st.subheader(
        "🤖 AI Coach"
    )

    st.write(
        "In questa sezione costruiremo il vero "
        "coach automatico dell'app."
    )

    st.write(
        "L'obiettivo sarà far analizzare all'AI:"
    )

    st.markdown(
        """
        - gli allenamenti programmati
        - gli allenamenti realmente completati
        - carico e fatica
        - progressione nel tempo
        - eventuali giorni saltati
        - prestazioni e sensazioni
        """
    )

    st.write(
        "Successivamente il coach potrà modificare "
        "automaticamente gli allenamenti futuri "
        "direttamente su Intervals.icu."
    )

st.button(
    "🤖 Analizza allenamento",
    disabled=True,
)
```

# ============================================================

# PROFILO

# ============================================================

def show_profile():

```
show_page_title(
    "Profilo",
    "Le tue impostazioni di allenamento.",
)

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.subheader(
            "🚴 Dati atleta"
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

with col2:

    with st.container(border=True):

        st.subheader(
            "🔗 Collegamenti"
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
```

# ============================================================

# ROUTING

# ============================================================

if pagina == "🏠 Dashboard":

```
show_dashboard()
```

elif pagina == "📅 Calendario":

```
show_calendar()
```

elif pagina == "🚴 Allenamenti":

```
show_workouts()
```

elif pagina == "📊 Analisi":

```
show_analysis()
```

elif pagina == "🤖 AI Coach":

```
show_ai_coach()
```

elif pagina == "👤 Profilo":

```
show_profile()
```

# ============================================================

# ALLENAMENTO SELEZIONATO

# ============================================================

if st.session_state.selected_event:

```
selected = find_event_by_id(
    st.session_state.selected_event
)

if selected:

    show_workout_detail(selected)

    if st.button(
        "✏️ Modifica questo allenamento",
        key="selected_edit_button",
    ):

        st.session_state.edit_event = (
            selected.get("id")
        )

        st.rerun()
```

# ============================================================

# FORM MODIFICA

# ============================================================

if st.session_state.edit_event:

```
edit_event = find_event_by_id(
    st.session_state.edit_event
)

if edit_event:

    show_edit_form(edit_event)

