import streamlit as st
import requests
from datetime import datetime, timedelta, time
import pytz

# 1. Translation Dictionary
trans = {
    "English": {
        "title": "🕉️ Swar Shastra Pro Assistant",
        "settings": "Location & Date Settings",
        "date_pick": "Select Date",
        "city": "Enter City (for reference)",
        "lat": "Latitude (અક્ષાંશ)",
        "long": "Longitude (રેખાંશ)",
        "get_sun": "Fetch Sunrise Automatically",
        "sun_found": "Sunrise found at:",
        "sunrise": "Sunrise Time",
        "lang": "Language",
        "left": "Left (Chandra Swar)",
        "right": "Right (Surya Swar)",
        "tattva_title": "Current Tattva",
        "schedule": "📅 Schedule for",
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
        "left": "ડાબું નાક (ચંદ્ર સ્વર)",
        "right": "જમણું નાક (સૂર્ય સ્વર)",
        "tattva_title": "અત્યારનું તત્વ",
        "schedule": "📅 દૈનિક શિડ્યુલ:",
    }
}

st.set_page_config(page_title="Swar Shastra Pro", page_icon="🕉️")
lang_choice = st.sidebar.radio("Language", ["English", "ગુજરાતી"])
t = trans[lang_choice]

st.title(t["title"])

# --- Sidebar Inputs ---
st.sidebar.header(t["settings"])
selected_date = st.sidebar.date_input(t["date_pick"], datetime.now())
city_name = st.sidebar.text_input(t["city"], "Mumbai")
lat = st.sidebar.number_input(t["lat"], value=19.0760, format="%.4f") # Mumbai Lat
lon = st.sidebar.number_input(t["long"], value=72.8777, format="%.4f") # Mumbai Long

# --- Fetch Sunrise Logic ---
def get_sunrise_api(date_obj, lat, lon):
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date_obj.strftime('%Y-%m-%d')}&formatted=0"
    response = requests.get(url).json()
    if response['status'] == 'OK':
        # Convert UTC to IST (Indian Standard Time)
        utc_sun = datetime.fromisoformat(response['results']['sunrise'])
        ist_sun = utc_sun.astimezone(pytz.timezone('Asia/Kolkata'))
        return ist_sun.time()
    return time(7, 12) # Fallback

if st.sidebar.button(t["get_sun"]):
    auto_sunrise = get_sunrise_api(selected_date, lat, lon)
    st.session_state['sunrise'] = auto_sunrise
else:
    if 'sunrise' not in st.session_state:
        st.session_state['sunrise'] = time(7, 12)

final_sunrise = st.sidebar.time_input(t["sunrise"], value=st.session_state['sunrise'])

# --- Swar Logic (Same as before) ---
st.sidebar.markdown("---")
paksha = st.sidebar.selectbox("Paksha", ["Shukla", "Krishna"])
tithi = st.sidebar.number_input("Tithi (1-15)", 1, 15, 1)

def get_start_swar(p, tithi):
    chandra_group = [1, 2, 3, 7, 8, 9, 13, 14, 15]
    if p == "Shukla":
        return t["left"] if tithi in chandra_group else t["right"]
    else:
        return t["right"] if tithi in chandra_group else t["left"]

start_swar = get_start_swar(paksha, tithi)
st.success(f"{t['sun_found']} **{final_sunrise.strftime('%I:%M %p')}**")

# --- Display Schedule ---
sunrise_dt = datetime.combine(selected_date, final_sunrise)
now = datetime.now()

schedule_data = []
current_swar = start_swar

for i in range(12):
    s_time = sunrise_dt + timedelta(hours=i*2)
    e_time = s_time + timedelta(hours=2)
    active = "🟢" if s_time <= now < e_time else ""
    
    schedule_data.append({
        "Time": f"{s_time.strftime('%I:%M %p')} - {e_time.strftime('%I:%M %p')}",
        "Swar": current_swar,
        "Status": active
    })
    current_swar = t["right"] if current_swar == t["left"] else t["left"]

st.write(f"### {t['schedule']} {selected_date.strftime('%d-%m-%Y')}")
st.table(schedule_data)
