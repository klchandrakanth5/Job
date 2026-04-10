"""
🛡️ AI Job Fraud Detector — PHOENIX DARK THEME + FIXED ANIMATION
"""

import time
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dataclasses import dataclass
import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_lottie import st_lottie
import plotly.express as px
import plotly.graph_objects as go

# ---------------- DATABASE ----------------
conn = sqlite3.connect("history.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS history (
    url TEXT,
    verdict TEXT,
    confidence REAL,
    timestamp TEXT
)
""")
conn.commit()

# ---------------- SAFE LOTTIE LOADER ----------------
def load_lottie(url):
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def show_lottie(anim, height=300, key=None):
    if anim:
        st_lottie(anim, height=height, key=key, speed=1)
    else:
        st.markdown("**🎨 Animation unavailable** (using placeholder)")

# ---------------- ANIMATIONS ----------------
loading_lottie = load_lottie("https://assets10.lottiefiles.com/packages/lf20_kkflmtur.json")
valid_lottie = load_lottie("https://assets10.lottiefiles.com/packages/lf20_touohxv0.json")
invalid_lottie = load_lottie("https://assets10.lottiefiles.com/packages/lf20_urbk83vw.json")
no_website_lottie = load_lottie("https://assets4.lottiefiles.com/packages/lf20_yf9k6v3t.json")

# NEW BETTER ANIMATION (Person with Box - close to your image)
box_person_lottie = load_lottie("https://assets-v2.lottiefiles.com/a/5610ffc6-116d-11ee-ad75-ff744d0c017e/wjksYTNp2d.lottie")  # Direct from LottieFiles

# ✅ NEW: 404 / URL Not Found Animation (from LottieFiles CDN)
# Primary: classic 404 error animation — falls back to secondary if unavailable
url_not_found_lottie = load_lottie("https://assets9.lottiefiles.com/packages/lf20_kcsr6fts.json")
if not url_not_found_lottie:
    url_not_found_lottie = load_lottie("https://assets4.lottiefiles.com/packages/lf20_qp1q7mct.json")
if not url_not_found_lottie:
    url_not_found_lottie = load_lottie("https://assets10.lottiefiles.com/packages/lf20_tpa93wkm.json")

# ---------------- DATA MODELS ----------------
@dataclass
class JobDetails:
    title: str
    description: str
    fetch_success: bool

@dataclass
class DetectionResult:
    is_fraud: bool
    confidence: float
    verdict: str
    real_prob: float
    fake_prob: float

# ---------------- HELPERS ----------------
def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        return "https://" + url.lstrip("www.")
    return url

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ---------------- SCRAPER & DETECTION (Unchanged) ----------------
def fetch_job(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, timeout=10, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "Unknown Job Title"
        paragraphs = soup.find_all("p")
        desc = " ".join([p.get_text().strip() for p in paragraphs[:8] if p.get_text().strip()])
        if not desc:
            desc = "No detailed description available."
        return JobDetails(title, desc, True)
    except Exception:
        return JobDetails("", "", False)

def detect_fraud(details: JobDetails) -> DetectionResult:
    text = (details.title + " " + details.description).lower()
    suspicious_words = [
        "earn money fast", "no experience needed", "whatsapp", "pay fee",
        "investment required", "urgent hiring", "work from home immediate",
        "guaranteed salary", "no qualification", "send cv to email"
    ]
    score = sum(25 for word in suspicious_words if word in text)
    if len(details.description) < 150:
        score += 15
    fake_prob = min(98, score * 1.8)
    real_prob = 100 - fake_prob
    is_fraud = fake_prob > 55
    verdict = "❌ FRAUD JOB" if is_fraud else "✅ LEGIT JOB"
    return DetectionResult(
        is_fraud=is_fraud,
        confidence=max(15, 100 - score),
        verdict=verdict,
        real_prob=round(real_prob, 1),
        fake_prob=round(fake_prob, 1)
    )

# ---------------- THEME (Clean Dark + Orange) ----------------
st.set_page_config(page_title="AI Job Fraud Detector", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a0a0a; color: #e0e0e0; }
    .main .block-container {
        background: #111111;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #ff9800;
    }
    h1, h2, h3 { color: #ff9800 !important; }
    .stTextInput > div > div > input {
        background-color: #1f1f1f;
        color: white;
        border: 2px solid #ff9800;
        border-radius: 8px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #ff9800, #f57c00);
        color: black;
        font-weight: bold;
        border-radius: 8px;
    }
    .stMetric { background: #1a1a1a; border: 1px solid #ff9800; border-radius: 12px; }
    .stAlert { border-radius: 8px; }
    section[data-testid="stSidebar"] { background: #0f0f0f; border-right: 1px solid #ff9800; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ Job Fraud Detector")
    st.markdown("**Phoenix Dark Theme**")

st.markdown("<h1 style='text-align: center; color: #ff9800;'>🛡️ AI Job Fraud Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #bbbbbb;'>Advanced Job Posting Authenticity Analysis</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Dashboard", "📋 Analysis History"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input("🔗 Enter Job Posting URL", placeholder="https://www.naukri.com/job-listings-...")
    with col2:
        analyze_btn = st.button("🚀 Analyze Job", type="primary", use_container_width=True)

    if analyze_btn:
        if not url:
            st.error("❌ Please enter a job URL")
            st.stop()

        url = normalize_url(url)

        with st.spinner("Fetching & Analyzing..."):
            show_lottie(loading_lottie, height=260, key="loading")
            time.sleep(1.6)

        if not is_valid_url(url):
            # ✅ Show 404 / URL Not Found animation here
            show_lottie(url_not_found_lottie, height=300, key="url_not_found_anim")
            st.error("❌ Invalid URL format")
            st.stop()

        job = fetch_job(url)
        if not job.fetch_success:
            # ✅ Also show 404 animation when website is unreachable / not found
            show_lottie(url_not_found_lottie, height=300, key="fetch_failed_anim")
            st.error("❌ Could not fetch job details. The website may be down or blocking access.")
            st.stop()

        result = detect_fraud(job)
        conf_value = result.fake_prob if result.is_fraud else result.real_prob

        st.success("✅ Analysis Complete")

        # KPI Cards
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Job Status", "FAKE" if result.is_fraud else "REAL")
            if result.is_fraud:
                st.error(f"**Fake Job ❌ ({result.fake_prob}%)**")
            else:
                st.success(f"**Real Job ✅ ({result.real_prob}%)**")

        with k2:
            st.metric("Confidence Score", f"{conf_value}%")

        with k3:
            st.metric("Analysis Time", datetime.now().strftime("%H:%M:%S"))

        # Charts
        c1, c2 = st.columns([2, 1])
        with c1:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=conf_value,
                title={"text": "Authenticity Confidence", "font": {"color": "#ff9800"}},
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#22c55e" if not result.is_fraud else "#ef4444"}}
            ))
            gauge.update_layout(height=380, paper_bgcolor="#111111", font={"color": "white"})
            st.plotly_chart(gauge, use_container_width=True)

        with c2:
            pie_df = pd.DataFrame({"Category": ["Real", "Fake"], "Probability": [result.real_prob, result.fake_prob]})
            pie = px.pie(pie_df, names="Category", values="Probability",
                         color_discrete_map={"Real": "#22c55e", "Fake": "#ef4444"}, hole=0.6,
                         title="Real vs Fake Probability")
            pie.update_layout(height=380, paper_bgcolor="#111111", font={"color": "white"})
            st.plotly_chart(pie, use_container_width=True)

        # Animation Section with New Box Animation
        col_a, col_b = st.columns([1, 2])
        with col_a:
            if result.is_fraud:
                show_lottie(invalid_lottie, height=280, key="fraud_anim")
            else:
                show_lottie(valid_lottie, height=280, key="valid_anim")
            
            st.markdown("**📦 Job Illustration**")
            show_lottie(box_person_lottie, height=280, key="box_person_anim")   # <-- Your new animation

        with col_b:
            st.subheader("📋 Job Details")
            st.write(f"**Title:** {job.title}")
            st.write(f"**URL:** {url}")
            with st.expander("Full Description"):
                st.write(job.description)
            st.subheader("🔍 Reasoning")
            if result.is_fraud:
                st.error("High risk indicators detected (suspicious keywords / short description)")
            else:
                st.success("No major red flags found. Appears legitimate.")

        # Save history
        c.execute("INSERT INTO history VALUES (?, ?, ?, ?)",
                  (url, result.verdict, conf_value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

with tab2:
    st.subheader("📋 All Analysis History")
    rows = c.execute("SELECT * FROM history ORDER BY rowid DESC").fetchall()
    if rows:
        df = pd.DataFrame(rows, columns=["URL", "Verdict", "Confidence", "Timestamp"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No analyses yet. Go to Dashboard and analyze a job.")

st.caption("💡 Phoenix Dark Theme | Rule-based AI Job Fraud Detector")