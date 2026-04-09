"""
🛡️ AI Job Fraud Detector — FINAL FULL BODY HUMAN ANIMATION VERSION
Run: streamlit run app.py
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

# ---------------- LOTTIE LOADER ----------------
def load_lottie(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def show_lottie(anim, height=320):
    if anim:
        st_lottie(anim, height=height)
    else:
        st.warning("⚠️ Animation not loaded")

# ---------------- FULL BODY HUMAN ANIMATIONS ----------------

# 👩‍🏭 Working full-body (LIKE YOUR IMAGE STYLE)
loading_lottie = load_lottie(
    "https://assets10.lottiefiles.com/packages/lf20_kkflmtur.json"
)

# 🎉 Full-body success human
valid_lottie = load_lottie(
    "https://assets10.lottiefiles.com/packages/lf20_touohxv0.json"
)

# 😞 Full-body confused human
invalid_lottie = load_lottie(
    "https://assets10.lottiefiles.com/packages/lf20_urbk83vw.json"
)

# 🔥 NEW: No Website Found / Invalid Website Animation
no_website_lottie = load_lottie(
    "https://assets4.lottiefiles.com/packages/lf20_yf9k6v3t.json"   # You can change this URL
)

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

# ---------------- HELPERS ----------------
def normalize_url(url):
    if url.startswith("www."):
        return "https://" + url
    return url

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ---------------- SCRAPER ----------------
def fetch_job(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.title.string if soup.title else "Unknown Job"
        desc = " ".join([p.get_text() for p in soup.find_all("p")[:5]])

        return JobDetails(title, desc, True)
    except:
        return JobDetails("", "", False)

# ---------------- FRAUD DETECTION ----------------
def detect_fraud(details):
    text = (details.title + details.description).lower()

    suspicious_words = [
        "earn money fast", "no experience", "whatsapp",
        "pay fee", "investment", "urgent hiring"
    ]

    score = 0

    for word in suspicious_words:
        if word in text:
            score += 20

    if len(details.description) < 100:
        score += 20

    is_fraud = score > 40
    confidence = max(10, 100 - score)

    return DetectionResult(
        is_fraud,
        confidence,
        "❌ FRAUD JOB" if is_fraud else "✅ LEGIT JOB"
    )

# ---------------- UI ----------------
st.set_page_config(page_title="AI Job Fraud Detector", layout="wide")

st.title("🛡️ AI Job Fraud Detector")
st.write("Detect whether a job posting is **Real or Fake**")

url = st.text_input("🔗 Enter Job URL")

if st.button("🚀 Analyze Job"):

    if not url:
        st.error("❌ Enter a URL")
        st.stop()

    url = normalize_url(url)

    # 🔄 FULL BODY LOADING ANIMATION
    with st.spinner("Analyzing job..."):
        show_lottie(loading_lottie)
        time.sleep(2)

    # ❌ INVALID URL
    if not is_valid_url(url):
        show_lottie(no_website_lottie)        # ← NEW ANIMATION HERE
        st.error("❌ Invalid URL")
        st.stop()

    # Fetch job
    job = fetch_job(url)

    if not job.fetch_success:
        show_lottie(no_website_lottie)        # ← NEW ANIMATION HERE
        st.error("❌ Unable to fetch job details (No website found)")
        st.stop()

    # Detect fraud
    result = detect_fraud(job)

    col1, col2 = st.columns(2)

    # 🎯 ANIMATION OUTPUT
    with col1:
        if result.is_fraud:
            show_lottie(invalid_lottie)
        else:
            show_lottie(valid_lottie)

    # 🎯 RESULT OUTPUT
    with col2:
        if result.is_fraud:
            st.error(result.verdict)
        else:
            st.success(result.verdict)

        st.subheader(f"Confidence: {result.confidence}%")
        st.progress(result.confidence)

    # Save history
    c.execute("INSERT INTO history VALUES (?, ?, ?, ?)",
              (url, result.verdict, result.confidence,
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# ---------------- HISTORY ----------------
st.markdown("---")
st.subheader("📋 History")

rows = c.execute("SELECT * FROM history ORDER BY rowid DESC LIMIT 5").fetchall()

if rows:
    df = pd.DataFrame(rows, columns=["URL", "Verdict", "Confidence", "Time"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No history yet")