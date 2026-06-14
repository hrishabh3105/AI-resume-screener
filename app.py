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
st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="centered")

# Header
st.markdown("<h1 style='text-align: center;'>📄 AI Resume Screener</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Paste or upload your resume and a job description to see how well you match.</p>", unsafe_allow_html=True)
st.divider()

# Job Description
st.markdown("### 📋 Job Description")
jd = st.text_area("", height=200, placeholder="Paste the job description here...")

# Resume
st.markdown("### 👤 Your Resume")
resume_option = st.radio("Choose input method:", ["Paste Text", "Upload PDF"], horizontal=True)

resume_text = ""

if resume_option == "Paste Text":
    resume_text = st.text_area("", height=200, placeholder="Paste your resume here...")

elif resume_option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload your resume as PDF", type=["pdf"])
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
        st.success("PDF uploaded and extracted successfully.")

st.divider()

import json

def extractKeywords(jd):
    prompt = f"""
    Extract the most important technical skills, tools, frameworks,
    programming languages, certifications, and job-related keywords
    from the following job description.

    Return ONLY a valid JSON list, no extra text.

    Example:
    ["Python", "React", "AWS", "Docker"]

    Job Description:
    {jd}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content.strip()
    try:
        keywords = json.loads(content)
        return keywords
    except:
        return []
    
# def keyword_match_analysis(keywords, resume_text):
#     resume_lower = resume_text.lower()
#     missing=[]
#     matched=[]

#     for keyword in keywords:
#         if keyword.lower() in resume_lower:
#             matched.append(keyword)
#         else:
#             missing.append(keyword)

#     return matched, missing

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
    response= client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    
    try:
        result = json.loads(content)
        return result["matched"], result["missing"]
    except:
        return [], []
    
    

# Button
if st.button("🔍 Screen My Resume", use_container_width=True):
    if not jd or not resume_text:
        st.warning("Please fill in both the job description and your resume.")
    else:
        with st.spinner("Analyzing your resume..."):
            # Main analysis
            prompt = f"""
            You are an expert recruiter and resume screener.
            
            Compare this resume against the job description and give:
            1. A match score out of 100
            2. Top 3 strengths of this resume for this role
            3. Top 3 missing skills or gaps
            4. One specific suggestion to improve the resume for this job
            
            Job Description:
            {jd}
            
            Resume:
            {resume_text}
            """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content

            # Keyword analysis
            keywords = extractKeywords(jd)
            matched, missing = smart_keyword_match(keywords, resume_text)

        st.divider()
        st.markdown("### 📊 Analysis Result")
        st.markdown(result)

        st.divider()
        st.markdown("### 🔑 Keyword Match Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ Matched Keywords")
            if matched:
                for keyword in matched:
                    st.success(keyword)
            else:
                st.info("No keywords matched.")

        with col2:
            st.markdown("#### ❌ Missing Keywords")
            if missing:
                for keyword in missing:
                    st.error(keyword)
            else:
                st.info("No keywords missing. Great match!")