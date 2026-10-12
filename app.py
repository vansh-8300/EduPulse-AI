"""
EduPulse AI - Student Analytics & Success Platform
Main Streamlit Web Application (Dark Green AI Intelligence Edition)
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_student_data, get_filtered_students, get_cohort_kpis
from src.model_utils import load_model, predict_student_risk, explain_student_indicators, predict_placement_risk
from src.recommendations import generate_recommendations

# --- Page Configuration ---
st.set_page_config(
    page_title="EduPulse AI | Student Intelligence Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS Design System
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

import urllib.request
import json

# --- Firebase Client Authentication Setup ---
FIREBASE_API_KEY = (
    st.secrets.get("FIREBASE_API_KEY") or 
    os.getenv("FIREBASE_API_KEY") or 
    "AIzaSyAE7mLwzMwsm7eTE2d1LaIalhZYz2V1eso"
)

def firebase_auth_sign_in(email: str, password: str):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return True, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            err_msg = err_data.get("error", {}).get("message", "INVALID_LOGIN_CREDENTIALS")
        except Exception:
            err_msg = "AUTHENTICATION_FAILED"
        return False, err_msg
    except Exception as e:
        return False, str(e)

def firebase_auth_sign_up(email: str, password: str, display_name: str = None):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            if display_name and "idToken" in data:
                update_url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}"
                up_payload = json.dumps({
                    "idToken": data["idToken"],
                    "displayName": display_name,
                    "returnSecureToken": True
                }).encode("utf-8")
                up_req = urllib.request.Request(update_url, data=up_payload, headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(up_req) as up_res:
                        data = json.loads(up_res.read().decode("utf-8"))
                except Exception:
                    pass
            return True, data
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            err_msg = err_data.get("error", {}).get("message", "SIGNUP_FAILED")
        except Exception:
            err_msg = "SIGNUP_FAILED"
        return False, err_msg
    except Exception as e:
        return False, str(e)

def translate_firebase_error(error_code: str) -> str:
    if "INVALID_LOGIN_CREDENTIALS" in error_code or "INVALID_PASSWORD" in error_code:
        return "Incorrect email address or password. Please try again."
    elif "EMAIL_NOT_FOUND" in error_code:
        return "No account was found with this email address."
    elif "EMAIL_EXISTS" in error_code:
        return "An account already exists with this email address."
    elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_code:
        return "Too many failed attempts. Please wait and try again later."
    elif "WEAK_PASSWORD" in error_code:
        return "Password must be at least 6 characters long."
    elif "INVALID_EMAIL" in error_code:
        return "Please enter a valid email address."
    elif "USER_DISABLED" in error_code:
        return "This user account has been disabled."
    elif "OPERATION_NOT_ALLOWED" in error_code:
        return "Email/password sign-in is not enabled in your Firebase Console."
    return f"Authentication failed: {error_code}"

def render_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(key="auth_card"):
            st.markdown("""
            <div class="auth-brand-header">
                <div class="auth-logo-badge">
                    <span class="auth-logo-icon">🎓</span>
                </div>
                <h1 class="auth-brand-title">EduPulse AI</h1>
                <div class="auth-brand-subtitle">
                    Student Intelligence & Risk Analytics Portal
                </div>
                <div class="auth-secure-badge">
                    <span class="auth-pulse-dot"></span>
                    <span>SECURE ACCESS</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            tab_login, tab_signup = st.tabs(["🔐 Log In", "📝 Create Account"])
            
            with tab_login:
                st.markdown("##### Access your EduPulse AI workspace")
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input("School / Work Email", placeholder="you@school.edu", key="login_email").strip()
                    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pw")
                    submit_login = st.form_submit_button("Log In to Dashboard", use_container_width=True)
                    
                    if submit_login:
                        if not email or not password:
                            st.error("Please enter both email address and password.")
                        else:
                            with st.spinner("Authenticating with Firebase..."):
                                success, res = firebase_auth_sign_in(email, password)
                                if success:
                                    st.session_state["authenticated"] = True
                                    st.session_state["user_email"] = res.get("email", email)
                                    st.session_state["user_name"] = res.get("displayName") or email.split("@")[0].capitalize()
                                    st.session_state["user_id"] = res.get("localId")
                                    st.success(f"Welcome back, {st.session_state['user_name']}!")
                                    st.rerun()
                                else:
                                    st.error(translate_firebase_error(str(res)))
            
            with tab_signup:
                st.markdown("##### Create a new advisor account")
                with st.form("signup_form", clear_on_submit=False):
                    full_name = st.text_input("Full Name", placeholder="Aarav Sharma", key="su_name").strip()
                    email = st.text_input("School / Work Email", placeholder="you@school.edu", key="su_email").strip()
                    password = st.text_input("Password (min. 6 chars)", type="password", placeholder="Choose a secure password", key="su_pw")
                    submit_signup = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if submit_signup:
                        if not full_name or not email or not password:
                            st.error("Please complete all fields.")
                        elif len(password) < 6:
                            st.error("Password must be at least 6 characters long.")
                        else:
                            with st.spinner("Creating Firebase account..."):
                                success, res = firebase_auth_sign_up(email, password, display_name=full_name)
                                if success:
                                    st.session_state["authenticated"] = True
                                    st.session_state["user_email"] = res.get("email", email)
                                    st.session_state["user_name"] = full_name
                                    st.session_state["user_id"] = res.get("localId")
                                    st.success(f"Account created successfully! Welcome, {full_name}!")
                                    st.rerun()
                                else:
                                    st.error(translate_firebase_error(str(res)))

