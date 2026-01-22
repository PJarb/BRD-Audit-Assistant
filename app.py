import streamlit as st
import pandas as pd

from pypdf import PdfReader
from docx import Document

import google.generativeai as genai


# =========================
# 🔐 CONFIG
# =========================
st.set_page_config(
    page_title="BRD Audit Assistant",
    layout="wide"
)

st.title("📄 BRD Audit Assistant")
st.caption("Deterministic Requirement Structuring (No Interpretation)")


# =========================
# 🔑 API KEY
# =========================
gemini_api_key = st.secrets.get("gemini_api_key", None)

if not GEMINI_API_KEY:
    st.error("❌ gemini_api_key not found in Streamlit secrets")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash"
)


# =========================
# 📄 TEXT EXTRACTION (NO AI)
# =========================
def extract_pdf_to_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def extract_docx_to_text(file):
    doc = Document(file)
    return "\n".join(
        [p.text for p in doc.paragraphs if p.text.strip()]
    )


# =========================
# 🔒 PROMPTS (DETERMINISTIC)
# =========================
SYSTEM_PROMPT = """
You are a deterministic text-structuring assistant.

You are NOT a business analyst.
You are NOT allowed to interpret, infer, summarize, or add meaning.

STRICT RULES:
1. Do NOT add new words that do not appear in the source text.
2. Do NOT infer user intent or system behavior.
3. Do NOT generalize meanings.
4. Do NOT resolve ambiguity.
5. Every output must be traceable to the source text.

Allowed operations only:
- grouping
- reordering
- concatenation of dependent fragments
"""

TASK_PROMPT_TEMPLATE = """
Task:
From the provided BRD text, consolidate dependent fragments
into self-contained, auditable requirements.

Definition of dependency (STRICT):
1. Sequential steps within the same flow
2. Condition or outcome of another fragment
3. Same data object reference (e.g., OTP, Category, Receipt)

Rules:
- A requirement must be understandable without referencing other requirements.
- Do NOT merge fragments from different user roles.
- Do NOT merge fragments from different sessions.
- Use ONLY words that appear in the source text.
- Output JSON only.

Output format:
[
  {
    "requirement_id": "REQ-XXX",
    "session": "Registration | Upload Receipt | Redeem Reward | Profile | Other",
    "source_texts": [
      "exact copied fragment text"
    ],
    "requirement_text": "consolidated requirement using only source words"
  }
]

BRD TEXT:
----------------
{brd_text}
----------------
"""


# =========================
# 📂 UI: FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "Upload BRD file (PDF or DOCX)",
    type=["pdf", "docx"]
)

raw_text = None

if uploaded_file:
    if uploaded_file.name.lower().endswith(".pdf"):
        raw_text = extract_pdf_to_text(uploaded_file)
    elif uploaded_file.name.lower().endswith(".docx"):
        raw_text = extract_docx_to_text(uploaded_file)

    st.subheader("🔎 Extracted Raw Text (Preview)")
    st.text_area(
        "Raw text extracted from document (no AI)",
        raw_text[:3000],
        height=300
    )


# =========================
# 🤖 LLM STRUCTURING
# =========================
if raw_text and st.button("🚀 Structure Requirements (Deterministic)"):
    with st.spinner("Structuring requirements with strict rules..."):
        task_prompt = TASK_PROMPT_TE_
