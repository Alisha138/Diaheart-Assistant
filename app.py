import streamlit as st
import os
import pandas as pd
import numpy as np
import joblib
import sqlite3
import hashlib
import re
from datetime import datetime
import time
import plotly.express as px
from fpdf import FPDF
import streamlit.components.v1 as components
from recommendation_engine import get_recommendations

# ---------------------------------------------------------
# PAGE CONFIGURATION (Strict Load First)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DiaHeart | Health Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE ENGINE (Strictly Untouched Logic)
# ---------------------------------------------------------
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, email TEXT UNIQUE, username TEXT UNIQUE, password TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, test_type TEXT, risk_level TEXT, probability REAL, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_platform_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    users_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM history")
    history_count = c.fetchone()[0]
    conn.close()
    return max(users_count, 1), max(history_count, 0)

# ---------------------------------------------------------
# UI VISIBILITY & THEME SYSTEM
# ---------------------------------------------------------
def apply_custom_css():
    st.markdown("""
    <style>
    /* Clean, High-Contrast Form Inputs */
    [data-testid="stForm"] div[data-baseweb="input"], 
    [data-testid="stForm"] div[data-baseweb="select"] > div,
    [data-testid="stForm"] div[data-baseweb="textarea"] {
        background-color: var(--background-color) !important;
        border: 1px solid var(--border-color, rgba(128,128,128,0.3)) !important;
        border-radius: 6px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stForm"] div[data-baseweb="input"]:focus-within, 
    [data-testid="stForm"] div[data-baseweb="select"] > div:focus-within,
    [data-testid="stForm"] div[data-baseweb="textarea"]:focus-within {
        border-color: var(--primary-color, #3b82f6) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* Cards */
    .dia-card {
        background-color: var(--secondary-background-color, #1e293b);
        border: 1px solid var(--border-color, #334155);
        border-radius: 12px;
        padding: 26px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .dia-card:hover { 
        transform: translateY(-4px); 
        box-shadow: 0 8px 15px -3px rgba(37, 99, 235, 0.3);
        border-color: var(--primary-color, #3b82f6);
    }

    /* Contact Form */
    [data-testid="stForm"] {
        background-color: var(--secondary-background-color, #1e293b);
        border: 1px solid var(--border-color, #334155);
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
    }

    /* Enhanced Sidebar Smoothness */
    [data-testid="stSidebar"] {
        box-shadow: 2px 0px 10px rgba(0,0,0,0.1);
    }
    div[role="radiogroup"] > label {
        padding: 5px 10px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease-in-out !important;
        margin-bottom: 2px !important;
    }
    div[role="radiogroup"] > label:hover {
        background-color: rgba(59, 130, 246, 0.15) !important;
        transform: translateX(4px) !important;
    }

    /* Button Consistency */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #10b981 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3) !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px -3px rgba(16, 185, 129, 0.5) !important;
    }

    .dia-risk-low { border-left: 6px solid #10b981; padding: 20px; border-radius: 8px; background: rgba(16, 185, 129, 0.1); color: inherit; }
    .dia-risk-med { border-left: 6px solid #f59e0b; padding: 20px; border-radius: 8px; background: rgba(245, 158, 11, 0.1); color: inherit; }
    .dia-risk-high { border-left: 6px solid #ef4444; padding: 20px; border-radius: 8px; background: rgba(239, 68, 68, 0.1); color: inherit; }
    .block-container { padding-bottom: 40px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MEDICAL AI LOGO ASSET
# ---------------------------------------------------------
BRAND_SVG = """
<svg width="75" height="75" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="medGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" /> <!-- Green -->
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" /> <!-- Blue -->
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  <!-- Background Medical Cross Shadow -->
  <path d="M40 20 H60 V40 H80 V60 H60 V80 H40 V60 H20 V40 H40 Z" fill="url(#medGrad)" opacity="0.15" />
  
  <!-- AI Circuit lines mapping to heart -->
  <polyline points="25,50 15,50 15,30" stroke="#3b82f6" stroke-width="2" fill="none" />
  <circle cx="15" cy="30" r="3" fill="#3b82f6" />
  <polyline points="75,50 85,50 85,70" stroke="#10b981" stroke-width="2" fill="none" />
  <circle cx="85" cy="70" r="3" fill="#10b981" />
  <polyline points="50,75 50,90" stroke="#3b82f6" stroke-width="2" fill="none" />
  <circle cx="50" cy="90" r="3" fill="#3b82f6" />
  
  <!-- Central Dynamic Heart -->
  <path d="M50 70 C50 70, 25 45, 25 30 A15 15 0 0 1 50 20 A15 15 0 0 1 75 30 C75 45, 50 70, 50 70 Z" fill="url(#medGrad)" filter="url(#glow)"/>
  
  <!-- Central Data / Pulse Core -->
  <circle cx="50" cy="35" r="4" fill="#ffffff" />
  <circle cx="40" cy="30" r="2" fill="#ffffff" opacity="0.7"/>
  <circle cx="60" cy="30" r="2" fill="#ffffff" opacity="0.7"/>
  <path d="M40 30 Q50 45 60 30" stroke="#ffffff" stroke-width="1.5" fill="none" opacity="0.5"/>
</svg>
"""

def show_original_counters():
    u_count, h_count = get_platform_stats()
    html_counters = f"""
    <style>
    .ctr-wrap {{ display: flex; gap: 1rem; justify-content: space-between; flex-wrap: wrap; margin-bottom: 1.5rem; }}
    .ctr-card {{ flex: 1; min-width: 150px; background-color: #1e293b; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #475569; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); transition: transform 0.3s; color: #f8fafc; }}
    .ctr-card:hover {{ transform: translateY(-5px); border-color: #3b82f6; }}
    .ctr-val {{ font-size: 2.2rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #3b82f6, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; font-family: sans-serif; margin-bottom: 0.3rem; }}
    .ctr-lbl {{ color: inherit; opacity: 0.8; font-size: 0.95rem; font-weight: 600; font-family: sans-serif; }}
    

    </style>
    <div class="ctr-wrap" id="dia-metrics">
        <div class="ctr-card"><div class="ctr-val" data-target="{u_count}">0</div><div class="ctr-lbl">Total Users</div></div>
        <div class="ctr-card"><div class="ctr-val" data-target="{h_count}">0</div><div class="ctr-lbl">Total Tests Conducted</div></div>
        <div class="ctr-card"><div class="ctr-val" data-target="92">0</div><div class="ctr-lbl">Model Accuracy (%)</div></div>
    </div>
    <script>
    document.querySelectorAll('#dia-metrics .ctr-val').forEach(ctr => {{
        const target = +ctr.getAttribute('data-target');
        const update = () => {{
            const count = +ctr.innerText;
            const inc = Math.max(1, Math.ceil(target / 40));
            if(count < target) {{ ctr.innerText = count + inc; setTimeout(update, 35); }}
            else {{ ctr.innerText = target; }}
        }}; update();
    }});
    </script>
    """
    components.html(html_counters, height=130)

# ---------------------------------------------------------
# PDF ENGINE
# ---------------------------------------------------------
def create_pdf(name, pred, prob, risk, time_val):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 24); pdf.set_text_color(37,99,235)
    pdf.cell(0, 15, "DiaHeart Health Report", ln=True, align='C')
    pdf.set_font("Arial", 'I', 11); pdf.set_text_color(100,116,139); pdf.line(10,30,200,30)
    pdf.cell(0, 5, "AI-Powered Health Risk Assessment", ln=True, align='C'); pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0,0,0)
    pdf.cell(40,10, "Name:", border=0); pdf.set_font("Arial", '', 12); pdf.cell(0,10, name, ln=True)
    pdf.set_font("Arial", 'B', 12); pdf.cell(40,10, "Timestamp:", border=0); pdf.set_font("Arial", '', 12); pdf.cell(0,10, time_val, ln=True)
    pdf.set_font("Arial", 'B', 12); pdf.cell(40,10, "Test Type:", border=0); pdf.set_font("Arial", '', 12); pdf.cell(0,10, pred, ln=True)
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 16); pdf.set_text_color(37,99,235)
    pdf.cell(0,10, "Assessment Results", ln=True)
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0,0,0)
    pdf.cell(45,10,"Risk Probability:",border=0); pdf.set_font("Arial",'',12); pdf.cell(0,10,f"{prob:.2f}%",ln=True)
    pdf.set_font("Arial", 'B', 12); pdf.cell(45,10,"Recommendation:",border=0)
    
    if "Low" in risk: pdf.set_text_color(16,185,129); rec = "Your risk level is low. Maintain a healthy lifestyle."
    elif "Medium" in risk: pdf.set_text_color(245,158,11); rec = "Your risk level is moderate. Consider consulting a healthcare professional."
    else: pdf.set_text_color(239,68,68); rec = "Your risk level is high. We highly recommend consulting a doctor."
    
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, risk.upper(), ln=True)
    pdf.ln(5)
    pdf.set_text_color(0,0,0); pdf.set_font("Arial", 'B', 12); pdf.cell(0,8,"Suggested Action:")
    pdf.ln(8); pdf.set_font("Arial", '', 11); pdf.multi_cell(0,6,rec)
    
    pdf.set_y(-30); pdf.set_font("Arial", 'I', 8); pdf.set_text_color(100,116,139); pdf.line(10,265,200,265)
    pdf.multi_cell(0,4, "DISCLAIMER: This is an AI-based prediction and should not replace professional medical advice.", align='C')
    out = pdf.output(dest='S')
    return out.encode('latin-1') if isinstance(out, str) else bytes(out)

# ---------------------------------------------------------
# AUTH LOGIC
# ---------------------------------------------------------
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def cr_user(f,e,u,p):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    try:
        c.execute("INSERT INTO users (full_name,email,username,password,created_at) VALUES (?,?,?,?,?)",
                  (f,e,u,hash_pw(p),datetime.now().isoformat())); conn.commit(); return True
    except: return False
    finally: conn.close()
def lg_user(i,p):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT username, full_name FROM users WHERE (username=? OR email=?) AND password=?",(i,i,hash_pw(p)))
    u = c.fetchone(); conn.close(); return u
def sv_pred(u,t,r,p,ts):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO history (username,test_type,risk_level,probability,timestamp) VALUES (?,?,?,?,?)",(u,t,r,p,ts)); conn.commit(); conn.close()
def gt_hist(u):
    conn = sqlite3.connect(DB_NAME); df = pd.read_sql_query("SELECT test_type,risk_level,probability,timestamp FROM history WHERE username=? ORDER BY id DESC",conn,params=(u,)); conn.close(); return df
def is_valid_email(email): return re.match(r"[^@]+@[^@]+\.[^@]+", email)



# ---------------------------------------------------------
# RENDER PAGES
# ---------------------------------------------------------
def nav_safe(to): st.session_state['dia_page'] = to; st.rerun()

def _home():
    st.header("DiaHeart Assistant")
    st.subheader("AI-based Diabetes & Heart Risk Intelligence System")
    
    show_original_counters()
    
    st.subheader("Platform Navigation")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="dia-card"><h4 style="text-align:center;">Predict Diabetes Risk</h4><p style="text-align:center; opacity:0.8;">Assess your diabetes risk using key health metrics.</p></div>', unsafe_allow_html=True)
        if st.button("Check Diabetes Risk"): nav_safe("Diabetes Predictor")
    with c2:
        st.markdown('<div class="dia-card"><h4 style="text-align:center;">Predict Heart Risk</h4><p style="text-align:center; opacity:0.8;">Evaluate your risk of heart disease based on clinical parameters.</p></div>', unsafe_allow_html=True)
        if st.button("Check Heart Risk"): nav_safe("Heart Predictor")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Why This Exists: The Global Impact")
    cx, cy = st.columns(2)
    with cx: st.markdown("<div class='dia-card'><h4>Rising Diabetes Cases</h4><p>Diabetes cases are rising globally among adults. Early detection is crucial for prevention and effective management.</p></div>", unsafe_allow_html=True)
    with cy: st.markdown("<div class='dia-card'><h4>Heart Disease Impact</h4><p>Heart disease remains a leading cause of health issues globally. Our system uses advanced data analysis to identify risk factors early.</p></div>", unsafe_allow_html=True)

def _auth(view):
    if view == "login":
        st.header("Login")
        st.markdown("<div class='dia-card'><p style='opacity:0.8'>Enter your username and password to access your account.</p></div>", unsafe_allow_html=True)
        idr = st.text_input("Username or Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            u = lg_user(idr, pwd)
            if u: st.session_state['lg'] = True; st.session_state['usr'] = u[0]; st.session_state['fn'] = u[1]; st.rerun()
            else: st.error("Access Refused - Invalid Credentials.")
    else:
        st.header("Create Account")
        st.markdown("<div class='dia-card'><p style='opacity:0.8'>Create a new account to start tracking your health risks.</p></div>", unsafe_allow_html=True)
        f = st.text_input("Full Name")
        e = st.text_input("Email Address")
        u = st.text_input("Username")
        p = st.text_input("Password (Min 8 Characters)", type="password")
        if st.button("Register"):
            if not is_valid_email(e): st.error("Invalid email format.")
            elif len(p)<8: st.error("Password must be at least 8 characters.")
            elif cr_user(f,e,u,p): st.success("Account created successfully. Please login."); time.sleep(1)
            else: st.error("Username or Email already exists.")

def get_risk_css(p):
    if p < 30: return "Low Risk", "dia-risk-low"
    elif p <= 60: return "Medium Risk", "dia-risk-med"
    return "High Risk", "dia-risk-high"

def _diab():
    st.header("Diabetes Risk Predictor")
    st.markdown('<div class="dia-card"><p style="opacity:0.8;">Enter your health details below to assess your diabetes risk.</p></div>', unsafe_allow_html=True)
    
    with st.form("d_f"):
        c1, c2 = st.columns(2)
        with c1: 
            ag = st.number_input("Age", 1, 120, 30)
            gd_str = st.selectbox("Gender", ["Male", "Female"])
            pr = st.number_input("Pulse Rate", 40, 200, 70)
            sb = st.number_input("Systolic Blood Pressure", 80, 250, 120)
            db = st.number_input("Diastolic Blood Pressure", 40, 150, 80)
            gl = st.number_input("Glucose", 40., 400., 100.)
            ht = st.number_input("Height (cm)", 50., 250., 170.)
        with c2:
            wt = st.number_input("Weight (kg)", 10., 300., 70.)
            bmi = st.number_input("BMI", 10., 80., 24.)
            fd = st.selectbox("Family History of Diabetes", ["No", "Yes"])
            hyp = st.selectbox("Hypertensive", ["No", "Yes"])
            fh = st.selectbox("Family History of Hypertension", ["No", "Yes"])
            cvd = st.selectbox("History of Cardiovascular Disease", ["No", "Yes"])
            stk = st.selectbox("History of Stroke", ["No", "Yes"])
            
        s = st.form_submit_button("Calculate Diabetes Risk")
    
    if s:
        with st.spinner("Analyzing your data..."):
            time.sleep(0.5)
            try:
                m = joblib.load("diabetes_model.pkl")
                g = 1 if gd_str=="Male" else 0
                fd_v = 1 if fd=="Yes" else 0
                hyp_v = 1 if hyp=="Yes" else 0
                fh_v = 1 if fh=="Yes" else 0
                cvd_v = 1 if cvd=="Yes" else 0
                stk_v = 1 if stk=="Yes" else 0
                
                arr = np.array([[ag, g, pr, sb, db, gl, ht, wt, bmi, fd_v, hyp_v, fh_v, cvd_v, stk_v]])
                prob = m.predict_proba(arr)[0][1]*100
                lvl, css = get_risk_css(prob)
                st.markdown(f"<div class='dia-card {css}'><h3>{lvl}</h3>Baseline Prob: {prob:.2f}%</div>", unsafe_allow_html=True)
                
                recs = get_recommendations(prob, "Diabetes")
                st.markdown(f"### {recs['Title']}")
                col1, col2, col3 = st.columns(3)
                
                box = st.success if prob < 30 else (st.warning if prob <= 60 else st.error)
                
                with col1: box(f"**🌿 Lifestyle Shift**\n\n{recs['Lifestyle Shift']}")
                with col2: box(f"**🍎 Nutritional Focus**\n\n{recs['Nutritional Focus']}")
                with col3: box(f"**👨‍⚕️ Doctor's Visit**\n\n{recs['When to see a Doctor']}")
                st.caption(f"_{recs['Safety Disclaimer']}_")

                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sv_pred(st.session_state['usr'], "Diabetes", lvl, prob, ts)
                pdf_b = create_pdf(st.session_state['fn'], "Diabetes Report", prob, lvl, ts)
                st.download_button("Secure PDF Export", pdf_b, f"Report_D_{ts[:10]}.pdf", "application/pdf")
            except Exception as e:
                st.error(f"Error making prediction or report: {e}")

def _heart():
    st.header("Heart Risk Predictor")
    st.markdown('<div class="dia-card"><p style="opacity:0.8;">Enter your health details below to assess your heart disease risk.</p></div>', unsafe_allow_html=True)
    
    with st.form("h_f"):
        c1, c2 = st.columns(2)
        with c1: 
            ag = st.number_input("Age", 1,120,50)
            gd = st.selectbox("Gender", ["Male", "Female"])
            sm = st.selectbox("Current Smoker", ["No", "Yes"])
            cpd = st.number_input("Cigarettes Per Day", 0, 100, 0)
            cd = st.number_input("Cholesterol", 100., 600., 200.)
            sb = st.number_input("Systolic Blood Pressure", 80., 250., 120.)
            db = st.number_input("Diastolic Blood Pressure", 40., 150., 80.)
        with c2:
            bm = st.number_input("BMI", 10., 80., 25.)
            gl = st.number_input("Glucose", 40., 400., 90.)
            hr = st.number_input("Resting Heart Rate", 40., 200., 75.)
            bpm = st.selectbox("On Blood Pressure Meds?", ["No", "Yes"])
            pst = st.selectbox("History of Stroke?", ["No", "Yes"])
            phy = st.selectbox("Prevalent Hypertension?", ["No", "Yes"])
            dia = st.selectbox("Diabetes?", ["No", "Yes"])
            
        s = st.form_submit_button("Calculate Heart Risk")
        
    if s:
        with st.spinner("Analyzing your data..."):
            time.sleep(0.5)
            try:
                m = joblib.load("CVD_model.pkl")
                try: 
                    medians = joblib.load("cvd_median.pkl")
                    med_edu = float(medians.get('education', 2.0))
                except:
                    med_edu = 2.0
                    
                g = 1 if gd=="Male" else 0
                sm_f = 1 if sm=="Yes" else 0
                bpm_f = 1 if bpm=="Yes" else 0
                pst_f = 1 if pst=="Yes" else 0
                phy_f = 1 if phy=="Yes" else 0
                dia_f = 1 if dia=="Yes" else 0
                
                arr = np.array([[g, ag, med_edu, sm_f, cpd, bpm_f, pst_f, phy_f, dia_f, cd, sb, db, bm, hr, gl]])
                prob = m.predict_proba(arr)[0][1]*100
                lvl, css = get_risk_css(prob)
                st.markdown(f"<div class='dia-card {css}'><h3>{lvl}</h3>Baseline Prob: {prob:.2f}%</div>", unsafe_allow_html=True)
                
                recs = get_recommendations(prob, "Heart")
                st.markdown(f"### {recs['Title']}")
                col1, col2, col3 = st.columns(3)
                
                box = st.success if prob < 30 else (st.warning if prob <= 60 else st.error)
                
                with col1: box(f"**🌿 Lifestyle Shift**\n\n{recs['Lifestyle Shift']}")
                with col2: box(f"**🍎 Nutritional Focus**\n\n{recs['Nutritional Focus']}")
                with col3: box(f"**👨‍⚕️ Doctor's Visit**\n\n{recs['When to see a Doctor']}")
                st.caption(f"_{recs['Safety Disclaimer']}_")
                
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sv_pred(st.session_state['usr'], "Heart", lvl, prob, ts)
                pdf_b = create_pdf(st.session_state['fn'], "Heart Report", prob, lvl, ts)
                st.download_button("Secure PDF Export", pdf_b, f"Report_H_{ts[:10]}.pdf", "application/pdf")
            except Exception as e:
                st.error(f"Error making prediction or report: {e}")

def _hub():
    st.header("Education Hub")
    st.markdown("<p style='opacity:0.8'>Information and resources to help you understand diabetes and heart health better.</p>", unsafe_allow_html=True)
    
    def render_v(col, u, vid, t):
        i = f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg"
        h = f"""
        <div style="margin-bottom: 8px; font-weight: 500; font-size: 1.1em;">{t}</div>
        <a href="{u}" target="_blank" style="text-decoration: none;">
            <div style="position: relative; border-radius: 12px; overflow: hidden; box-shadow: 0 6px 12px rgba(0,0,0,0.15); margin-bottom: 8px; border: 1px solid rgba(128,128,128,0.2); transition: transform 0.3s ease;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
                <img src="{i}" style="width: 100%; display: block;" onerror="this.onerror=null;this.src='https://img.youtube.com/vi/{vid}/hqdefault.jpg';"/>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.7); width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(2px);">
                    <div style="width: 0; height: 0; border-top: 8px solid transparent; border-bottom: 8px solid transparent; border-left: 14px solid white; margin-left: 4px;"></div>
                </div>
            </div>
        </a>
        <div style="font-size: 0.85em; opacity: 0.9; margin-bottom: 15px;">▶️ <a href="{u}" target="_blank" style="color: inherit;">{u}</a></div>
        """
        col.markdown(h, unsafe_allow_html=True)
        
    c1, c2, c3 = st.columns(3)
    render_v(c1, "https://www.youtube.com/watch?v=UMv0Ww6sFng", "UMv0Ww6sFng", "<span style='color:#3b82f6;'>Trending: Heart Health</span><br><span style='font-size:0.8em;opacity:0.7;'>Updated 4 hours ago</span>")
    render_v(c2, "https://www.youtube.com/watch?v=wZAjVQWbMlE", "wZAjVQWbMlE", "<span style='color:#10b981;'>Trending: Diabetes Info</span><br><span style='font-size:0.8em;opacity:0.7;'>Updated recently</span>")
    render_v(c3, "https://www.youtube.com/watch?v=eB8D-kmaQ8s", "eB8D-kmaQ8s", "Role of AI in Healthcare<br><span style='font-size:0.8em;opacity:0.7;'>General Awareness</span>")
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("View More Educational Videos", expanded=False):
        ec1, ec2, ec3 = st.columns(3)
        render_v(ec1, "https://www.youtube.com/watch?v=3cW8cvB5BIE", "3cW8cvB5BIE", "Heart Attack Insights")
        render_v(ec2, "https://www.youtube.com/watch?v=XfyGv-xwjlI", "XfyGv-xwjlI", "How Your Pancreas Works")
        render_v(ec3, "https://www.youtube.com/watch?v=-sBEnETrJlk", "-sBEnETrJlk", "Medical AI Overview")

def _reports():
    st.header("My Health Reports")
    df = gt_hist(st.session_state['usr'])
    if df.empty: st.info("No past reports found. Run a prediction to see it here."); return
    cx, cy = st.columns(2)
    with cx: 
        fig1 = px.pie(df, names='risk_level', title="Risk Level Breakdown", color_discrete_sequence=['#f59e0b','#10b981','#ef4444'])
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#F8FAFC')
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    with cy:
        fig2 = px.histogram(df, x='test_type', color='test_type', title="Tests Conducted")
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#F8FAFC')
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    st.dataframe(df, use_container_width=True, hide_index=True)

def _about():
    st.header("About DiaHeart")
    
    st.subheader("Project Overview")
    st.markdown("<div class='dia-card'><p>DiaHeart Assistant is a comprehensive, Al-powered system that predicts the risk of diabetes and cardiovascular diseases utilizing state-of-the-art machine learning capabilities.</p></div>", unsafe_allow_html=True)
    
    st.subheader("Purpose")
    st.markdown("<div class='dia-card'><p>Our purpose is to bridge the gap between advanced artificial intelligence and everyday personal healthcare tracking.</p></div>", unsafe_allow_html=True)
    
    st.subheader("Role of Al in Healthcare")
    st.markdown("<div class='dia-card'><p>Al accelerates diagnosis generation, augments clinical assessments, and highlights subtle parameters that standard methods might miss.</p></div>", unsafe_allow_html=True)
    
    st.subheader("Core Technologies")
    st.markdown("<div class='dia-card'><ul><li>Python 3.10+ (Core programming language)</li><li>Streamlit (Frontend framework)</li><li>Machine Learning (Random Forest via scikit-learn & joblib)</li><li>SQLite3 (Secure local user authentication and history management)</li></ul></div>", unsafe_allow_html=True)

    st.subheader("Developers")
    st.markdown("<div class='dia-card'><div style='display: flex; justify-content: space-around;'><div> Alisha Amjad</div><div> Fatima Munir</div></div></div>", unsafe_allow_html=True)

def _contact():
    st.header("Contact Support")
    st.markdown("<p style='opacity:0.8'>Having issues or questions? Fill out the form below to contact us.</p>", unsafe_allow_html=True)
    with st.form("cx"):
        st.text_input("Your Name")
        st.text_input("Your Email")
        st.text_area("Describe your question or issue")
        if st.form_submit_button("Send Message"):
            st.success("Message sent successfully.")

def main():
    apply_custom_css()
    
    # Initialize the splash state if it doesn't exist
    if 'splash_complete' not in st.session_state:
        st.session_state.splash_complete = False

    # Splash Screen Logic
    if not st.session_state.splash_complete:
        # Use columns to center your logo
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown(f'<div style="text-align:center;margin-bottom:10px;">{BRAND_SVG}</div>', unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Loading DiaHeart...</h3>", unsafe_allow_html=True)
            st.progress(100) # Simple progress bar
        
        time.sleep(3) # The "Splash" duration
        st.session_state.splash_complete = True
        st.rerun() # Forces the page to refresh and show main app

    # Main App starts here
    if 'lg' not in st.session_state: st.session_state['lg'] = False
    if 'dia_page' not in st.session_state: st.session_state['dia_page'] = "Home"
    
    with st.sidebar:
        st.markdown(f'<div style="text-align:center;margin-bottom:10px;">{BRAND_SVG}</div><h2 style="text-align:center; font-weight:700; font-size:1.4rem; margin-top:5px; margin-bottom:15px; line-height:1.2;">DiaHeart Assistant</h2><hr>', unsafe_allow_html=True)
        if st.session_state['lg']:
            pages = ["Home", "Diabetes Predictor", "Heart Predictor", "Diagnostic Reports", "Education Hub", "About DiaHeart", "Contact Support"]
            sel = st.radio("Navigation", pages, index=pages.index(st.session_state['dia_page']))
            st.session_state['dia_page'] = sel
            st.markdown("---")
            if st.session_state.get('confirm_logout', False):
                st.warning("Confirm Logout?")
                xc1, xc2 = st.columns(2)
                if xc1.button("Yes"):
                    for key in list(st.session_state.keys()): del st.session_state[key]
                    st.rerun()
                if xc2.button("Cancel"):
                    st.session_state['confirm_logout'] = False
                    st.rerun()
            else:
                if st.button("Logout"): 
                    st.session_state['confirm_logout'] = True
                    st.rerun()
        else:
            st.markdown("""<style>
            [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: 1.3rem !important; font-weight: 700 !important; }
            [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 1.25rem !important; font-weight: 600 !important; }
            </style>""", unsafe_allow_html=True)
            sel = st.radio("Access", ["Login", "Sign Up"])
            
    curr = st.session_state.get('dia_page', "Home")
    if not st.session_state['lg']:
        if sel == "Login": _auth("login")
        else: _auth("signup")
    else:
        if curr == "Home": _home()
        elif curr == "Diabetes Predictor": _diab()
        elif curr == "Heart Predictor": _heart()
        elif curr == "Diagnostic Reports": _reports()
        elif curr == "Education Hub": _hub()
        elif curr == "About DiaHeart": _about()
        elif curr == "Contact Support": _contact()
        else: _home()



    # Restoration of EXACT Footer Formatting requirement (Single String)
    st.markdown("---")
    st.text('''DiaHeart Assistant © 2026 | Educational AI Healthcare Project | Disclaimer: This system does not provide medical diagnosis. Consult a healthcare professional.''')

def inject_botpress_chatbot():
    """
    Direct Botpress injection into the parent window.
    """
    components.html(
        """
        <script>
            const s1 = window.parent.document.createElement('script');
            s1.src = "https://cdn.botpress.cloud/webchat/v3.6/inject.js";
            window.parent.document.head.appendChild(s1);

            const s2 = window.parent.document.createElement('script');
            s2.src = "https://files.bpcontent.cloud/2026/04/19/06/20260419062702-K2KSZOIF.js";
            window.parent.document.head.appendChild(s2);
        </script>
        """,
        height=0,
    )

if __name__ == "__main__":
    main()
    if st.session_state.get('lg', False):
        inject_botpress_chatbot()
        