# Check authentication state - block protected dashboard until authenticated
if not st.session_state.get("authenticated", False):
    render_login_page()
    st.stop()

# Helper function to apply uniform Dark Green Plotly styling
def apply_dark_green_plotly_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif', color="#F0FDF4"),
        margin=dict(t=30, b=30, l=20, r=20),
        xaxis=dict(gridcolor='rgba(94, 234, 160, 0.12)', zerolinecolor='rgba(94, 234, 160, 0.2)'),
        yaxis=dict(gridcolor='rgba(94, 234, 160, 0.12)', zerolinecolor='rgba(94, 234, 160, 0.2)')
    )
    return fig


# --- Load Data & Model Artifact ---
@st.cache_data
def get_cached_data():
    return load_student_data()

@st.cache_resource
def get_cached_model():
    return load_model()

df = get_cached_data()
artifact = get_cached_model()

# Risk Palette
RISK_COLORS = {
    "High": "#EF4444",
    "Medium": "#F59E0B",
    "Low": "#10B981"
}


# --- Sidebar Navigation & Controls ---
st.sidebar.image("https://img.icons8.com/isometric/96/000000/graduation-cap.png", width=55)
st.sidebar.title("EduPulse AI")
st.sidebar.markdown("<div style='font-size:0.82rem; color:#9CB7A5; margin-top:-10px; margin-bottom:15px; font-weight:600;'>Student Intelligence Platform</div>", unsafe_allow_html=True)

# User Session & Logout Control in Sidebar
user_name = st.session_state.get("user_name", "User")
user_email = st.session_state.get("user_email", "")

