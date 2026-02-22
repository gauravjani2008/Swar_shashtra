import streamlit as st
import requests
from datetime import datetime, timedelta, time
import pytz
import pandas as pd

# 1. Translation Dictionary
trans = {
    "English": {
        "title": "🕉️ Swar Shastra Pro Assistant",
        "settings": "Location & Date Settings",
        "date_pick": "Select Date",
        "city": "Enter City (for reference)",
        "lat": "Latitude",
        "long": "Longitude",
        "get_sun": "Fetch Sunrise Automatically",
        "sun_found": "Sunrise locked at:",
        "sunrise": "Sunrise Time",
        "lang": "Language",
        "left": "Left (Chandra Swar) 🔵",
        "right": "Right (Surya Swar) 🟠",
        "schedule": "📅 Master Schedule for",
        "paksha": "Select Paksha",
        "tithi": "Sunrise Tithi (1-15)",
        "active_now": "🟢 ACTIVE NOW",
        "tattva_running": "Current Tattva (Element):",
    },
    "ગુજરાતી": {
        "title": "🕉️ સ્વર શાસ્ત્ર પ્રો મદદનીશ",
        "settings": "સ્થળ અને તારીખ સેટિંગ્સ",
        "date_pick": "તારીખ પસંદ કરો",
        "city": "શહેરનું નામ",
        "lat": "અક્ષાંશ (Latitude)",
        "long": "રેખાંશ (Longitude)",
        "get_sun": "સૂર્યોદય સમય મેળવો",
        "sun_found": "સૂર્યોદયનો સમય:",
        "sunrise": "સૂર્યોદય સમય",
        "lang": "ભાષા",
        "left": "ડાબું નાક (ચંદ્ર સ્વર) 🔵",
        "right": "જમણું નાક (સૂર્ય સ્વર) 🟠",
        "schedule": "📅 દૈનિક શિડ્યુલ:",
        "paksha": "પક્ષ પસંદ કરો",
        "tithi": "સૂર્યોદય વખતની તિથિ (૧-૧૫)",
        "active_now": "🟢 અત્યારે ચાલુ",
        "tattva_running": "અત્યારનું તત્વ:",
    }
}

st.set_page_config(page_title="Swar Shastra Pro", page_icon="🕉️", layout="wide")
lang_choice = st.sidebar.radio("Language / ભાષા", ["English", "ગુજરાતી"])
t = trans[lang_choice]

st.title(t["title"])

# --- Timezone Enforcer (CRITICAL FIX) ---
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)

# --- Sidebar Inputs ---
st.sidebar.header(t["settings"])
selected_date = st.sidebar.date_input(t["date_pick"], now_ist.date())
city_name = st.sidebar.text_input(t["city"], "Mumbai")
lat = st.sidebar.number_input(t["lat"], value=19.0760, format="%.4f") 
lon = st.sidebar.number_input(t["long"], value=72.8777, format="%.4f") 

# --- Fetch Sunrise Logic ---
def get_sunrise_api(date_obj, lat, lon):
    try:
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date_obj.strftime('%Y-%m-%d')}&formatted=0"
        response = requests.get(url).json()
        if response['status'] == 'OK':
            utc_sun = datetime.fromisoformat(response['results']['sunrise'])
            ist_sun = utc_sun.astimezone(ist)
            return ist_sun.time()
    except Exception:
        pass
    return time(7, 12) # Fallback

if st.sidebar.button(t["get_sun"]):
    st.session_state['sunrise'] = get_sunrise_api(selected_date, lat, lon)
elif 'sunrise' not in st.session_state:
    st.session_state['sunrise'] = get_sunrise_api(now_ist.date(), 19.0760, 72.8777) # Auto-fetch on load

final_sunrise = st.sidebar.time_input(t["sunrise"], value=st.session_state['sunrise'])

# --- Astrological Logic (Applying your exact rule) ---
st.sidebar.markdown("---")
paksha = st.sidebar.selectbox(t["paksha"], ["Shukla", "Krishna"])
tithi = st.sidebar.number_input(t["tithi"], 1, 15, 1)

def get_start_swar(p, t_num):
    chandra_group = [1, 2, 3, 7, 8, 9, 13, 14, 15]
    if "Shukla" in p:
        return t["left"] if t_num in chandra_group else t["right"]
    else:
        return t["right"] if t_num in chandra_group else t["left"]

start_swar = get_start_swar(paksha, tithi)
st.success(f"🌅 {t['sun_found']} **{final_sunrise.strftime('%I:%M %p')}** (Sunrise Tithi applies for the entire day)")

# --- Schedule & Tattva Calculation ---
# Combine selected date with sunrise time and localize to IST
sunrise_dt = ist.localize(datetime.combine(selected_date, final_sunrise))

schedule_data = []
current_swar = start_swar
active_swar_display = None
active_tattva_display = None

tattva_sequence = [
    ("Prithvi (Earth) 🟤", 20),
    ("Jal (Water) 💧", 16),
    ("Agni (Fire) 🔥", 12),
    ("Vayu (Air) 💨", 8),
    ("Akash (Ether) ✨", 4)
]

for i in range(12):
    s_time = sunrise_dt + timedelta(hours=i*2)
    e_time = s_time + timedelta(hours=2)
    
    is_active = s_time <= now_ist < e_time
    status = t["active_now"] if is_active else ""
    
    if is_active:
        active_swar_display = current_swar
        # Calculate exactly which Tattva is running right now
        mins_passed = int((now_ist - s_time).total_seconds() / 60)
        cycle_mins = mins_passed % 60 # Tattvas repeat every 60 mins within the 120 min swar
        
        elapsed = 0
        for t_name, t_dur in tattva_sequence:
            elapsed += t_dur
            if cycle_mins < elapsed:
                active_tattva_display = t_name
                break

    schedule_data.append({
        "Time Slot": f"{s_time.strftime('%I:%M %p')} - {e_time.strftime('%I:%M %p')}",
        "Swar": current_swar,
        "Status": status
    })
    
    current_swar = t["right"] if current_swar == t["left"] else t["left"]

# --- Live Dashboard (The "Hero" Section) ---
if active_swar_display and selected_date == now_ist.date():
    color = "#1E3A8A" if "Left" in active_swar_display or "ડાબું" in active_swar_display else "#9A3412"
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; color:white; text-align:center; border: 2px solid #ffffff;">
            <h2 style="margin:0;">{active_swar_display}</h2>
            <h4 style="margin-top:10px;">{t['tattva_running']} <span style="color:#FFD700;">{active_tattva_display}</span></h4>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- Render the Data Table with Highlights ---
st.write(f"### {t['schedule']} {selected_date.strftime('%d-%m-%Y')}")

df = pd.DataFrame(schedule_data)

# Highlight the active row
def highlight_row(row):
    if row['Status'] == t["active_now"]:
        return ['background-color: #004d40; color: white'] * len(row)
    return [''] * len(row)

st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True, hide_index=True)
