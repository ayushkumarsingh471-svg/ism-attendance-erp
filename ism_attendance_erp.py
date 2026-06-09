import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import calendar
import io
import os
import base64

# --- 1. PAGE SETUP & SAFE CSS ---
# initial_sidebar_state="expanded" ensures sidebar starts open
st.set_page_config(layout="wide", page_title="ISM Attendance ERP", page_icon="🎓", initial_sidebar_state="expanded")

# --- 2. MASTER USER DATABASE ---
MASTER_DB = 'master_users.db'
def init_master_db():
    conn = sqlite3.connect(MASTER_DB)
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit(); conn.close()

init_master_db()

# =========================================================================
# 3. SAFE LOGIN & REGISTRATION SCREEN
# =========================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

if not st.session_state.logged_in:
    # SAFE CSS: Top menu/header is NOT hidden so Dark Mode & Sidebar toggle works!
    st.markdown("""
        <style>
        .stApp { background-color: #f8fafc; }
        .block-container { padding-top: 2rem !important; max-width: 1000px !important; }
        
        /* Clean Tab Styling */
        .stTabs [data-baseweb="tab-list"] { justify-content: center; }
        .stTabs [data-baseweb="tab"] { font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    with col1:
        # Safe HTML for left banner
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a, #005073); padding: 50px 40px; border-radius: 15px; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-right: 5px solid #f59e0b; height: 100%;">
            <h1 style="font-size: 42px; font-weight: 900; margin: 0;">🎓 ISM PATNA</h1>
            <h3 style="color: #fcd34d; font-weight: 700; margin-top: 5px;">ATTENDANCE ERP SYSTEM</h3>
            <p style="margin-top: 25px; line-height: 1.7; font-size: 15px; color: #cbd5e1;">
                Welcome to the professional Multi-Tenant Attendance ERP Platform. This enterprise portal provides complete data isolation, analytical insights, automated reports, and secure image profile mapping for individual courses and classes.
            </p>
            <div style="background: rgba(255,255,255,0.08); padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-top: 35px;">
                <b style="color: #fcd34d; font-size: 15px;">💡 Multi-Tenant Isolation Feature:</b><br>
                <span style="font-size: 14px; color: #f8fafc; display: inline-block; margin-top: 8px;">Every class, course coordinator, or administrator can register a custom User ID to instantiate a clean, completely independent localized database.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("<h2 style='text-align:center; color: #0f172a; font-weight: 900;'>🔐 Access Portal</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER NEW CLASS"])
        
        with tab1:
            with st.form("login_form"):
                l_user = st.text_input("User ID", placeholder="Enter User ID")
                l_pass = st.text_input("Password", type="password", placeholder="Enter Password")
                submitted = st.form_submit_button("SECURE LOGIN", type="primary", use_container_width=True)
                
                if submitted:
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
            with st.form("register_form"):
                n_user = st.text_input("User ID", placeholder="Choose User ID (e.g., BCA_Sem1)")
                n_pass = st.text_input("Password", type="password", placeholder="Create Password")
                reg_submitted = st.form_submit_button("REGISTER ACCOUNT", type="primary", use_container_width=True)
                
                if reg_submitted:
                    if n_user and n_pass:
                        conn = sqlite3.connect(MASTER_DB)
                        try:
                            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (n_user.strip(), n_pass))
                            conn.commit()
                            st.success(f"✅ Registered '{n_user}' successfully! Please switch to the Login tab.")
                        except sqlite3.IntegrityError:
                            st.error("⚠️ This User ID already exists. Try another name.")
                        conn.close()
                    else:
                        st.error("Both fields are required.")
    st.stop()

# =========================================================================
# TENANT SPACE ISOLATION CONFIGURATION (AFTER LOGIN)
# =========================================================================
USER_ID = st.session_state.current_user
DB_NAME = f"database_{USER_ID}.db"
PHOTO_DIR = f"photos_{USER_ID}"
LOGO_FILE = f"logo_{USER_ID}.png"
os.makedirs(PHOTO_DIR, exist_ok=True)

# FULL APP CSS (TABLE COLUMN FIX ADDED HERE)
st.markdown("""
    <style>
    /* Make the block container take full width */
    .block-container { padding-top: 2rem !important; max-width: 95% !important; }
    
    /* Attendance Table Styling */
    .excel-table-container { overflow-x: auto; max-height: 650px; border: 1px solid #cbd5e1; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .excel-table { width: 100%; border-collapse: collapse; background: white; font-size: 14px; white-space: nowrap; }
    .excel-table th { background: #0f172a; color: white; padding: 12px; position: sticky; top: 0; z-index: 2; text-align: center; }
    .excel-table td { padding: 10px; border: 1px solid #e2e8f0; text-align: center; }
    
    /* 🔥 EXACT FIX FOR STUDENT NAME COLUMN WIDTH 🔥 */
    .excel-table th:nth-child(3), .excel-table td:nth-child(3) { 
        min-width: 300px !important; 
        text-align: left !important; 
        padding-left: 15px !important;
    }
    
    .row-even { background-color: #f8fafc; }
    .row-odd { background-color: #ffffff; }
    .status-p { background: #10b981; color: white; font-weight: bold; }
    .status-a { background: #ef4444; color: white; font-weight: bold; }
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

# --- HEADER SECTION ---
logo_html = ""
if os.path.exists(LOGO_FILE):
    logo_base64 = get_image_base64(LOGO_FILE)
    logo_html = f"<img src='data:image/png;base64,{logo_base64}' style='max-width:100px; max-height:100px; object-fit:contain; margin-right:20px; border-radius:8px;'>"

c_name = get_setting('college_name', 'INTERNATIONAL SCHOOL OF MANAGEMENT (ISM)')
c_sub = get_setting('app_subtitle', 'ATTENDANCE MANAGEMENT SYSTEM')
c_course = get_setting('course_name', 'BCA')
c_sec = get_setting('section_name', 'Semester 1')

st.markdown(f"""
    <div style="display:flex; align-items:center; background: #0f172a; padding: 20px 30px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-bottom: 5px solid #f59e0b; margin-bottom: 25px;">
        {logo_html}
        <div>
            <h1 style="margin: 0; font-size: 30px; font-weight: 900; color: white;">{c_name}</h1>
            <h3 style="margin: 5px 0 0 0; font-size: 16px; color: #fcd34d;">{c_sub} &nbsp;|&nbsp; {c_course} &nbsp;|&nbsp; {c_sec}</h3>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR NAV ---
st.sidebar.markdown(f"<h3 style='text-align:center; color:#0f172a;'>👤 User: {USER_ID}</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigate Pages:", [
    "📊 Dashboard", 
    "📝 Mark Attendance", 
    "📅 Attendance Table", 
    "👥 Manage Students",
    "🏢 College Profile"
])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 LOGOUT", type="primary"):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.rerun()

if 'current_idx' not in st.session_state: st.session_state.current_idx = 0

# =========================================================================
# TAB 1: DASHBOARD
# =========================================================================
if menu == "📊 Dashboard":
    st.markdown("### 📈 Monthly Overview & Daily Status")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    now = datetime.now()
    sel_month = col_a.selectbox("Month", list(calendar.month_name)[1:], index=now.month-1)
    sel_year = col_b.selectbox("Year", [now.year-1, now.year, now.year+1], index=1)
    sel_sub = col_c.selectbox("Subject", get_subjects())
    target_date = col_d.date_input("Select Date", date.today())
    
    month_num = list(calendar.month_name).index(sel_month)
    date_pattern = f"{sel_year}-{month_num:02d}-%"
    
    conn = sqlite3.connect(DB_NAME)
    total_students = conn.execute("SELECT COUNT(id) FROM students").fetchone()[0] or 0
    tc_count = conn.execute("SELECT COUNT(DISTINCT date) FROM attendance WHERE subject_id=(SELECT id FROM subjects WHERE subject_name=?) AND date LIKE ?", (sel_sub, date_pattern)).fetchone()[0] or 0
    present_today = conn.execute("SELECT COUNT(date) FROM attendance WHERE subject_id=(SELECT id FROM subjects WHERE subject_name=?) AND date=? AND status='Present'", (sel_sub, str(target_date))).fetchone()[0] or 0
    conn.close()
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    def metric_card(title, value, color):
        return f"<div style='background: white; border-radius: 12px; padding: 20px; text-align: center; border-top: 4px solid {color}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'><h4 style='margin:0; color:#64748b; font-size:16px;'>{title}</h4><h2 style='margin:10px 0 0 0; color:#0f172a; font-size:32px;'>{value}</h2></div>"
        
    c1.markdown(metric_card("Total Students", total_students, "#3b82f6"), unsafe_allow_html=True)
    c2.markdown(metric_card("Classes Conducted", tc_count, "#8b5cf6"), unsafe_allow_html=True)
    c3.markdown(metric_card("Selected Subject", sel_sub, "#10b981"), unsafe_allow_html=True)
    c4.markdown(metric_card(f"Present on {target_date.strftime('%d %b')}", present_today, "#f59e0b"), unsafe_allow_html=True)

# =========================================================================
# TAB 2: MARK ATTENDANCE (PROFESSIONAL ID CARD)
# =========================================================================
elif menu == "📝 Mark Attendance":
    st.markdown("### 📝 Active Mark Attendance Panel")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    now = datetime.now()
    sel_month = col_a.selectbox("Month", list(calendar.month_name)[1:], index=now.month-1)
    sel_year = col_b.selectbox("Year", [now.year-1, now.year, now.year+1], index=1)
    sel_sub = col_c.selectbox("Subject", get_subjects())
    target_date = col_d.date_input("Date", date.today())

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    students_df = pd.read_sql("SELECT id, reg_no, roll_no, name FROM students ORDER BY CAST(roll_no AS INTEGER) ASC", conn)
    student_list = students_df.values.tolist() if not students_df.empty else []
    
    if student_list:
        if st.session_state.current_idx >= len(student_list): st.session_state.current_idx = len(student_list) - 1
        curr_student = student_list[st.session_state.current_idx]
        s_id, s_reg, s_roll, s_name = curr_student
        photo_url = get_student_photo_url(s_reg)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        col_prof, col_space, col_btn = st.columns([2.5, 0.2, 1.5])
        
        with col_prof:
            # PURE HTML PROFESSIONAL ID CARD (100% SAFE)
            profile_html = f"""
            <div style='background: white; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #cbd5e1; text-align: center; max-width: 350px; margin: 0 auto; overflow: hidden; position: relative;'>
                <div style='background: #0f172a; padding: 15px; color: #fcd34d; font-weight: 900; font-size: 16px; letter-spacing: 1px;'>
                    <div style='width: 40px; height: 5px; background: rgba(255,255,255,0.2); border-radius: 10px; margin: 0 auto 10px auto;'></div>
                    STUDENT ID CARD
                </div>
                <div style='padding: 25px 20px;'>
                    <img src='{photo_url}' style='width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 5px solid white; box-shadow: 0 5px 15px rgba(0,0,0,0.15); margin-bottom: 15px;'>
                    <h2 style='color: #0f172a; font-size: 24px; font-weight: 900; margin: 0;'>{s_name}</h2>
                    <div style='background: #f1f5f9; color: #ef4444; padding: 6px 15px; border-radius: 6px; font-weight: bold; margin: 10px 0; border: 1px solid #e2e8f0; display: inline-block;'>
                        REG NO: {s_reg}
                    </div>
                    <h4 style='color: #64748b; margin: 0; font-size: 15px;'>ROLL NO: {s_roll}</h4>
                </div>
                <div style='background: #f8fafc; padding: 12px; color: #475569; font-weight: bold; font-size: 12px; border-top: 1px solid #e2e8f0;'>
                    {c_name}
                </div>
            </div>
            """
            st.markdown(profile_html, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            student_options = [f"{s[1]} - {s[3]}" for s in student_list]
            selected_student = st.selectbox("🔍 Quick Jump to Student", student_options, index=st.session_state.current_idx)
            if student_options.index(selected_student) != st.session_state.current_idx:
                st.session_state.current_idx = student_options.index(selected_student)
                st.rerun()
                
            n1, n2 = st.columns(2)
            if n1.button("◀ PREVIOUS", use_container_width=True):
                if st.session_state.current_idx > 0: st.session_state.current_idx -= 1; st.rerun()
            if n2.button("NEXT ▶", use_container_width=True):
                if st.session_state.current_idx < len(student_list) - 1: st.session_state.current_idx += 1; st.rerun()

        with col_btn:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            
            # Safe Native Buttons
            if st.button("🟢 MARK PRESENT (P)", type="primary", use_container_width=True):
                cursor.execute("INSERT OR REPLACE INTO attendance (student_id, subject_id, date, status) VALUES (?, (SELECT id FROM subjects WHERE subject_name=?), ?, 'Present')", (s_id, sel_sub, str(target_date)))
                conn.commit()
                st.toast(f"{s_name} Marked PRESENT", icon="🟢")
                if st.session_state.current_idx < len(student_list) - 1: st.session_state.current_idx += 1
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🔴 MARK ABSENT (A)", use_container_width=True):
                cursor.execute("INSERT OR REPLACE INTO attendance (student_id, subject_id, date, status) VALUES (?, (SELECT id FROM subjects WHERE subject_name=?), ?, 'Absent')", (s_id, sel_sub, str(target_date)))
                conn.commit()
                st.toast(f"{s_name} Marked ABSENT", icon="🔴")
                if st.session_state.current_idx < len(student_list) - 1: st.session_state.current_idx += 1
                st.rerun()
            
    else:
        st.warning("No students available. Go to Manage Students to import records.")
    conn.close()

# =========================================================================
# TAB 3: ATTENDANCE TABLE
# =========================================================================
elif menu == "📅 Attendance Table":
    st.markdown("### 📅 Monthly Register")
    
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
        html_grid += '<tr><th>Reg No</th><th>Roll</th><th>Student Name</th>'
        for d in range(1, num_days + 1): html_grid += f'<th>{d}</th>'
        html_grid += '<th>%</th></tr>'
        
        row_counter = 0
        for idx, row in students_df.iterrows():
            row_class = "row-even" if row_counter % 2 == 0 else "row-odd"
            row_counter += 1
            html_grid += f'<tr class="{row_class}">'
            
            html_grid += f'<td>{row["reg_no"]}</td>'
            html_grid += f'<td>{row["roll_no"]}</td>'
            html_grid += f'<td>{row["name"]}</td>'
            
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
            html_grid += f'<td style="color:#0f172a; font-weight:bold;">{pct:.0f}%</td></tr>'
            
        html_grid += '</table></div>'
        st.markdown(html_grid, unsafe_allow_html=True)
    else:
        st.info("No data found. Please add records.")
    conn.close()

# =========================================================================
# TAB 4: MANAGE STUDENTS
# =========================================================================
elif menu == "👥 Manage Students":
    st.markdown("### 👥 Database Management")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ➕ Add New Student")
        with st.form("add_student_form"):
            new_reg = st.text_input("Registration No")
            new_roll = st.text_input("Roll No")
            new_name = st.text_input("Full Name")
            if st.form_submit_button("Save Student", type="primary"):
                if new_reg and new_name:
                    conn = sqlite3.connect(DB_NAME)
                    conn.execute("INSERT OR IGNORE INTO students (reg_no, roll_no, name) VALUES (?, ?, ?)", (new_reg.strip(), new_roll.strip(), new_name.strip()))
                    conn.commit(); conn.close()
                    st.success("Student added successfully!")
                else: st.error("Reg No and Name are required.")

    with c2:
        st.markdown("#### 🗑️ Delete Student")
        with st.form("delete_student_form"):
            del_reg = st.text_input("Enter Reg No to Delete")
            if st.form_submit_button("Delete Student", type="primary"):
                if del_reg:
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM students WHERE reg_no = ?", (del_reg.strip(),))
                    if cursor.rowcount > 0: st.success("Record deleted.")
                    else: st.warning("Record not found.")
                    conn.commit(); conn.close()

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 📥 Bulk Import (Excel/CSV)")
        with st.form("bulk_import_form"):
            uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])
            if st.form_submit_button("Import Data", type="primary"):
                if uploaded_file is not None:
                    try:
                        if uploaded_file.name.endswith('.csv'): df_raw = pd.read_csv(uploaded_file)
                        else: df_raw = pd.read_excel(uploaded_file)
                        if len(df_raw.columns) >= 3:
                            df_clean = df_raw.iloc[:, :3].copy()
                            df_clean.columns = ['reg_no', 'roll_no', 'name']
                            df_clean = df_clean.dropna(subset=['reg_no', 'name'])
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
                            st.success("Imported successfully!")
                    except Exception as e: st.error("Error reading file.")
                else:
                    st.warning("Please select a file first.")

    with c4:
        st.markdown("#### 📸 Upload Photo Mapping")
        with st.form("photo_upload_form"):
            reg_input = st.text_input("Student Reg No")
            photo_file = st.file_uploader("Image (JPG, PNG)", type=["jpg", "png", "jpeg"])
            if st.form_submit_button("Save Photo", type="primary"):
                if reg_input and photo_file:
                    ext = photo_file.name.split('.')[-1].lower()
                    with open(os.path.join(PHOTO_DIR, f"{reg_input.strip()}.{ext}"), "wb") as f: f.write(photo_file.getbuffer())
                    st.success("Photo saved!")
                else: st.error("Reg No and file are required.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🧹 Remove Specific Attendance")
    with st.form("remove_att_form"):
        r_a1, r_a2 = st.columns(2)
        clr_reg = r_a1.text_input("Enter Target Reg No")
        clr_sub = r_a2.selectbox("Select Subject", ["All Subjects"] + get_subjects())
        if st.form_submit_button("Purge Records", type="primary"):
            if clr_reg:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM students WHERE reg_no=?", (clr_reg,))
                s_res = cursor.fetchone()
                if s_res:
                    s_id = s_res[0]
                    if clr_sub == "All Subjects": cursor.execute("DELETE FROM attendance WHERE student_id=?", (s_id,))
                    else: cursor.execute("DELETE FROM attendance WHERE student_id=? AND subject_id=(SELECT id FROM subjects WHERE subject_name=?)", (s_id, clr_sub))
                    rows_deleted = cursor.rowcount
                    conn.commit()
                    st.success(f"Purged {rows_deleted} logs for Reg No: {clr_reg}.")
                else: st.error("Student not found.")
                conn.close()
            else: st.error("Reg No required.")

# =========================================================================
# TAB 5: COLLEGE PROFILE SETTINGS
# =========================================================================
elif menu == "🏢 College Profile":
    st.markdown("### 🏢 Core Settings")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🏫 Institutional Config")
        with st.form("college_profile_form"):
            new_c_name = st.text_input("College Name", get_setting('college_name', 'INTERNATIONAL SCHOOL OF MANAGEMENT (ISM)'))
            new_c_sub = st.text_input("Subtitle", get_setting('app_subtitle', 'ATTENDANCE MANAGEMENT SYSTEM'))
            new_course = st.text_input("Course", get_setting('course_name', 'BCA'))
            new_sec = st.text_input("Semester", get_setting('section_name', 'Semester 1'))
            if st.form_submit_button("Save Metadata", type="primary"):
                set_setting('college_name', new_c_name); set_setting('app_subtitle', new_c_sub)
                set_setting('course_name', new_course); set_setting('section_name', new_sec)
                st.success("Saved!")
                st.rerun()

    with c2:
        st.markdown("#### 🔐 Security Access")
        with st.form("login_creds_form"):
            new_admin_pass = st.text_input(f"New Password for {USER_ID}", type="password")
            if st.form_submit_button("Update Password", type="primary"):
                if new_admin_pass:
                    conn = sqlite3.connect(MASTER_DB)
                    conn.execute("UPDATE users SET password=? WHERE username=?", (new_admin_pass, USER_ID))
                    conn.commit(); conn.close()
                    st.success("Updated safely.")
                else: st.error("Cannot be empty.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 📚 Add Subject")
        with st.form("add_sub_form"):
            n_sub = st.text_input("Subject Name")
            if st.form_submit_button("Add Subject", type="primary"):
                if n_sub:
                    conn = sqlite3.connect(DB_NAME)
                    conn.execute("INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)", (n_sub.strip(),))
                    conn.commit(); conn.close()
                    st.success("Added!")
                    st.rerun()
        
    with c4:
        st.markdown("#### 🖼️ College Logo")
        with st.form("logo_form"):
            logo_file_new = st.file_uploader("Select PNG/JPG", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("Upload Logo", type="primary"):
                if logo_file_new:
                    with open(LOGO_FILE, "wb") as f: f.write(logo_file_new.getbuffer())
                    st.success("Updated!")
                    st.rerun()
                else: st.error("No file selected.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🗑️ Delete Subject")
    with st.form("del_sub_form"):
        d_sub = st.selectbox("Select Subject", get_subjects())
        if st.form_submit_button("Delete Subject", type="primary"):
            if d_sub:
                conn = sqlite3.connect(DB_NAME)
                conn.execute("DELETE FROM subjects WHERE subject_name=?", (d_sub,))
                conn.commit(); conn.close()
                st.success("Removed.")
                st.rerun()
