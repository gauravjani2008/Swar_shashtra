import streamlit as st
from datetime import datetime, timedelta, time

# 1. Translation Dictionary
trans = {
    "English": {
        "title": "🕉️ Swar Shastra Assistant",
        "subtitle": "Bhrigu Nandi Nadi & Swara Yoga",
        "settings": "Daily Settings",
        "paksha": "Select Paksha",
        "tithi": "Sunrise Tithi (1-15)",
        "sunrise": "Sunrise Time",
        "lang": "Select Language",
        "rule_msg": "Rule: Sunrise Tithi applies for the full 24 hours.",
        "start_swar": "Sunrise Starting Swar",
        "left": "Left (Chandra Swar)",
        "right": "Right (Surya Swar)",
        "active": "🟢 ACTIVE NOW",
        "schedule": "📅 Daily 2-Hour Schedule",
        "time_slot": "Time Slot",
        "swar": "Active Swar",
        "status": "Status",
        "tattva_title": "⏳ Current Tattva (Sub-cycle)",
        "prithvi": "Prithvi (Earth)", "jal": "Jal (Water)", "agni": "Agni (Fire)", 
        "vayu": "Vayu (Air)", "akash": "Akash (Ether)"
    },
    "ગુજરાતી": {
        "title": "🕉️ સ્વર શાસ્ત્ર મદદનીશ",
        "subtitle": "ભૃગુ નંદી નાડી અને સ્વર યોગ",
        "settings": "દૈનિક સેટિંગ્સ",
        "paksha": "પક્ષ પસંદ કરો",
        "tithi": "સૂર્યોદય વખતની તિથિ (૧-૧૫)",
        "sunrise": "સૂર્યોદય સમય",
        "lang": "ભાષા બદલો",
        "rule_msg": "નિયમ: સૂર્યોદયની તિથિ આખા દિવસ માટે ગણાય છે.",
        "start_swar": "સૂર્યોદયનો પ્રથમ સ્વર",
        "left": "ડાબું નાક (ચંદ્ર સ્વર)",
        "right": "જમણું નાક (સૂર્ય સ્વર)",
        "active": "🟢 અત્યારે ચાલુ",
        "schedule": "📅 આખા દિવસનું શિડ્યુલ",
        "time_slot": "સમયગાળો",
        "swar": "ચાલુ સ્વર",
        "status": "સ્થિતિ",
        "tattva_title": "⏳ અત્યારનું તત્વ",
        "prithvi": "પૃથ્વી", "jal": "જલ", "agni": "અગ્નિ", 
        "vayu": "વાયુ", "akash": "આકાશ"
    }
}

# 2. UI Setup
st.set_page_config(page_title="Swar Shastra", page_icon="🕉️")
lang_choice = st.sidebar.radio("Language / ભાષા", ["English", "ગુજરાતી"])
t = trans[lang_choice]

st.title(t["title"])
st.subheader(t["subtitle"])

# 3. Sidebar Inputs
st.sidebar.markdown("---")
st.sidebar.header(t["settings"])
paksha_type = st.sidebar.selectbox(t["paksha"], ["Shukla / શુક્લ", "Krishna / કૃષ્ણ"])
tithi_num = st.sidebar.number_input(t["tithi"], min_value=1, max_value=15, value=1)
sunrise_val = st.sidebar.time_input(t["sunrise"], value=time(7, 12))

# 4. Logic: Determine Starting Swar
def get_starting_swar(paksha, tithi):
    chandra_tithis = [1, 2, 3, 7, 8, 9, 13, 14, 15]
    if "Shukla" in paksha:
        return t["left"] if tithi in chandra_tithis else t["right"]
    else:
        return t["right"] if tithi in chandra_tithis else t["left"]

first_swar = get_starting_swar(paksha_type, tithi_num)

# 5. Calculate Schedule
now = datetime.now()
sunrise_dt = datetime.combine(now.date(), sunrise_val)

st.info(f"📍 {t['rule_msg']} \n\n **{t['start_swar']}:** {first_swar}")

# Tattva Logic (Sequence repeats every 60 mins within the 120 min swar cycle)
tattvas = [
    (t["prithvi"], 20), (t["jal"], 16), (t["agni"], 12), (t["vayu"], 8), (t["akash"], 4)
]

schedule_data = []
current_swar = first_swar
active_swar_name = ""
active_end_time = None

for i in range(12):
    s_time = sunrise_dt + timedelta(hours=i*2)
    e_time = s_time + timedelta(hours=2)
    
    is_active = s_time <= now < e_time
    status_text = t["active"] if is_active else ""
    
    if is_active:
        active_swar_name = current_swar
        active_end_time = e_time
        
        # Calculate Current Tattva
        mins_passed = (now - s_time).seconds // 60
        mins_in_hour = mins_passed % 60
        elapsed = 0
        current_tattva = ""
        for name, duration in tattvas:
            elapsed += duration
            if mins_in_hour < elapsed:
                current_tattva = name
                break
        active_tattva = current_tattva

    schedule_data.append({
        t["time_slot"]: f"{s_time.strftime('%I:%M %p')} - {e_time.strftime('%I:%M %p')}",
        t["swar"]: current_swar,
        t["status"]: status_text
    })
    
    # Flip Swar
    current_swar = t["right"] if current_swar == t["left"] else t["left"]

# 6. Display Active Card
if active_swar_name:
    color = "#3498db" if t["left"] in active_swar_name else "#e67e22"
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:15px; text-align:center; color:white;">
            <h2 style="margin:0;">{active_swar_name}</h2>
            <p style="margin:5px 0 0 0;">{t['active']} | {t['tattva_title']}: <b>{active_tattva}</b></p>
        </div>
    """, unsafe_allow_html=True)

# 7. Display Table
st.write(f"### {t['schedule']}")
st.table(schedule_data)
