# AI Resume Screener

An AI-powered resume screening tool that analyzes how well your resume matches a job description — with smart keyword matching, match scoring, and actionable feedback.

---

## Live Demo

> Run locally using the steps below.

---

## What It Does

- **Match Score** — gives your resume a score out of 100 for the specific job
- **Strength Analysis** — identifies your top strengths for the role
- **Gap Analysis** — highlights missing skills and experience
- **Smart Keyword Matching** — detects keywords even when written as abbreviations or synonyms (e.g. JS = JavaScript, ML = Machine Learning)
- **Keyword Match Meter** — visual percentage breakdown of matched vs missing keywords
- **PDF Upload** — upload your resume as a PDF or paste it as text
- **Actionable Suggestion** — one specific thing you can do to improve your resume for that role

---

## Built With

- **Python** — core language
- **Streamlit** — frontend UI
- **Groq API** — LLM inference (llama-3.3-70b-versatile)
- **PyPDF2** — PDF text extraction
- **python-dotenv** — secure environment variable management

---

## Project Structure

```
resume-screener/
│
├── app.py          # Main application
├── .env            # API keys (not uploaded to GitHub)
├── .gitignore      # Ignores .env and venv
└── requirements.txt
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/hrishabh3105/AI-resume-screener.git
cd AI-resume-screener
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Create a `.env` file in the root folder:
```
GROQ_API_KEY=your-groq-api-key-here
```

Get your free API key at: https://console.groq.com

### 5. Run the app
```bash
streamlit run app.py
```

---

## Security Practices

- API keys stored in `.env` file, never hardcoded
- `.env` excluded from version control via `.gitignore`
- Virtual environment dependencies isolated per project

---

## How It Works

1. User pastes a job description and their resume (text or PDF)
2. App sends both to Groq's LLaMA model with a structured prompt
3. AI returns a match score, strengths, gaps, and suggestions
4. A second prompt extracts keywords from the JD
5. A third prompt matches those keywords against the resume using synonym awareness
6. Results are displayed with visual score meters and keyword pills

---

## What I Learned Building This

- How to integrate LLM APIs into a real application
- Prompt engineering for structured and consistent AI output
- Handling PDF parsing and file uploads in Python
- Secure API key management with environment variables
- Building and iterating on a project using Git version control

---

## Future Improvements

- Rebuild frontend in React for a more polished UI
- Add support for multiple resume formats (DOCX)
- Store analysis history per user
- Add a cover letter generator based on JD and resume
- Deploy on cloud (Render / Railway)

---

## Author

**Hrishabh Mishra**  
[GitHub](https://github.com/hrishabh3105) • [LinkedIn](https://www.linkedin.com/in/hrishabh-mishra-a0bb7115a/)
