import streamlit as st
import pandas as pd
import time
import os
import fitz  # PyMuPDF
from docx import Document
import google.generativeai as genai

# ===============================
# Config
# ===============================
st.set_page_config(page_title="BRD Analyzer (Gemini)", layout="wide")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ===============================
# Session State
# ===============================
if "step" not in st.session_state:
    st.session_state.step = "empty"

if "results" not in st.session_state:
    st.session_state.results = []

if "file_name" not in st.session_state:
    st.session_state.file_name = None

# ===============================
# Utils
# ===============================
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def split_requirements(text):
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 20]
    return lines[:10]  # จำกัดไว้ demo

def analyze_with_gemini(requirements):
    prompt = f"""
You are a senior Business Analyst and QA.

For each requirement below:
1. Classify as Clear or Unclear
2. If Unclear, explain the issue
3. Suggest a clearer rewrite
4. If Clear, generate a Gherkin test case

Return JSON array only.

Requirements:
{requirements}
"""
    response = model.generate_content(prompt)
    return response.text

# ===============================
# Sidebar
# ===============================
with st.sidebar:
    st.title("🤖 BRD Analyzer")
    st.caption("PDF / DOCX + Gemini LLM")

    uploaded_file = st.file_uploader(
        "Upload BRD (PDF or DOCX)",
        type=["pdf", "docx"]
    )

    if uploaded_file:
        st.session_state.file_name = uploaded_file.name
        st.session_state.step = "processing"

# ===============================
# Empty View
# ===============================
if st.session_state.step == "empty":
    st.title("Welcome to BRD Analyzer")
    st.write(
        "Upload a BRD document to analyze requirement clarity using Gemini AI."
    )

# ===============================
# Processing View
# ===============================
elif st.session_state.step == "processing":
    st.title(f"Analyzing {st.session_state.file_name}")

    with st.spinner("Extracting text and analyzing with Gemini..."):
        # ---- Extract ----
        if uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        else:
            text = extract_text_from_docx(uploaded_file)

        requirements = split_requirements(text)

        # ---- Gemini ----
        raw_output = analyze_with_gemini(requirements)

        # ---- Parse JSON (simple demo) ----
        try:
            results = eval(raw_output)  # demo only (present ได้)
        except:
            st.error("Gemini output parsing failed")
            st.stop()

        st.session_state.results = results
        st.session_state.step = "results"

# ===============================
# Results View
# ===============================
elif st.session_state.step == "results":

    st.header(st.session_state.file_name)

    df = pd.DataFrame(st.session_state.results)

    # ---- Metrics ----
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", len(df))
    col2.metric("Clear", len(df[df["status"] == "Clear"]))
    col3.metric("Unclear", len(df[df["status"] == "Unclear"]))

    st.divider()

    # ---- Detail ----
    for i, r in df.iterrows():
        with st.expander(f"Requirement {i+1} | {r['status']}"):
            st.write(r["text"])

            if r["status"] == "Unclear":
                st.warning(r["issue"])
                st.text_area(
                    "AI Suggestion",
                    r["suggestion"],
                    key=f"sug_{i}"
                )

            if r.get("testCase"):
                st.subheader("Test Case")
                st.code(r["testCase"], language="gherkin")

    # ---- Export ----
    st.download_button(
        "⬇ Export CSV",
        df.to_csv(index=False),
        file_name="brd_analysis_gemini.csv"
    )
