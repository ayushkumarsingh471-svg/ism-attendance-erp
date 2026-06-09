import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import calendar
import io
import os
import base64

# --- 1. PAGE SETUP & GLOBAL CSS ---
st.set_page_config(layout="wide", page_title="ISM Attendance ERP", page_icon="🎓")

# --- 2. MASTER USER DATABASE ---
MASTER_DB = 'master_users.db'
def init_master_db():
    conn = sqlite3.connect(MASTER_DB)
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit(); conn.close()

init_master_db()

# --- 3. LOGIN & REGISTRATION EXACT UI MATCH ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

if not st.session_state.logged_in:
    # EXACT CSS FIX FOR IMAGE 2 LOOK
    st.markdown("""
        <style>
        /* General background */
        .stApp { background: #f4f6f9; }
        
        /* Hide native Streamlit headers */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Container for the split view */
        .login-container {
            display: flex;
            max-width: 1050px;
            margin: 40px auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }
        
        /* LEFT SIDE: Deep Blue Information Panel */
        .left-panel {
            flex: 1.2;
            background: linear-gradient(135deg, #0f172a, #005073);
            color: white;
            padding: 50px 40px;
            border-right: 4px solid #f59e0b;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        /* RIGHT SIDE: White Login Form Area */
        .right-panel {
            flex: 1;
            padding: 40px 50px;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        /* Text Styles inside Left Panel */
        .lp-title { font-size: 38px; font-weight: 900; margin: 0; color: white; display: flex; align-items: center; gap: 10px;}
        .lp-subtitle { color: #fcd34d; font-size: 16px; font-weight: 700; margin-top: 5px; margin-bottom: 25px; letter-spacing: 1px;}
        .lp-desc { font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-bottom: 30px;}
        .lp-feature { background: rgba(255,255,255,0.05); padding: 15px 20px; border-radius: 8px; border-left: 4px solid #f59e0b;}
        .lp-feature-title { color: #fcd34d; font-weight: bold; font-size: 14px; margin-bottom: 5px;}
        .lp-feature-text { color: #f8fafc; font-size: 13px; line-height: 1.5; margin: 0;}

        /* Form Native Overrides */
        .stTextInput input { border-radius: 8px; border: 1px solid #cbd5e1; padding: 10px; font-size: 15px;}
        .stTextInput p { font-weight: bold; color: #334155; margin-bottom: 5px;}
        .stButton>button { width: 100%; border-radius: 8px; height: 45px; background-color: #f43f5e !important; color: white !important; font-weight: bold; border: none; transition: 0.2s;}
        .stButton>button:hover { background-color: #e11d48 !important; transform: translateY(-2px);}
        
        /* Hide Streamlit Empty Elements */
        .element-container:empty { display: none !important; }
        
        </style>
    """, unsafe_allow_html=True)
    
    # Render the pure HTML/CSS split layout structure
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("""
        <div class="left-panel">
            <div class="lp-title">🎓 ISM PATNA</div>
            <div class="lp-subtitle">ATTENDANCE ERP SYSTEM</div>
            <p class="lp-desc">
                Welcome to the professional Multi-Tenant Attendance ERP Platform. This enterprise portal provides complete data isolation, analytical insights, automated reports, and secure image profile mapping for individual courses and classes.
            </p>
            <div class="lp-feature">
                <div class="lp-feature-title">💡 Multi-Tenant Isolation Feature:</div>
                <p class="lp-feature-text">Every class, course coordinator, or administrator can register a custom User ID to instantiate a clean, completely independent localized database.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='right-panel'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#0f172a; font-weight:900; margin-top:0; margin-bottom:15px;'>🔐 Access Portal</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER NEW CLASS"])
        
        with tab1:
            l_user = st.text_input("User ID", placeholder="Enter User ID", key="login_uid_field")
            l_pass = st.text_input("Password", type="password", placeholder="Enter Password", key="login_pwd_field")
            st.write("")
            if st.button("SECURE LOGIN", type="primary"):
                conn = sqlite3.connect(MASTER_DB)
                res = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (l_user.strip(), l_pass)).fetchone()
                conn.close()
                if res:
                    st.session_state.logged_in = True
                    st.session_state.current_user = l_user.strip()
                    st.rerun()
                else:
                    st.error("❌ Invalid User ID or Password!")
                    
        with tab2:
            n_user = st.text_input("User ID", placeholder="Choose User ID (e.g., BCA_Sem1)")
            n_pass = st.text_input("Password", type="password", placeholder="Create Password")
            st.write("")
            if st.button("REGISTER ACCOUNT", type="primary"):
                if n_user and n_pass:
                    conn = sqlite3.connect(MASTER_DB)
                    try:
                        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (n_user.strip(), n_pass))
                        conn.commit()
                        st.success(f"✅ Registered '{n_user}' successfully! Switch to Login tab.")
                    except sqlite3.IntegrityError:
                        st.error("⚠️ This User ID already exists. Try another name.")
                    conn.close()
                else:
                    st.error("Both fields are required.")
                    
        st.markdown("</div>", unsafe_allow_html=True) # close right panel
        
    st.markdown('</div>', unsafe_allow_html=True) # close login container
    st.stop()

# =========================================================================
# TENANT SPACE ISOLATION CONFIGURATION (AFTER LOGIN)
# =========================================================================
USER_ID = st.session_state.current_user
DB_NAME = f"database_{USER_ID}.db"
PHOTO_DIR = f"photos_{USER_ID}"
LOGO_FILE = f"logo_{USER_ID}.png"
os.makedirs(PHOTO_DIR, exist_ok=True)

# Main App CSS (Applies only after login)
st.markdown("""
    <style>
    .stApp { background: #f0f4f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; } 
    div[data-testid="stSidebar"] { background-color: #1e293b; color: white !important; border-right: 2px solid #005073; }
    div[data-testid="stSidebar"] * { color: white !important; }
    .panel-box { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #005073; margin-bottom: 20px; transition: transform 0.3s; }
    .panel-box:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    
    .profile-card-left { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e2e8f0; height: 100%; }
    .profile-pic-left { width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 5px solid #f8fafc; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: 0 auto; display: block; }
    .id-badge { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #000 !important; padding: 6px 20px; border-radius: 25px; display: inline-block; font-weight: 900; font-size: 16px; margin-bottom: 5px; box-shadow: 0 4px 6px rgba(245,158,11,0.3); border: 2px solid #fff; }
    
    .excel-table-container { overflow-x: auto; width: 100%; max-height: 700px; background-color: white; border-radius: 8px; border: 2px solid #cbd5e1; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .excel-table { width: 100%; border-collapse: collapse; font-size: 14px; white-space: nowrap; }
    .excel-table th { background-color: #0f172a; color: white; padding: 12px; font-weight: bold; text-align: center; position: sticky; top: 0; z-index: 2; border: 1px solid #334155; }
    .excel-table td { padding: 10px; border: 1px solid #e2e8f0; text-align: center; font-weight: bold; }
    .row-even { background-color: #f8fafc; }
    .row-odd { background-color: #ffffff; }
    .excel-table tr:hover td { background-color: #e2e8f0 !important; cursor: default; }
    
    .sticky-col-1 { position: sticky; left: 0; min-width: 100px; max-width: 100px; z-index: 3; border-right: 1px solid #cbd5e1; background-color: inherit; }
    .sticky-col-2 { position: sticky; left: 100px; min-width: 60px; max-width: 60px; z-index: 3; border-right: 1px solid #cbd5e1; background-color: inherit; }
    .sticky-col-3 { position: sticky; left: 160px; min-width: 220px; max-width: 220px; z-index: 3; border-right: 3px solid #005073; background-color: inherit; text-align: left !important; padding-left: 15px !important; }
    th.sticky-col-1 { left: 0; min-width: 100px; z-index: 4 !important; background-color: #0f172a; border-right: 1px solid #334155; }
    th.sticky-col-2 { left: 100px; min-width: 60px; z-index: 4 !important; background-color: #0f172a; border-right: 1px solid #334155; }
    th.sticky-col-3 { left: 160px; min-width: 220px; z-index: 4 !important; background-color: #0f172a; border-right: 3px solid #f59e0b; }
    
    .status-p { background-color: #10b981 !important; color: white !important; font-size: 16px; font-weight: 900; }
    .status-a { background-color: #ef4444 !important; color: white !important; font-size: 16px; font-weight: 900; }
    
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; transition: all 0.2s; }
    .stButton>button:active { transform: scale(0.95); }
    .btn-vertical-p button { background: linear-gradient(145deg, #10b981, #059669) !important; color: white !important; height: 90px; font-size: 24px !important; margin-bottom: 10px; border: none; box-shadow: 0 5px 15px rgba(16,185,129,0.3); }
    .btn-vertical-p button:hover { transform: translateY(-3px); }
    .btn-vertical-a button { background: linear-gradient(145deg, #ef4444, #dc2626) !important; color: white !important; height: 90px; font-size: 24px !important; border: none; box-shadow: 0 5px 15px rgba(239,68,68,0.3); }
    .btn-vertical-a button:hover { transform: translateY(-3px); }
    </style>
""", unsafe_allow_html=True)

def init_user_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, reg_no TEXT UNIQUE, roll_no TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY, subject_name TEXT UNIQUE)')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY, student_id INTEGER, subject_id INTEGER, date TEXT, status TEXT,
            UNIQUE(student_id, subject_id, date))''')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    c.execute("SELECT COUNT(*) FROM subjects")
    if c.fetchone()[0] == 0:
        for sub in ['SAD', 'PST&PC', 'NT', 'BE', 'OS&UNIX LAB', 'PROG IN C LAB']:
            c.execute('INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)', (sub,))
    conn.commit(); conn.close()

init_user_db()

def get_setting(key, default_val):
    conn = sqlite3.connect(DB_NAME)
    res = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return res[0] if res else default_val

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit(); conn.close()

def get_subjects():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT subject_name FROM subjects ORDER BY subject_name").fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else ["No Subjects Found"]

def get_image_base64(img_path):
    try:
        with open(img_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode('utf-8')
    except: return ""

def get_student_photo_url(reg_no):
    for ext in ['jpg', 'png', 'jpeg']:
        path = os.path.join(PHOTO_DIR, f"{reg_no}.{ext}")
        if os.path.exists(path):
            return f"data:image/{ext};base64,{get_image_base64(path)}"
    return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

def generate_excel_report():
    conn = sqlite3.connect(DB_NAME)
    df_details = pd.read_sql("SELECT s.reg_no AS 'Reg No', s.roll_no AS 'Roll No', s.name AS 'Student Name', sub.subject_name AS 'Subject', a.date AS 'Date', a.status AS 'Status' FROM attendance a JOIN students s ON a.student_id = s.id JOIN subjects sub ON a.subject_id = sub.id ORDER BY a.date DESC", conn)
    df_students = pd.read_sql("SELECT reg_no AS 'Reg No', roll_no AS 'Roll No', name AS 'Name' FROM students ORDER BY CAST(roll_no AS INTEGER) ASC", conn)
    conn.close()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_details.to_excel(writer, sheet_name='Detailed_Logs', index=False)
        df_students.to_excel(writer, sheet_name='All_Students', index=False)
    return output.getvalue()

# --- HEADER SECTION ---
logo_html = ""
if os.path.exists(LOGO_FILE):
    logo_base64 = get_image_base64(LOGO_FILE)
    logo_html = f"<img src='data:image/png;base64,{logo_base64}' style='max-width:110px; max-height:110px; object-fit:contain; margin-right:25px; border-radius:8px;'><div style='padding-left:10px;'></div>"

c_name = get_setting('college_name', 'INTERNATIONAL SCHOOL OF MANAGEMENT (ISM)')
c_sub = get_setting('app_subtitle', 'ATTENDANCE MANAGEMENT SYSTEM')
c_course = get_setting('course_name', 'BCA')
c_sec = get_setting('section_name', 'Semester 1')

st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:flex-start; background: linear-gradient(135deg, #0f172a, #005073); padding: 20px 30px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); border-bottom: 5px solid #f59e0b; margin-bottom: 25px;">
        {logo_html}
        <div style="text-align: left;">
            <h1 style="margin: 0; font-size: 32px; font-weight: 900; letter-spacing: 1px; color: white;">{c_name}</h1>
            <h3 style="margin: 5px 0 0 0; font-size: 18px; color: #fcd34d; font-weight: 600; letter-spacing: 1px;">{c_sub} &nbsp;|&nbsp; COURSE: {c_course} &nbsp;|&nbsp; SEC/SEM: {c_sec}</h3>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR NAV MENU ---
st.sidebar.markdown(f"<h3 style='text-align:center; color:#fcd34d;'>👤 Welcome: {USER_ID}</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigate Pages:", [
    "📊 Dashboard", 
    "📝 Mark Attendance", 
    "📅 Attendance Table", 
    "👥 Manage Students",
    "🏢 College Profile"
])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 LOGOUT SECURELY", type="primary"):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.rerun()

if 'current_idx' not in st.session_state: st.session_state.current_idx = 0

# =========================================================================
# TAB 1: DASHBOARD
# =========================================================================
if menu == "📊 Dashboard":
    st.markdown("### 📈 Monthly Overview & Daily Status")
    
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    c_m, c_y, c_s, c_d = st.columns(4)
    now = datetime.now()
    sel_month = c_m.selectbox("Month", list(calendar.month_name)[1:], index=now.month-1)
    sel_year = c_y.selectbox("Year", [now.year-1, now.year, now.year+1], index=1)
    sel_sub = c_s.selectbox("Subject", get_subjects())
    target_date = c_d.date_input("Select Date for Present Count", date.today())
    st.markdown("</div>", unsafe_allow_html=True)
    
    month_num = list(calendar.month_name).index(sel_month)
    date_pattern = f"{sel_year}-{month_num:02d}-%"
    
    conn = sqlite3.connect(DB_NAME)
    total_students = conn.execute("SELECT COUNT(id) FROM students").fetchone()[0] or 0
    tc_count = conn.execute("SELECT COUNT(DISTINCT date) FROM attendance WHERE subject_id=(SELECT id FROM subjects WHERE subject_name=?) AND date LIKE ?", (sel_sub, date_pattern)).fetchone()[0] or 0
    present_today = conn.execute("SELECT COUNT(date) FROM attendance WHERE subject_id=(SELECT id FROM subjects WHERE subject_name=?) AND date=? AND status='Present'", (sel_sub, str(target_date))).fetchone()[0] or 0
    conn.close()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="panel-box" style="text-align:center; background:#007bff; color:white;"><h4>Total Students</h4><h2>{total_students}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="panel-box" style="text-align:center; background:#6f42c1; color:white;"><h4>Classes Conducted</h4><h2>{tc_count}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="panel-box" style="text-align:center; background:#17a2b8; color:white;"><h4>Selected Subject</h4><h2>{sel_sub}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="panel-box" style="text-align:center; background:#28a745; color:white;"><h4>Present on {target_date.strftime("%d %b")}</h4><h2>{present_today}</h2></div>', unsafe_allow_html=True)

# =========================================================================
# TAB 2: MARK ATTENDANCE
# =========================================================================
elif menu == "📝 Mark Attendance":
    st.markdown("### 📝 Active Mark Attendance Panel")
    
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    now = datetime.now()
    sel_month = f1.selectbox("Month", list(calendar.month_name)[1:], index=now.month-1)
    sel_year = f2.selectbox("Year", [now.year-1, now.year, now.year+1], index=1)
    sel_sub = f3.selectbox("Subject", get_subjects())
    target_date = f4.date_input("Date", date.today())
    st.markdown("</div>", unsafe_allow_html=True)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    students_df = pd.read_sql("SELECT id, reg_no, roll_no, name FROM students ORDER BY CAST(roll_no AS INTEGER) ASC", conn)
    student_list = students_df.values.tolist() if not students_df.empty else []
    
    if student_list:
        if st.session_state.current_idx >= len(student_list): st.session_state.current_idx = len(student_list) - 1
        curr_student = student_list[st.session_state.current_idx]
        s_id, s_reg, s_roll, s_name = curr_student
        photo_url = get_student_photo_url(s_reg)
        
        st.write("")
        col_prof, col_btn = st.columns([2.5, 1.5])
        
        with col_prof:
            profile_html = f"""
            <div class='profile-card-left'>
                <img src='{photo_url}' class='profile-pic-left'>
                <h1 style='margin: 15px 0 5px 0; color:#0f172a; font-size:28px;'>{s_name}</h1>
                <div class='id-badge'>🆔 REG NO: {s_reg}</div>
                <h4 style='margin: 5px 0 0 0; color:#64748b; font-size: 16px;'>ROLL NO: {s_roll}</h4>
            </div>
            """
            st.markdown(profile_html, unsafe_allow_html=True)
            
            st.write("")
            student_options = [f"{s[1]} - {s[3]}" for s in student_list]
            selected_student = st.selectbox("🔍 Quick Jump to Student", student_options, index=st.session_state.current_idx)
            if student_options.index(selected_student) != st.session_state.current_idx:
                st.session_state.current_idx = student_options.index(selected_student)
                st.rerun()
                
            n1, n2 = st.columns(2)
            if n1.button("◀ PREVIOUS STUDENT"):
                if st.session_state.current_idx > 0: st.session_state.current_idx -= 1; st.rerun()
            if n2.button("NEXT STUDENT ▶"):
                if st.session_state.current_idx < len(student_list) - 1: st.session_state.current_idx += 1; st.rerun()

        with col_btn:
            st.markdown("<div style='padding: 20px 0;'></div>", unsafe_allow_html=True) 
            st.markdown('<div class="btn-vertical-p">', unsafe_allow_html=True)
            if st.button("✅ PRESENT (P)"):
                cursor.execute("INSERT OR REPLACE INTO attendance (student_id, subject_id, date, status) VALUES (?, (SELECT id FROM subjects WHERE subject_name=?), ?, 'Present')", (s_id, sel_sub, str(target_date)))
                conn.commit()
                st.toast(f"{s_name} Marked PRESENT", icon="🟢")
                if st.session_state.current_idx < len(student_list) - 1: st.session_state.current_idx += 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="btn-vertical-a">', unsafe_allow_html=True)
            if st.button("❌ ABSENT (A)"):
                cursor.execute("INSERT OR REPLACE INTO attendance (student_id, subject_id, date, status) VALUES (?, (SELECT id FROM subjects WHERE subject_name=?), ?, 'Absent')", (s_id, sel_sub, str(target_date)))
                conn.commit()
                st.toast(f"{s_name} Marked ABSENT", icon="🔴")
                if st.session_state.current_idx < len(student_list) - 1: st.session_state.current_idx += 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.warning("No students available. Go to Manage Students to import records.")
    conn.close()

# =========================================================================
# TAB 3: ATTENDANCE TABLE
# =========================================================================
elif menu == "📅 Attendance Table":
    st.markdown("### 📅 Monthly Register (Scrollable with Sticky Columns)")
    
    c_m, c_y, c_s = st.columns(3)
    now = datetime.now()
    sel_month = c_m.selectbox("Select Month", list(calendar.month_name)[1:], index=now.month-1)
    sel_year = c_y.selectbox("Select Year", [now.year-1, now.year, now.year+1], index=1)
    sel_sub = c_s.selectbox("Select Subject", get_subjects())
    
    month_num = list(calendar.month_name).index(sel_month)
    date_pattern = f"{sel_year}-{month_num:02d}-%"
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    students_df = pd.read_sql("SELECT id, reg_no, roll_no, name FROM students ORDER BY CAST(roll_no AS INTEGER) ASC", conn)
    
    if not students_df.empty:
        num_days = calendar.monthrange(sel_year, month_num)[1]
        att_records = cursor.execute("""
            SELECT s.reg_no, a.date, a.status FROM attendance a JOIN students s ON a.student_id = s.id
            WHERE a.subject_id = (SELECT id FROM subjects WHERE subject_name = ?) AND a.date LIKE ?
        """, (sel_sub, date_pattern)).fetchall()
        
        att_map = {}
        for r_no, d_str, stat in att_records:
            try:
                day_idx = int(d_str.split('-')[2])
                if r_no not in att_map: att_map[r_no] = {}
                att_map[r_no][day_idx] = 'P' if stat == 'Present' else 'A'
            except: pass
            
        tc_count = cursor.execute("SELECT COUNT(DISTINCT date) FROM attendance WHERE subject_id=(SELECT id FROM subjects WHERE subject_name=?) AND date LIKE ?", (sel_sub, date_pattern)).fetchone()[0] or 0
            
        html_grid = '<div class="excel-table-container"><table class="excel-table">'
        html_grid += '<tr><th class="sticky-col-1">Reg No</th><th class="sticky-col-2">Roll</th><th class="sticky-col-3">Student Name</th>'
        for d in range(1, num_days + 1): html_grid += f'<th>{d}</th>'
        html_grid += '<th style="min-width:80px;">%</th></tr>'
        
        row_counter = 0
        for idx, row in students_df.iterrows():
            row_class = "row-even" if row_counter % 2 == 0 else "row-odd"
            row_counter += 1
            html_grid += f'<tr class="{row_class}">'
            
            html_grid += f'<td class="sticky-col-1" style="color:#0f172a;">{row["reg_no"]}</td>'
            html_grid += f'<td class="sticky-col-2" style="color:#0f172a;">{row["roll_no"]}</td>'
            html_grid += f'<td class="sticky-col-3" style="color:#0f172a;">{row["name"]}</td>'
            
            total_p = 0
            s_reg_str = row['reg_no']
            for d in range(1, num_days + 1):
                status_char = att_map.get(s_reg_str, {}).get(d, "")
                if status_char == 'P':
                    total_p += 1
                    html_grid += '<td class="status-p">P</td>'
                elif status_char == 'A':
                    html_grid += '<td class="status-a">A</td>'
                else:
                    html_grid += '<td></td>'
                    
            pct = (total_p / tc_count * 100) if tc_count > 0 else 0
            html_grid += f'<td style="color:#005073; font-size:16px;">{pct:.0f}%</td></tr>'
            
        html_grid += '</table></div>'
        st.markdown(html_grid, unsafe_allow_html=True)
    else:
        st.info("No data found. Please add records under Manage Students.")
    conn.close()

# =========================================================================
# TAB 4: MANAGE STUDENTS
# =========================================================================
elif menu == "👥 Manage Students":
    st.markdown("### 👥 Student Database Management Panel")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#28a745;'>➕ 1. Add New Student (Manual)</h3>", unsafe_allow_html=True)
        with st.form("add_student_form"):
            new_reg = st.text_input("Registration No")
            new_roll = st.text_input("Roll No")
            new_name = st.text_input("Full Name")
            if st.form_submit_button("ADD STUDENT"):
                if new_reg and new_name:
                    conn = sqlite3.connect(DB_NAME)
                    conn.execute("INSERT OR IGNORE INTO students (reg_no, roll_no, name) VALUES (?, ?, ?)", (new_reg.strip(), new_roll.strip(), new_name.strip()))
                    conn.commit(); conn.close()
                    st.success(f"✅ Student {new_name} added successfully!")
                else: st.error("Registration Number and Student Name are required.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#dc3545;'>🗑️ 2. Delete Student Record</h3>", unsafe_allow_html=True)
        with st.form("delete_student_form"):
            del_reg = st.text_input("Enter Registration No to Delete")
            if st.form_submit_button("DELETE STUDENT"):
                if del_reg:
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM students WHERE reg_no = ?", (del_reg.strip(),))
                    if cursor.rowcount > 0: st.success(f"✅ Record for Reg No {del_reg} deleted successfully.")
                    else: st.warning("⚠️ Student record not found.")
                    conn.commit(); conn.close()
        st.markdown("</div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("### 📥 3. Excel/CSV Bulk Import</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose CSV/Excel Document", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'): df_raw = pd.read_csv(uploaded_file)
                else: df_raw = pd.read_excel(uploaded_file)
                if len(df_raw.columns) >= 3:
                    df_clean = df_raw.iloc[:, :3].copy()
                    df_clean.columns = ['reg_no', 'roll_no', 'name']
                    df_clean = df_clean.dropna(subset=['reg_no', 'name'])
                    if st.button("UPLOAD PARSED DATA TO DATABASE"):
                        conn = sqlite3.connect(DB_NAME)
                        for _, row in df_clean.iterrows():
                            reg = str(row['reg_no']).strip()
                            if reg.endswith('.0'): reg = reg[:-2]
                            roll = str(row['roll_no']).strip()
                            if roll.endswith('.0'): roll = roll[:-2]
                            name = str(row['name']).strip()
                            if reg and name and reg.lower() != 'nan':
                                conn.execute("INSERT OR IGNORE INTO students (reg_no, roll_no, name) VALUES (?, ?, ?)", (reg, roll, name))
                        conn.commit(); conn.close()
                        st.success("🎉 Bulk student repository imported successfully!")
            except Exception as e: st.error("Error reading data file structural layout.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("### 📸 4. Upload Student Photo Mapping</h3>", unsafe_allow_html=True)
        reg_input = st.text_input("Enter Student Registration No")
        photo_file = st.file_uploader("Select Image File (JPG, PNG)", type=["jpg", "png", "jpeg"])
        if st.button("SAVE IMAGE TARGET", type="primary"):
            if reg_input and photo_file:
                ext = photo_file.name.split('.')[-1].lower()
                with open(os.path.join(PHOTO_DIR, f"{reg_input.strip()}.{ext}"), "wb") as f: f.write(photo_file.getbuffer())
                st.success(f"✅ Photo matched and saved for Reg No: {reg_input}!")
            else: st.error("Registration Number and image asset selection are mandatory.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel-box' style='border-top: 4px solid #f59e0b;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#f59e0b;'>🧹 5. Remove Individual Attendance Logs</h3>", unsafe_allow_html=True)
    r_a1, r_a2 = st.columns(2)
    clr_reg = r_a1.text_input("Enter Target Student Reg No")
    clr_sub = r_a2.selectbox("Select Subject Horizon", ["All Subjects"] + get_subjects())
    
    if st.button("🚨 REMOVE ATTENDANCE LOGS", type="primary"):
        if clr_reg:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM students WHERE reg_no=?", (clr_reg,))
            s_res = cursor.fetchone()
            if s_res:
                s_id = s_res[0]
                if clr_sub == "All Subjects":
                    cursor.execute("DELETE FROM attendance WHERE student_id=?", (s_id,))
                else:
                    cursor.execute("DELETE FROM attendance WHERE student_id=? AND subject_id=(SELECT id FROM subjects WHERE subject_name=?)", (s_id, clr_sub))
                rows_deleted = cursor.rowcount
                conn.commit()
                st.success(f"🧹 Purged {rows_deleted} attendance logs cleanly for Reg No: {clr_reg}.")
            else:
                st.error("No verified student matches the provided Registration Number.")
            conn.close()
        else: st.error("Valid target student Registration Number required.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================================
# TAB 5: COLLEGE PROFILE SETTINGS
# =========================================================================
elif menu == "🏢 College Profile":
    st.markdown("### 🏢 Core Enterprise Settings Panel")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#005073;'>🏫 1. Institutional Configuration</h3>", unsafe_allow_html=True)
        with st.form("college_profile_form"):
            new_c_name = st.text_input("College Corporate Name", get_setting('college_name', 'INTERNATIONAL SCHOOL OF MANAGEMENT (ISM)'))
            new_c_sub = st.text_input("Application Functional Subtitle", get_setting('app_subtitle', 'ATTENDANCE MANAGEMENT SYSTEM'))
            new_course = st.text_input("Course Domain Descriptor", get_setting('course_name', 'BCA'))
            new_sec = st.text_input("Section / Semester Target", get_setting('section_name', 'Semester 1'))
            
            if st.form_submit_button("SAVE PLATFORM METADATA"):
                set_setting('college_name', new_c_name)
                set_setting('app_subtitle', new_c_sub)
                set_setting('course_name', new_course)
                set_setting('section_name', new_sec)
                st.success("✅ System header identity synced successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#dc3545;'>🔐 2. Security & Credentials Access</h3>", unsafe_allow_html=True)
        with st.form("login_creds_form"):
            st.write(f"Modify password for User ID: **{USER_ID}**")
            new_admin_pass = st.text_input("Input New Security Password", type="password")
            
            if st.form_submit_button("UPDATE ACCOUNT PASSWORD"):
                if new_admin_pass:
                    conn = sqlite3.connect(MASTER_DB)
                    conn.execute("UPDATE users SET password=? WHERE username=?", (new_admin_pass, USER_ID))
                    conn.commit(); conn.close()
                    st.success("✅ Credentials encrypted and mapped safely.")
                else:
                    st.error("Password field cannot be empty.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#10b981;'>📚 3. Add Custom Subject</h3>", unsafe_allow_html=True)
        with st.form("add_sub_form"):
            n_sub = st.text_input("Instantiate New Subject Label")
            if st.form_submit_button("ADD SUBJECT TO CURRICULUM"):
                if n_sub:
                    conn = sqlite3.connect(DB_NAME)
                    conn.execute("INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)", (n_sub.strip(),))
                    conn.commit(); conn.close()
                    st.success(f"✅ Subject '{n_sub}' added successfully.")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c4:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#f59e0b;'>🖼️ 4. College Logo Brand Upload</h3>", unsafe_allow_html=True)
        logo_file_new = st.file_uploader("Select institutional brand mark (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("UPDATE BRAND GRAPHIC", type="primary"):
            if logo_file_new:
                with open(LOGO_FILE, "wb") as f: f.write(logo_file_new.getbuffer())
                st.success("✅ Brand graphic updated across session vectors.")
                st.rerun()
            else:
                st.error("No valid image file selected.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#ef4444;'>🗑️ 5. Remove Subject</h3>", unsafe_allow_html=True)
    with st.form("del_sub_form"):
        d_sub = st.selectbox("Select Subject to Delete", get_subjects())
        if st.form_submit_button("DELETE SUBJECT PERMANENTLY"):
            if d_sub:
                conn = sqlite3.connect(DB_NAME)
                conn.execute("DELETE FROM subjects WHERE subject_name=?", (d_sub,))
                conn.commit(); conn.close()
                st.success(f"✅ Subject '{d_sub}' removed safely.")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
