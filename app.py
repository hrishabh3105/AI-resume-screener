import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("AI Resume Screener")
st.write("Paste a Job Description and your Resume below to see how well they match.")

jd = st.text_area("Job Description", height=200, placeholder="Paste the job description here...")
resume = st.text_area("Your Resume", height=200, placeholder="Paste your resume here...")

if st.button("Screen Resume"):
    if not jd or not resume:
        st.warning("Please fill in both fields.")
    else:
        with st.spinner("Analyzing..."):    
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
            {resume}
            """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            st.success("Analysis Complete")
            st.write(response.choices[0].message.content)