st.sidebar.markdown(f"""
<div style="background: rgba(16, 39, 28, 0.9); border: 1px solid rgba(94, 234, 160, 0.25); padding: 0.75rem; border-radius: 10px; margin-bottom: 12px;">
    <div style="font-size: 0.72rem; color: #9CB7A5; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Authenticated Session</div>
    <div style="color: #F0FDF4; font-weight: 700; font-size: 0.92rem; margin-top: 2px;">{user_name}</div>
    <div style="color: #5FF2A5; font-size: 0.78rem; word-break: break-all;">{user_email}</div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Log Out Session", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state.pop("user_email", None)
    st.session_state.pop("user_name", None)
    st.session_state.pop("user_id", None)
    st.rerun()

st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Navigation Mode:",
    [
        "📊 Dashboard Overview",
        "🎓 Student Risk Predictor",
        "👤 Student Deep Dive",
        "🛠️ AI Recommendations",
        "🔮 What-If Simulator",
        "📁 Student Data Explorer"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filter Cohort Data")
selected_major = st.sidebar.selectbox(
    "Department / Major:",
    ["All Majors"] + sorted(list(df["major"].unique()))
)

selected_grade = st.sidebar.selectbox(
    "Grade Level:",
    ["All Grades"] + list(df["grade_level"].unique())
)

selected_risk_filter = st.sidebar.selectbox(
    "Risk Level Filter:",
    ["All Risk Levels", "High", "Medium", "Low"]
)

# Apply Sidebar Filters
filtered_df = get_filtered_students(
    df,
    major=selected_major,
    grade_level=selected_grade,
    risk_level=selected_risk_filter
)

st.sidebar.markdown("---")

# System & Model Status Indicators in Sidebar
st.sidebar.markdown(f"""
<div style="background: rgba(16, 39, 28, 0.85); border: 1px solid rgba(94, 234, 160, 0.2); padding: 0.85rem; border-radius: 12px; font-size: 0.78rem;">
    <div style="display:flex; align-items:center; gap:6px; color:#5FF2A5; font-weight:700; margin-bottom:4px;">
        <span class="pulse-dot"></span> SYSTEM ONLINE
    </div>
    <div style="color:#9CB7A5;">• Model: Random Forest Classifier</div>
    <div style="color:#9CB7A5;">• Active Dataset: {len(df)} Records</div>
    <div style="color:#9CB7A5;">• Filtered View: {len(filtered_df)} Records</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.caption("⚠️ **Demo Disclaimer**: EduPulse AI uses synthetic student data (`students_1200.csv`) and a prototype ML model for hackathon demonstration. It is not validated for real-world academic decisions.")


# --- Top Header Section ---
st.markdown("""
<div class="header-container animate-fade-in">
    <div class="header-top-row">
        <div>
            <h1 class="header-title">🎓 Student Intelligence Dashboard</h1>
            <div class="header-subtitle">AI-powered academic risk monitoring and student success analytics</div>
        </div>
        <div class="status-pills">
            <div class="pill-indicator">
                <span class="pulse-dot"></span> 1,200 RECORDS LOADED
            </div>
            <div class="pill-indicator" style="border-color: rgba(34, 197, 94, 0.4); color: #22C55E;">
                RANDOM FOREST MODEL READY
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# VIEW 1: DASHBOARD OVERVIEW
# ==========================================
if app_mode == "📊 Dashboard Overview":
    # Hero Welcome Panel
    st.markdown("""
    <div class="hero-card animate-slide-up">
        <div class="hero-glow-bg"></div>
        <div class="hero-text-content">
            <h2>Predict Risk. Empower Success.</h2>
            <p>EduPulse AI monitors early behavioral indicators—attendance, LMS engagement, assignment completion, and midterm performance—to deliver predictive risk scores and automated academic support interventions before dropouts occur.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(filtered_df) == 0:
        st.info("ℹ️ No students match the current sidebar filter selection. Reset or broaden filters to view cohort metrics.")

    kpis = get_cohort_kpis(filtered_df)

    # KPI Row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown(f"""
        <div class="kpi-card-enhanced animate-fade-in">
            <div class="kpi-card-header">
                <span class="kpi-label">Total Cohort</span>
                <div class="kpi-icon-wrapper">👥</div>
            </div>
            <div class="kpi-val">{kpis['total']}</div>
            <div class="kpi-sub">Active Students</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card-enhanced kpi-danger animate-fade-in">
            <div class="kpi-card-header">
                <span class="kpi-label">High Risk</span>
                <div class="kpi-icon-wrapper" style="background:rgba(239,68,68,0.15); color:#EF4444;">⚠️</div>
            </div>
            <div class="kpi-val" style="color:#EF4444;">{kpis['high_risk_cnt']}</div>
            <div class="kpi-sub" style="color:#EF4444;">{kpis['high_risk_pct']}% of total</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card-enhanced animate-fade-in">
            <div class="kpi-card-header">
                <span class="kpi-label">Success Score</span>
                <div class="kpi-icon-wrapper">⚡</div>
            </div>
            <div class="kpi-val" style="color:#5FF2A5;">{kpis['avg_success_score']}</div>
            <div class="kpi-sub">Cohort Avg / 100</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card-enhanced animate-fade-in">
            <div class="kpi-card-header">
                <span class="kpi-label">Cohort GPA</span>
                <div class="kpi-icon-wrapper">📘</div>
            </div>
            <div class="kpi-val" style="color:#38BDF8;">{kpis['avg_gpa']}</div>
            <div class="kpi-sub">4.0 Scale</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card-enhanced animate-fade-in">
            <div class="kpi-card-header">
                <span class="kpi-label">Attendance</span>
                <div class="kpi-icon-wrapper">🕒</div>
            </div>
            <div class="kpi-val" style="color:#10B981;">{kpis['avg_attendance']}%</div>
            <div class="kpi-sub">Target: 80%+</div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="kpi-card-enhanced animate-fade-in">
            <div class="kpi-card-header">
                <span class="kpi-label">Assignment Rate</span>
                <div class="kpi-icon-wrapper">📝</div>
            </div>
            <div class="kpi-val" style="color:#A855F7;">{kpis['avg_assignment']}%</div>
            <div class="kpi-sub">Target: 85%+</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1: Donut & Scatter Plot
    c1, c2 = st.columns([1.2, 1.8])

    with c1:
        st.subheader("🎯 Academic Risk Distribution")
        risk_counts = filtered_df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Count"]

        fig_donut = px.pie(
            risk_counts,
            values="Count",
            names="Risk Level",
            hole=0.55,
            color="Risk Level",
            color_discrete_map=RISK_COLORS
        )
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#07130F', width=2))
        )
        apply_dark_green_plotly_theme(fig_donut)
        st.plotly_chart(fig_donut, width="stretch")

    with c2:
        st.subheader("📈 GPA vs. Attendance Rate by Risk Tier")
        fig_scatter = px.scatter(
            filtered_df,
            x="attendance_rate",
            y="gpa",
            color="risk_level",
            size="study_hours_per_week",
            hover_data=["student_id", "name", "major"],
            labels={"attendance_rate": "Attendance Rate (%)", "gpa": "GPA", "study_hours_per_week": "Study Hrs/Wk"},
            color_discrete_map=RISK_COLORS
        )
        fig_scatter.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color='rgba(255,255,255,0.4)')))
        apply_dark_green_plotly_theme(fig_scatter)
        st.plotly_chart(fig_scatter, width="stretch")

    # Charts Row 2: Department & Grade Breakdown
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("🏢 Risk Breakdown by Major / Department")
        dept_risk = pd.crosstab(filtered_df["major"], filtered_df["risk_level"]).reindex(columns=["High", "Medium", "Low"], fill_value=0).reset_index()
        fig_dept = px.bar(
            dept_risk,
            x="major",
            y=["High", "Medium", "Low"],
            color_discrete_map=RISK_COLORS,
            labels={"value": "Student Count", "major": "Major"}
        )
        fig_dept.update_layout(barmode="stack")
        apply_dark_green_plotly_theme(fig_dept)
        st.plotly_chart(fig_dept, width="stretch")

    with c4:
        st.subheader("🎓 Risk Breakdown by Grade Level")
        grade_risk = pd.crosstab(filtered_df["grade_level"], filtered_df["risk_level"]).reindex(columns=["High", "Medium", "Low"], fill_value=0).reset_index()
        fig_grade = px.bar(
            grade_risk,
            x="grade_level",
            y=["High", "Medium", "Low"],
            color_discrete_map=RISK_COLORS,
            labels={"value": "Student Count", "grade_level": "Grade Level"}
        )
        fig_grade.update_layout(barmode="group")
        apply_dark_green_plotly_theme(fig_grade)
        st.plotly_chart(fig_grade, width="stretch")


