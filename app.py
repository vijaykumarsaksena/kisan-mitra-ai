import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# --- 1. डेटाबेस लॉजिक (Database Logic) ---
def init_all_dbs():
    conn = sqlite3.connect('kisan_mitra_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tech_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, lang TEXT, crop TEXT, moisture INTEGER, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS finance_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, crop TEXT, cost REAL, revenue REAL, profit REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS mushroom_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, temp REAL, humidity REAL, status TEXT)''')
    conn.commit()
    conn.close()

# --- 2. डेटा एक्सपोर्ट फंक्शन (Data Export) ---
def export_data_ui(t):
    st.sidebar.markdown("---")
    st.sidebar.subheader(t["export_head"])
    
    conn = sqlite3.connect('kisan_mitra_final.db')
    df = pd.read_sql_query("SELECT * FROM finance_logs", conn)
    conn.close()

    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button(
            label=t["btn_download"],
            data=csv,
            file_name=f'kisan_mitra_report_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
    else:
        st.sidebar.info(t["no_data"])

# --- 3. भाषा शब्दकोश (Multi-lingual Dictionary) ---
lang_dict = {
    "Hindi": {
        "title": "🚜 डिजिटल कृषि मित्र Pro",
        "tab1": "📡 खेत निगरानी", "tab2": "💰 डिजिटल बहीखाता", "tab3": "🍄 मशरूम लैब",
        "export_head": "📥 रिपोर्ट डाउनलोड", "btn_download": "Excel डाउनलोड करें",
        "no_data": "डेटा उपलब्ध नहीं है", "btn_save": "सुरक्षित करें",
        "crops": ["मक्का", "आलू", "मशरूम", "धान"],
        "alerts": ["⚠️ सिंचाई आवश्यक!", "✅ नमी पर्याप्त।", "🌊 पानी अधिक!"]
    },
    "Angika": {
        "title": "🚜 डिजिटल कृषि मित्र Pro",
        "tab1": "📡 खेत निगरानी", "tab2": "💰 डिजिटल बहीखाता", "tab3": "🍄 मशरूम लैब",
        "export_head": "📥 रिपोर्ट डाउनलोड", "btn_download": "Excel डाउनलोड करियै",
        "no_data": "डेटा नै छै", "btn_save": "सुरक्षित करियै",
        "crops": ["मक्का", "आलू", "मशरूम", "धान"],
        "alerts": ["⚠️ पटवन के जरूरत छै!", "✅ नमी ठीक छै।", "🌊 पानी बेसी छै!"]
    },
    "Bhojpuri": {
        "title": "🚜 डिजिटल कृषि मित्र Pro",
        "tab1": "📡 खेत निगरानी", "tab2": "💰 डिजिटल बहीखाता", "tab3": "🍄 मशरूम लैब",
        "export_head": "📥 रिपोर्ट डाउनलोड", "btn_download": "Excel डाउनलोड करीं",
        "no_data": "डेटा नईखे", "btn_save": "सुरक्षित करीं",
        "crops": ["मक्का", "आलू", "खूँभी", "धान"],
        "alerts": ["⚠️ पानी चलावे के जरूरत बा!", "✅ नमी ठीक बा।", "🌊 पानी ढेर बा!"]
    }
}

# --- 4. मुख्य ऐप (Main App) ---
def main():
    st.set_page_config(page_title="Kisan Mitra Pro v3", layout="wide")
    init_all_dbs()

    selected_lang = st.sidebar.selectbox("Language / भाषा", list(lang_dict.keys()))
    t = lang_dict[selected_lang]
    st.title(t["title"])
    
    # एक्सपोर्ट फीचर कॉल
    export_data_ui(t)

    tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

    # --- TAB 1: FIELD MONITORING ---
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            crop = st.selectbox("फसल", t["crops"], key="f1")
            moisture = st.slider("नमी (%)", 0, 100, 45)
            status = t["alerts"][0] if moisture < 30 else (t["alerts"][1] if moisture <= 60 else t["alerts"][2])
            st.info(status)
            if st.button(t["btn_save"], key="b1"): st.toast("Saved!")
        with c2:
            st.line_chart(np.random.randn(10, 1) + (moisture/10))

    # --- TAB 2: FINANCE (CA MODULE) ---
    with tab2:
        st.subheader("📊 Profit & Loss Analysis")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            cost = st.number_input("कुल लागत (Input Cost ₹)", value=5000)
        with f_col2:
            rev = st.number_input("कुल आय (Revenue ₹)", value=8000)
            profit = rev - cost
            st.metric("शुद्ध मुनाफा (Net Profit)", f"₹{profit}", delta=f"{profit}")
        
        if st.button(t["btn_save"], key="b2"):
            conn = sqlite3.connect('kisan_mitra_final.db')
            c = conn.cursor()
            c.execute("INSERT INTO finance_logs (date, crop, cost, revenue, profit) VALUES (?, ?, ?, ?, ?)", 
                      (datetime.now().strftime("%Y-%m-%d"), crop, cost, rev, profit))
            conn.commit()
            conn.close()
            st.success("Record Added to Ledger!")

    # --- TAB 3: MUSHROOM LAB ---
    with tab3:
        st.subheader("🍄 Lab Climate Control")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            temp = st.number_input("Temp (°C)", 10, 40, 22)
            hum = st.slider("Humidity (%)", 0, 100, 85)
        with m_col2:
            if temp > 24: st.error("⚠️ Cooling ON")
            if hum < 80: st.warning("💧 Humidifier ON")
            else: st.success("✅ Ideal Condition")

if __name__ == "__main__":
    main()
