import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import PyPDF2
import io
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Page config
st.set_page_config(page_title="AI Resume Screener", page_icon="", layout="centered")

# Custom CSS
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: #a0aec0;
        font-size: 1.1rem;
    }
    
    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Section labels */
    .section-label {
        font-size: 1rem;
        font-weight: 600;
        color: #667eea;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    /* Score meter container */
    .score-container {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin: 1rem 0;
    }
    .score-number {
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
    }
    .score-label {
        font-size: 1rem;
        color: #a0aec0;
        margin-top: 0.5rem;
    }
    
    /* Keyword pills */
    .keyword-matched {
        display: inline-block;
        background: rgba(72, 187, 120, 0.15);
        color: #68d391;
        border: 1px solid rgba(72, 187, 120, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .keyword-missing {
        display: inline-block;
        background: rgba(245, 101, 101, 0.15);
        color: #fc8181;
        border: 1px solid rgba(245, 101, 101, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Meter bar */
    .meter-bar-bg {
        background: rgba(255,255,255,0.1);
        border-radius: 50px;
        height: 14px;
        width: 100%;
        margin: 1rem 0;
        overflow: hidden;
    }

    /* Text areas and inputs */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    /* Button */
    .stButton button {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .stButton button:hover {
        opacity: 0.9 !important;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>AI Resume Screener</h1>
    <p>Find out how well your resume matches any job description</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Job Description
st.markdown('<p class="section-label">Job Description</p>', unsafe_allow_html=True)
jd = st.text_area("", height=180, placeholder="Paste the job description here...", key="jd")

# Resume
st.markdown('<p class="section-label"> Your Resume</p>', unsafe_allow_html=True)
resume_option = st.radio("Input method:", ["Paste Text", "Upload PDF"], horizontal=True)

resume_text = ""

if resume_option == "Paste Text":
    resume_text = st.text_area("", height=180, placeholder="Paste your resume here...", key="resume")
elif resume_option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
        st.success("✅ PDF extracted successfully")

st.divider()


# Functions
def extractKeywords(jd):
    prompt = f"""
    Extract the most important technical skills, tools, frameworks,
    programming languages, certifications, and job-related keywords
    from the following job description.
    Return ONLY a valid JSON list, no extra text.
    Example: ["Python", "React", "AWS", "Docker"]
    Job Description: {jd}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(content)
    except:
        return []


def smart_keyword_match(keywords, resume_text):
    prompt = f"""
    You are a keyword matching system. Your ONLY job is to return a JSON object.
    Do NOT explain anything. Do NOT write code. Do NOT add any text.
    ONLY return a valid JSON object and nothing else.
    Check which of these keywords are present in the resume.
    Consider abbreviations and synonyms as matches (e.g. JS = JavaScript, ML = Machine Learning).
    Keywords: {keywords}
    Resume: {resume_text}
    Return ONLY this exact format:
    {{"matched": ["keyword1", "keyword2"], "missing": ["keyword3", "keyword4"]}}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    try:
        result = json.loads(content)
        return result["matched"], result["missing"]
    except:
        return [], []


def get_score_color(score):
    if score >= 75:
        return "#68d391"  # green
    elif score >= 50:
        return "#f6e05e"  # yellow
    else:
        return "#fc8181"  # red


def extract_score(text):
    import re
    match = re.search(r'\b(\d{1,3})\s*(?:/\s*100|out of 100)?', text)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 100:
            return score
    return None


# Button
if st.button("🔍 Screen My Resume", use_container_width=True):
    if not jd or not resume_text:
        st.warning("Please fill in both the job description and your resume.")
    else:
        with st.spinner("Analyzing your resume..."):
            prompt = f"""
            You are an expert recruiter and resume screener.
            Compare this resume against the job description and give:
            1. A match score out of 100 (write it as: Score: X/100)
            2. Top 3 strengths of this resume for this role
            3. Top 3 missing skills or gaps
            4. One specific suggestion to improve the resume for this job
            Job Description: {jd}
            Resume: {resume_text}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

            keywords = extractKeywords(jd)
            matched, missing = smart_keyword_match(keywords, resume_text)

        # Score meter
        score = extract_score(result)
        if score is not None:
            color = get_score_color(score)
            match_pct = len(matched) / len(keywords) * 100 if keywords else 0

            st.markdown(f"""
            <div class="score-container">
                <div class="score-number" style="color: {color};">{score}</div>
                <div class="score-label">Match Score out of 100</div>
                <div class="meter-bar-bg">
                    <div style="height:100%; width:{score}%; background: linear-gradient(90deg, #667eea, {color}); border-radius:50px; transition: width 1s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Analysis
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("Detailed Analysis")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        # Keyword match
        st.markdown("Keyword Match Analysis")

        if keywords:
            match_pct = int(len(matched) / len(keywords) * 100)
            st.markdown(f"""
            <div class="score-container">
                <div class="score-number" style="color: #667eea;">{match_pct}%</div>
                <div class="score-label">Keywords Matched ({len(matched)} of {len(keywords)})</div>
                <div class="meter-bar-bg">
                    <div style="height:100%; width:{match_pct}%; background: linear-gradient(90deg, #667eea, #f093fb); border-radius:50px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("Matched Keywords")
            if matched:
                pills = "".join([f'<span class="keyword-matched">{k}</span>' for k in matched])
                st.markdown(f'<div class="card">{pills}</div>', unsafe_allow_html=True)
            else:
                st.info("No keywords matched.")

        with col2:
            st.markdown("Missing Keywords")
            if missing:
                pills = "".join([f'<span class="keyword-missing">{k}</span>' for k in missing])
                st.markdown(f'<div class="card">{pills}</div>', unsafe_allow_html=True)
            else:
                st.success("No keywords missing!")