# ==========================================
# VIEW 2: STUDENT RISK PREDICTOR
# ==========================================
elif app_mode == "🎓 Student Risk Predictor":
    st.subheader("🔍 Select Student Record to Analyze")

    search_col, select_col = st.columns([1, 2])
    with search_col:
        search_query = st.text_input("Filter by Name or ID:", placeholder="e.g. EDU-2026-1015 or Alex")

    selectable_df = get_filtered_students(df, search_query=search_query) if search_query else df
    student_options = [f"{row['student_id']} - {row['name']} ({row['major']})" for _, row in selectable_df.iterrows()]

    if not student_options:
        st.warning("No student matching your query was found.")
        st.stop()

    with select_col:
        selected_option = st.selectbox("Choose Student Record:", student_options)

    selected_id = selected_option.split(" - ")[0]
    student = df[df["student_id"] == selected_id].iloc[0]

    # Run Prediction & Feature Explanation
    pred = predict_student_risk(student, artifact)
    placement_pred = predict_placement_risk(student)

    st.markdown("---")

    # Student Header Card & Risk Summary
    sc1, sc2 = st.columns([1.5, 2.5])

    with sc1:
        tuition_color = "#10B981" if student['tuition_status']=='Paid' else "#EF4444"
        st.markdown(f"""
        <div class="section-glass-container">
            <h3 style="color: #5FF2A5; margin-top:0; font-size: 1.35rem; font-weight: 800;">👤 {student['name']}</h3>
            <div style="display: flex; flex-direction: column; gap: 0.45rem; margin-top: 0.8rem; font-size: 0.95rem;">
                <div><span style="color: #9CB7A5; font-weight: 600;">Student ID:</span> <span style="font-weight: 700; color: #F0FDF4;">{student['student_id']}</span></div>
                <div><span style="color: #9CB7A5; font-weight: 600;">Major:</span> <span style="font-weight: 700; color: #F0FDF4;">{student['major']}</span></div>
                <div><span style="color: #9CB7A5; font-weight: 600;">Grade Level:</span> <span style="font-weight: 700; color: #F0FDF4;">{student['grade_level']}</span></div>
                <div><span style="color: #9CB7A5; font-weight: 600;">Success Score:</span> <span style="color: #5FF2A5; font-weight: 800; font-size: 1.1rem;">{pred['success_score']} / 100</span></div>
                <div><span style="color: #9CB7A5; font-weight: 600;">Tuition Status:</span> <span style="color: {tuition_color}; font-weight: 700;">{student['tuition_status']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        risk_class = pred["predicted_risk"]
        color_hex = RISK_COLORS.get(risk_class, "#10B981")
        badge_symbol = "🔴" if risk_class == "High" else "🟡" if risk_class == "Medium" else "🟢"

        p_risk = placement_pred["placement_risk"]
        p_color = RISK_COLORS.get(p_risk, "#10B981")
        p_symbol = "🔴" if p_risk == "High" else "🟡" if p_risk == "Medium" else "🟢"

        st.markdown(f"""
        <div class="section-glass-container" style="border-top: 4px solid {color_hex}; text-align: center;">
            <div style="display: flex; justify-content: space-around; align-items: center; gap: 1rem;">
                <div style="flex: 1;">
                    <div style="font-size: 0.8rem; color: #9CB7A5; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Academic Risk Level</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: {color_hex}; margin: 0.3rem 0;">
                        {badge_symbol} {risk_class.upper()} RISK
                    </div>
                </div>
                <div style="border-left: 1px solid rgba(94, 234, 160, 0.15); height: 55px;"></div>
                <div style="flex: 1;">
                    <div style="font-size: 0.8rem; color: #9CB7A5; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Placement Readiness Risk</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: {p_color}; margin: 0.3rem 0;">
                        {p_symbol} {p_risk.upper()} RISK
                    </div>
                    <div style="font-size: 0.8rem; color: #9CB7A5; font-weight: 600;">Readiness Score: {placement_pred['placement_score']}/100</div>
                </div>
            </div>
            <div style="margin-top: 1.2rem; padding-top: 0.9rem; border-top: 1px solid rgba(94, 234, 160, 0.12);">
                <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 0.4rem;">
                    <div style="flex: 1; padding: 0 0.5rem; text-align: left;">
                        <span style="color:#EF4444; font-weight:700;">High Risk:</span> <span style="font-weight:800; color:#F0FDF4;">{pred['high_risk_prob']}%</span>
                        <div class="prob-bar-container"><div class="prob-bar-fill prob-bar-high" style="width: {pred['high_risk_prob']}%;"></div></div>
                    </div>
                    <div style="flex: 1; padding: 0 0.5rem; text-align: left;">
                        <span style="color:#F59E0B; font-weight:700;">Medium Risk:</span> <span style="font-weight:800; color:#F0FDF4;">{pred['medium_risk_prob']}%</span>
                        <div class="prob-bar-container"><div class="prob-bar-fill prob-bar-medium" style="width: {pred['medium_risk_prob']}%;"></div></div>
                    </div>
                    <div style="flex: 1; padding: 0 0.5rem; text-align: left;">
                        <span style="color:#10B981; font-weight:700;">Low Risk:</span> <span style="font-weight:800; color:#F0FDF4;">{pred['low_risk_prob']}%</span>
                        <div class="prob-bar-container"><div class="prob-bar-fill prob-bar-low" style="width: {pred['low_risk_prob']}%;"></div></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# VIEW 3: STUDENT DEEP DIVE
# ==========================================
elif app_mode == "👤 Student Deep Dive":
    st.subheader("👤 Student Feature Indicators & Deep Dive Analysis")

    search_col, select_col = st.columns([1, 2])
    with search_col:
        search_query = st.text_input("Search student name/ID:", placeholder="e.g. Alex")

    selectable_df = get_filtered_students(df, search_query=search_query) if search_query else df
    student_options = [f"{row['student_id']} - {row['name']} ({row['major']})" for _, row in selectable_df.iterrows()]

    if not student_options:
        st.warning("No student matching your query was found.")
        st.stop()

    with select_col:
        selected_option = st.selectbox("Select Student for Feature Analysis:", student_options)

    selected_id = selected_option.split(" - ")[0]
    student = df[df["student_id"] == selected_id].iloc[0]

    indicators = explain_student_indicators(student, artifact)

    st.markdown("---")
    ind_col1, ind_col2 = st.columns([1.8, 1.2])

    with ind_col1:
        st.markdown("#### Feature Metrics vs. Cohort Average")
        ind_df = pd.DataFrame(indicators)

        fig_ind = px.bar(
            ind_df,
            x="impact_score",
            y="feature_name",
            orientation="h",
            color="status",
            color_discrete_map={
                "Risk Driver": "#EF4444",
                "Average": "#64748B",
                "Positive Strength": "#10B981"
            },
            labels={"impact_score": "Relative Indicator Impact Score", "feature_name": "Indicator"},
            hover_data=["student_value", "cohort_avg", "badge"]
        )
        fig_ind.update_layout(yaxis=dict(autorange="reversed"))
        apply_dark_green_plotly_theme(fig_ind)
        st.plotly_chart(fig_ind, width="stretch")

    with ind_col2:
        st.markdown("#### Indicator Summary Table")
        display_ind = ind_df[["badge", "feature_name", "student_value", "cohort_avg"]].copy()
        display_ind.columns = ["Status", "Metric", "Student Value", "Cohort Avg"]
        st.dataframe(display_ind, width="stretch", hide_index=True)


# ==========================================
# VIEW 4: AI RECOMMENDATIONS
# ==========================================
elif app_mode == "🛠️ AI Recommendations":
    st.subheader("🛠️ Actionable Support Interventions & Recommendations")

    sim_student_id = st.selectbox("Select Student for Recommendations:", df["student_id"] + " - " + df["name"])
    sid = sim_student_id.split(" - ")[0]
    student = df[df["student_id"] == sid].iloc[0]

    pred = predict_student_risk(student, artifact)
    placement_pred = predict_placement_risk(student)
    recommendations = generate_recommendations(student, pred, placement_pred)

    st.markdown("---")

    for rec in recommendations:
        priority_color = "#EF4444" if "High" in rec["priority"] or "Critical" in rec["priority"] else "#F59E0B" if "Medium" in rec["priority"] else "#5FF2A5"

        st.markdown(f"""
        <div class="rec-item-card" style="border-left-color: {priority_color};">
            <div class="rec-item-header">
                <span class="rec-item-title">{rec['action']}</span>
                <span style="background-color: {priority_color}; color: #07130F; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem; font-weight: 800;">
                    {rec['priority']}
                </span>
            </div>
            <div class="rec-category-tag">
                CATEGORY: {rec['category'].upper()}
            </div>
            <div class="rec-item-desc">
                {rec['details']}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# VIEW 5: INTERACTIVE WHAT-IF SIMULATOR
# ==========================================
elif app_mode == "🔮 What-If Simulator":
    st.subheader("🔮 Interventions Simulator (What-If Scenario)")
    st.markdown("Test how targeted academic interventions (e.g., increasing attendance or study hours) impact a student's predicted risk level in real-time.")

    sim_student_id = st.selectbox("Select Student to Simulate:", df["student_id"] + " - " + df["name"])
    sid = sim_student_id.split(" - ")[0]
    base_student = df[df["student_id"] == sid].iloc[0]

    original_pred = predict_student_risk(base_student, artifact)

    st.markdown("---")
    sim_col1, sim_col2 = st.columns([1.2, 1.8])

    with sim_col1:
        st.markdown("### 🎛️ Adjust Student Parameters")

        sim_attendance = st.slider(
            "Attendance Rate (%)",
            min_value=40.0, max_value=100.0,
            value=float(base_student["attendance_rate"]), step=1.0
        )

        sim_study_hours = st.slider(
            "Study Hours / Week",
            min_value=2.0, max_value=38.0,
            value=float(base_student["study_hours_per_week"]), step=1.0
        )

        sim_assignment = st.slider(
            "Assignment Completion (%)",
            min_value=40.0, max_value=100.0,
            value=float(base_student["assignment_completion_rate"]), step=1.0
        )

        sim_midterm = st.slider(
            "Midterm Score (%)",
            min_value=35.0, max_value=100.0,
            value=float(base_student["midterm_score"]), step=1.0
        )

        sim_stress = st.slider(
            "Stress Level (1-10)",
            min_value=1, max_value=10,
            value=int(base_student["stress_level"]), step=1
        )

    # Construct simulated student profile
    sim_student = base_student.to_dict()
    sim_student["attendance_rate"] = sim_attendance
    sim_student["study_hours_per_week"] = sim_study_hours
    sim_student["assignment_completion_rate"] = sim_assignment
    sim_student["midterm_score"] = sim_midterm
    sim_student["stress_level"] = sim_stress

    sim_pred = predict_student_risk(sim_student, artifact)

    with sim_col2:
        st.markdown("### 📊 Simulation Results Comparison")

        orig_risk = original_pred["predicted_risk"]
        sim_risk = sim_pred["predicted_risk"]

        orig_color = RISK_COLORS.get(orig_risk, "#10B981")
        sim_color = RISK_COLORS.get(sim_risk, "#10B981")

        res_c1, res_c2 = st.columns(2)
        with res_c1:
            st.markdown(f"""
            <div class="section-glass-container" style="border-top: 4px solid {orig_color}; text-align: center;">
                <div style="font-size: 0.85rem; color: #9CB7A5; font-weight: 700; text-transform: uppercase;">ORIGINAL RISK LEVEL</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: {orig_color}; margin: 0.3rem 0;">{orig_risk.upper()}</div>
                <div style="font-size: 0.9rem; color: #F0FDF4; font-weight: 600;">High Risk Prob: {original_pred['high_risk_prob']}%</div>
            </div>
            """, unsafe_allow_html=True)

        with res_c2:
            st.markdown(f"""
            <div class="section-glass-container" style="border-top: 4px solid {sim_color}; text-align: center;">
                <div style="font-size: 0.85rem; color: #9CB7A5; font-weight: 700; text-transform: uppercase;">SIMULATED RISK LEVEL</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: {sim_color}; margin: 0.3rem 0;">{sim_risk.upper()}</div>
                <div style="font-size: 0.9rem; color: #F0FDF4; font-weight: 600;">High Risk Prob: {sim_pred['high_risk_prob']}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        prob_comp_df = pd.DataFrame([
            {"Scenario": "Original Baseline", "High Risk": original_pred['high_risk_prob'], "Medium Risk": original_pred['medium_risk_prob'], "Low Risk": original_pred['low_risk_prob']},
            {"Scenario": "Simulated Intervention", "High Risk": sim_pred['high_risk_prob'], "Medium Risk": sim_pred['medium_risk_prob'], "Low Risk": sim_pred['low_risk_prob']}
        ])

        fig_prob = px.bar(
            prob_comp_df,
            x="Scenario",
            y=["High Risk", "Medium Risk", "Low Risk"],
            color_discrete_map={"High Risk": "#EF4444", "Medium Risk": "#F59E0B", "Low Risk": "#10B981"},
            title="Risk Probability Distribution Comparison (%)"
        )
        fig_prob.update_layout(barmode="group")
        apply_dark_green_plotly_theme(fig_prob)
        st.plotly_chart(fig_prob, width="stretch")


# ==========================================
# VIEW 6: STUDENT DATA EXPLORER
# ==========================================
elif app_mode == "📁 Student Data Explorer":
    st.subheader("📁 Cohort Student Data Directory")
    st.markdown(f"Displaying **{len(filtered_df)}** records based on active sidebar filters.")

    st.dataframe(
        filtered_df,
        width="stretch",
        hide_index=True
    )

    # Download CSV button (Sanitized against CSV formula injection)
    export_df = filtered_df.copy()
    for col in export_df.select_dtypes(include=['object', 'string']).columns:
        export_df[col] = export_df[col].astype(str).apply(
            lambda x: f"'{x}" if x and x[0] in ('=', '+', '-', '@') else x
        )
    csv_data = export_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Filtered Student Dataset (CSV)",
        data=csv_data,
        file_name="edupulse_student_records.csv",
        mime="text/csv"
    )
