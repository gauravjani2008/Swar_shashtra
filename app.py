import streamlit as st
import requests
from datetime import datetime, timedelta, time
import pytz
import pandas as pd

# ─────────────────────────────────────────────
# 1. TRANSLATION DICTIONARY
# ─────────────────────────────────────────────
trans = {
    "English": {
        "title": "🕉️ Swar Shastra Pro",
        "settings": "Location & Date Settings",
        "date_pick": "Select Date",
        "city": "Enter City (for reference)",
        "lat": "Latitude",
        "long": "Longitude",
        "get_sun": "Fetch Sunrise Automatically",
        "sun_found": "Sunrise locked at:",
        "sunrise": "Sunrise Time",
        "lang": "Language",
        "left": "Left Nostril — Chandra Swar 🔵",
        "right": "Right Nostril — Surya Swar 🟠",
        "schedule": "📅 Full Day Schedule —",
        "paksha": "Select Paksha",
        "tithi": "Sunrise Tithi (1–15)",
        "active_now": "🟢 NOW",
        "tattva_running": "Active Tattva:",
        "what_now": "🧭 What Should You Do Now?",
        "auspicious_label": "✅ Auspicious Time",
        "caution_label": "⚠️ Use Caution",
        "avoid_label": "🚫 Avoid Action",
        "sandhi_label": "🌀 Sandhi (Junction) — Sushumna Active",
        "sandhi_note": "This is a transition period. Best for meditation & spiritual practice only. Avoid all worldly actions.",
        "refresh": "🔄 Refresh Now",
        "last_updated": "Last updated:",
        "timeline": "⏱️ Today's Swar Timeline",
        "cycle": "Tattva Cycle",
        "shukla": "Shukla (Bright)",
        "krishna": "Krishna (Dark)",
    },
    "ગુજરાતી": {
        "title": "🕉️ સ્વર શાસ્ત્ર પ્રો",
        "settings": "સ્થળ અને તારીખ સેટિંગ્સ",
        "date_pick": "તારીખ પસંદ કરો",
        "city": "શહેરનું નામ",
        "lat": "અક્ષાંશ (Latitude)",
        "long": "રેખાંશ (Longitude)",
        "get_sun": "સૂર્યોદય સમય મેળવો",
        "sun_found": "સૂર્યોદયનો સમય:",
        "sunrise": "સૂર્યોદય સમય",
        "lang": "ભાષા",
        "left": "ડાબું નાક — ચન્દ્ર સ્વર 🔵",
        "right": "જમણું નાક — સૂર્ય સ્વર 🟠",
        "schedule": "📅 આખા દિવસનું શિડ્યુલ —",
        "paksha": "પક્ષ પસંદ કરો",
        "tithi": "સૂર્યોદય વખતની તિથિ (૧-૧૫)",
        "active_now": "🟢 અત્યારે",
        "tattva_running": "અત્યારનું તત્વ:",
        "what_now": "🧭 અત્યારે શું કરવું?",
        "auspicious_label": "✅ શુભ સમય",
        "caution_label": "⚠️ સાવધાની રાખો",
        "avoid_label": "🚫 કામ ટાળો",
        "sandhi_label": "🌀 સંધિ — સુષુમ્ના સક્રિય",
        "sandhi_note": "આ સ્વર-પરિવર્તનનો સમય છે. ફક્ત ધ્યાન અને આધ્યાત્મિક કાર્ય માટે શ્રેષ્ઠ. સાંસારિક કામ ટાળો.",
        "refresh": "🔄 રિફ્રેશ કરો",
        "last_updated": "છેલ્લી વાર અપડેટ:",
        "timeline": "⏱️ આજનો સ્વર ટાઇમલાઇન",
        "cycle": "તત્વ ચક્ર",
        "shukla": "શુક્લ પક્ષ",
        "krishna": "કૃષ્ણ પક્ષ",
    }
}

# ─────────────────────────────────────────────
# 2. ACTIVITY GUIDANCE (Source: Shiva Swarodaya)
# ─────────────────────────────────────────────
activity_guide = {
    "chandra": {
        "label_en": "Chandra Swar Active 🔵",
        "label_gu": "ચન્દ્ર સ્વર સક્રિય 🔵",
        "activities_en": [
            "Long distance travel & pilgrimage",
            "New agreements, treaties, contracts",
            "Marriage & relationships",
            "Starting education or learning",
            "Administering or taking medicine",
            "Worship, mantra recitation, yoga",
            "Agriculture & sowing seeds",
            "Purchasing jewellery or property",
            "Entering a new home",
            "Creative & mental work",
            "Meeting officials or important people",
            "Collecting wealth, grains, domestic items",
        ],
        "activities_gu": [
            "લાંબી મુસાફરી અને તીર્થ",
            "નવા કરાર, સંધિ, સમજૂતી",
            "લગ્ન અને સંબંધ",
            "ભણતર શરૂ કરવું",
            "દવા આપવી કે લેવી",
            "પૂજા, મંત્ર, યોગ",
            "ખેતી અને બીજ વાવવા",
            "ઘરેણાં કે જમીન ખરીદવી",
            "નવા ઘરમાં પ્રવેશ",
            "સર્જનાત્મક અને માનસિક કાર્ય",
            "અધિકારી કે મહત્વના વ્યક્તિ સાથે મળવું",
            "સંપત્તિ, અનાજ, ઘરેલુ વસ્તુઓ એકઠી કરવી",
        ],
    },
    "surya": {
        "label_en": "Surya Swar Active 🟠",
        "label_gu": "સૂર્ય સ્વર સક્રિય 🟠",
        "activities_en": [
            "Physical exercise & hard labour",
            "Writing & academic learning",
            "Bathing, eating, daily routines",
            "Sale & purchase of goods",
            "Crossing rivers or difficult terrain",
            "Destruction of obstacles or enemies",
            "Climbing or adventurous activities",
            "Taking or giving donations",
            "Agriculture (physical work)",
            "Dealing with animals",
        ],
        "activities_gu": [
            "કસરત અને શારીરિક શ્રમ",
            "લેખન અને અભ્યાસ",
            "સ્નાન, ભોજન, દૈનિક ક્રિયાઓ",
            "ખરીદ-વેચાણ",
            "નદી કે મુશ્કેલ ભૂમિ પાર કરવી",
            "અવરોધ કે શત્રુ નષ્ટ કરવા",
            "ચઢાણ કે સાહસ",
            "દાન આપવું કે લેવું",
            "ખેતી (શારીરિક કામ)",
            "પ્રાણીઓ સાથે વ્યવહાર",
        ],
    },
}

tattva_guide = {
    "Prithvi": {
        "status": "auspicious",
        "note_en": "Stable & grounded energy. Excellent for all important work.",
        "note_gu": "સ્થિર અને ધરતી જેવી ઊર્જા. મહત્વના કામ માટે ઉત્તમ.",
        "emoji": "🟤",
    },
    "Jal": {
        "status": "auspicious",
        "note_en": "Flowing & nourishing energy. Good for travel, relationships, healing.",
        "note_gu": "વહેતી અને પોષક ઊર્જા. મુસાફરી, સંબંધ, ઉપચાર માટે સારું.",
        "emoji": "💧",
    },
    "Agni": {
        "status": "caution",
        "note_en": "Fiery & transformative energy. Good for debate. Avoid new starts.",
        "note_gu": "અગ્નિ જેવી ઊર્જા. ચર્ચા-વાદ માટે સારું. નવું કામ ટાળો.",
        "emoji": "🔥",
    },
    "Vayu": {
        "status": "avoid",
        "note_en": "Unstable & moving energy. Avoid all important work.",
        "note_gu": "અસ્થિર ઊર્જા. તમામ મહત્વના કામ ટાળો.",
        "emoji": "💨",
    },
    "Akash": {
        "status": "avoid",
        "note_en": "Etheric energy. For meditation & spiritual practice only.",
        "note_gu": "આકાશ તત્વ. ફક્ત ધ્યાન અને આધ્યાત્મિક અભ્યાસ માટે.",
        "emoji": "✨",
    },
}

# ─────────────────────────────────────────────
# 3. PAGE CONFIG & MOBILE CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="Swar Shastra Pro", page_icon="🕉️", layout="wide")

st.markdown("""
<style>
/* Mobile-friendly base */
@media (max-width: 768px) {
    .block-container { padding: 1rem 0.5rem !important; }
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1rem !important; }
}
/* Hero card */
.hero-card {
    padding: 20px;
    border-radius: 14px;
    color: white;
    text-align: center;
    margin-bottom: 16px;
}
/* Guidance card */
.guide-card {
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    border-left: 5px solid;
}
.guide-auspicious { background: #052e16; border-color: #22c55e; }
.guide-caution { background: #431407; border-color: #f97316; }
.guide-avoid { background: #3b0764; border-color: #a855f7; }
.guide-sandhi { background: #1e293b; border-color: #94a3b8; }
/* Timeline bar */
.timeline-slot {
    display: inline-block;
    height: 32px;
    text-align: center;
    font-size: 10px;
    line-height: 32px;
    color: white;
    border-radius: 4px;
    margin: 1px;
    overflow: hidden;
}
.slot-chandra { background: #1E3A8A; }
.slot-surya   { background: #9A3412; }
.slot-active  { border: 2px solid #FFD700; }
/* Activity list */
.activity-item {
    padding: 6px 10px;
    margin: 4px 0;
    border-radius: 6px;
    background: rgba(255,255,255,0.07);
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. SIDEBAR
# ─────────────────────────────────────────────
lang_choice = st.sidebar.radio("Language / ભાષા", ["English", "ગુજરાતી"])
t = trans[lang_choice]
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)

st.sidebar.header(t["settings"])
selected_date = st.sidebar.date_input(t["date_pick"], now_ist.date())
city_name = st.sidebar.text_input(t["city"], "Mumbai")
lat = st.sidebar.number_input(t["lat"], value=19.0760, format="%.4f")
lon = st.sidebar.number_input(t["long"], value=72.8777, format="%.4f")

def get_sunrise_api(date_obj, lat, lon):
    try:
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date_obj.strftime('%Y-%m-%d')}&formatted=0"
        response = requests.get(url, timeout=5).json()
        if response['status'] == 'OK':
            utc_sun = datetime.fromisoformat(response['results']['sunrise'])
            return utc_sun.astimezone(ist).time()
    except Exception:
        pass
    return time(6, 12)

if st.sidebar.button(t["get_sun"]):
    st.session_state['sunrise'] = get_sunrise_api(selected_date, lat, lon)
elif 'sunrise' not in st.session_state:
    st.session_state['sunrise'] = get_sunrise_api(now_ist.date(), lat, lon)

final_sunrise = st.sidebar.time_input(t["sunrise"], value=st.session_state['sunrise'])

st.sidebar.markdown("---")
paksha_options = [t["shukla"], t["krishna"]]
paksha_raw = st.sidebar.selectbox(t["paksha"], paksha_options)
paksha = "Shukla" if paksha_raw == t["shukla"] else "Krishna"
tithi = st.sidebar.number_input(t["tithi"], 1, 15, 1)

# ─────────────────────────────────────────────
# 5. CORE LOGIC
# ─────────────────────────────────────────────
chandra_group = [1, 2, 3, 7, 8, 9, 13, 14, 15]

def get_start_swar(paksha, tithi_num):
    is_chandra = tithi_num in chandra_group
    if paksha == "Shukla":
        return "chandra" if is_chandra else "surya"
    else:
        return "surya" if is_chandra else "chandra"

tattva_sequence = [
    ("Prithvi", 20),
    ("Jal",     16),
    ("Agni",    12),
    ("Vayu",     8),
    ("Akash",    4),
]
SANDHI_MINS = 4  # minutes before/after swar change = Sushumna/Sandhi

start_swar_key = get_start_swar(paksha, tithi)
sunrise_dt = ist.localize(datetime.combine(selected_date, final_sunrise))

# Build schedule
schedule = []
current_swar_key = start_swar_key

for i in range(12):
    s_time = sunrise_dt + timedelta(hours=i * 2)
    e_time = s_time + timedelta(hours=2)
    is_today = selected_date == now_ist.date()
    is_active = is_today and (s_time <= now_ist < e_time)
    is_sandhi = is_today and (
        abs((now_ist - s_time).total_seconds()) < SANDHI_MINS * 60 or
        abs((now_ist - e_time).total_seconds()) < SANDHI_MINS * 60
    )

    # Tattva within this slot
    active_tattva = None
    tattva_cycle_num = None
    if is_active:
        mins_passed = int((now_ist - s_time).total_seconds() / 60)
        cycle_mins = mins_passed % 60
        cycle_num = (mins_passed // 60) + 1
        tattva_cycle_num = cycle_num
        elapsed = 0
        for t_name, t_dur in tattva_sequence:
            elapsed += t_dur
            if cycle_mins < elapsed:
                active_tattva = t_name
                break

    schedule.append({
        "swar_key": current_swar_key,
        "swar_label": t["left"] if current_swar_key == "chandra" else t["right"],
        "start": s_time,
        "end": e_time,
        "is_active": is_active,
        "is_sandhi": is_sandhi,
        "active_tattva": active_tattva,
        "cycle_num": tattva_cycle_num,
    })
    current_swar_key = "right" if current_swar_key == "chandra" else "chandra"
    current_swar_key = "surya" if current_swar_key == "right" else "chandra"
    # Simpler toggle:
    current_swar_key = "surya" if schedule[-1]["swar_key"] == "chandra" else "chandra"

# ─────────────────────────────────────────────
# 6. TITLE & REFRESH
# ─────────────────────────────────────────────
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title(t["title"])
with col_refresh:
    st.write("")
    if st.button(t["refresh"]):
        st.rerun()
    st.caption(f"{t['last_updated']} {now_ist.strftime('%I:%M %p')}")

st.success(f"🌅 {t['sun_found']} **{final_sunrise.strftime('%I:%M %p')}**")

# ─────────────────────────────────────────────
# 7. LIVE HERO CARD
# ─────────────────────────────────────────────
active_slot = next((s for s in schedule if s["is_active"]), None)

if active_slot and selected_date == now_ist.date():
    swar_key = active_slot["swar_key"]
    tattva_key = active_slot["active_tattva"]
    t_info = tattva_guide.get(tattva_key, {})
    t_emoji = t_info.get("emoji", "")
    t_note = t_info.get("note_en" if lang_choice == "English" else "note_gu", "")
    t_status = t_info.get("status", "auspicious")
    cycle_num = active_slot["cycle_num"]

    color = "#1E3A8A" if swar_key == "chandra" else "#9A3412"
    swar_label = t["left"] if swar_key == "chandra" else t["right"]

    if active_slot["is_sandhi"]:
        st.markdown(f"""
        <div class="hero-card" style="background:{color}; border:2px solid #94a3b8;">
            <h2 style="margin:0;">{t['sandhi_label']}</h2>
            <p style="margin-top:8px; color:#CBD5E1;">{t['sandhi_note']}</p>
        </div>""", unsafe_allow_html=True)
    else:
        tattva_full = f"{t_emoji} {tattva_key}" if tattva_key else "—"
        cycle_text = f" ({t['cycle']} {cycle_num}/2)" if cycle_num else ""
        st.markdown(f"""
        <div class="hero-card" style="background:{color}; border:2px solid #ffffff;">
            <h2 style="margin:0;">{swar_label}</h2>
            <h3 style="margin:8px 0 4px 0;">{t['tattva_running']} {tattva_full}{cycle_text}</h3>
            <p style="margin:4px 0; color:#FDE68A; font-size:0.9rem;">{t_note}</p>
        </div>""", unsafe_allow_html=True)

    # ── What to do now ──
    st.markdown(f"### {t['what_now']}")

    # Tattva-level guidance
    if active_slot["is_sandhi"]:
        st.markdown(f"""<div class="guide-card guide-sandhi">
            <strong>{t['sandhi_label']}</strong><br>{t['sandhi_note']}
        </div>""", unsafe_allow_html=True)
    elif t_status == "auspicious":
        note = t_info.get("note_en" if lang_choice == "English" else "note_gu", "")
        st.markdown(f"""<div class="guide-card guide-auspicious">
            <strong>{t['auspicious_label']} — {tattva_full}</strong><br>{note}
        </div>""", unsafe_allow_html=True)
    elif t_status == "caution":
        note = t_info.get("note_en" if lang_choice == "English" else "note_gu", "")
        st.markdown(f"""<div class="guide-card guide-caution">
            <strong>{t['caution_label']} — {tattva_full}</strong><br>{note}
        </div>""", unsafe_allow_html=True)
    else:
        note = t_info.get("note_en" if lang_choice == "English" else "note_gu", "")
        st.markdown(f"""<div class="guide-card guide-avoid">
            <strong>{t['avoid_label']} — {tattva_full}</strong><br>{note}
        </div>""", unsafe_allow_html=True)

    # Swar-level activities
    guide = activity_guide[swar_key]
    swar_lbl = guide["label_en"] if lang_choice == "English" else guide["label_gu"]
    acts = guide["activities_en"] if lang_choice == "English" else guide["activities_gu"]
    st.markdown(f"**{swar_lbl} — Recommended Activities:**")
    cols = st.columns(2)
    for i, act in enumerate(acts):
        with cols[i % 2]:
            st.markdown(f"<div class='activity-item'>• {act}</div>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# 8. VISUAL TIMELINE BAR
# ─────────────────────────────────────────────
st.markdown(f"### {t['timeline']}")
timeline_html = '<div style="display:flex; flex-wrap:wrap; gap:2px; margin-bottom:12px;">'
for slot in schedule:
    css_class = "slot-chandra" if slot["swar_key"] == "chandra" else "slot-surya"
    active_border = " slot-active" if slot["is_active"] else ""
    label = slot["start"].strftime("%-I%p")
    swar_title = slot["swar_label"]
    timeline_html += f'<div class="timeline-slot {css_class}{active_border}" style="width:calc(8.33% - 4px);" title="{swar_title}">{label}</div>'
timeline_html += '</div>'
timeline_html += '<div style="display:flex;gap:16px;font-size:0.8rem;margin-bottom:8px;">'
timeline_html += '<span><span style="display:inline-block;width:12px;height:12px;background:#1E3A8A;border-radius:2px;"></span> Chandra (Left)</span>'
timeline_html += '<span><span style="display:inline-block;width:12px;height:12px;background:#9A3412;border-radius:2px;"></span> Surya (Right)</span>'
timeline_html += '<span><span style="display:inline-block;width:12px;height:12px;background:#FFD700;border-radius:2px;"></span> Active Now</span>'
timeline_html += '</div>'
st.markdown(timeline_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 9. FULL SCHEDULE TABLE WITH EXPANDABLE GUIDANCE
# ─────────────────────────────────────────────
st.markdown(f"### {t['schedule']} {selected_date.strftime('%d %B %Y')}")

for slot in schedule:
    swar_key = slot["swar_key"]
    color = "#1E3A8A" if swar_key == "chandra" else "#9A3412"
    status_badge = f" &nbsp; {t['active_now']}" if slot["is_active"] else ""
    time_range = f"{slot['start'].strftime('%I:%M %p')} – {slot['end'].strftime('%I:%M %p')}"
    swar_label = t["left"] if swar_key == "chandra" else t["right"]

    with st.expander(f"{time_range}  |  {swar_label}{status_badge}", expanded=slot["is_active"]):
        guide = activity_guide[swar_key]
        acts = guide["activities_en"] if lang_choice == "English" else guide["activities_gu"]
        swar_lbl = guide["label_en"] if lang_choice == "English" else guide["label_gu"]

        st.markdown(f"**{swar_lbl}**")

        # Tattva mini-timeline for this slot
        st.markdown("**Tattva sequence within this slot:**")
        tv_cols = st.columns(5)
        tv_names = ["Prithvi 🟤", "Jal 💧", "Agni 🔥", "Vayu 💨", "Akash ✨"]
        tv_mins  = [20, 16, 12, 8, 4]
        for idx, (tv_col, tv_n, tv_m) in enumerate(zip(tv_cols, tv_names, tv_mins)):
            with tv_col:
                st.markdown(f"<div style='text-align:center;font-size:0.75rem;'>{tv_n}<br><b>{tv_m} min</b></div>", unsafe_allow_html=True)

        st.markdown("**Recommended activities:**")
        cols = st.columns(2)
        for i, act in enumerate(acts):
            with cols[i % 2]:
                st.markdown(f"<div class='activity-item'>• {act}</div>", unsafe_allow_html=True)
