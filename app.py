from flask import Flask, request, jsonify
from pypdf import PdfReader
from docx import Document
import google.generativeai as genai
import os

app = Flask(__name__)

# ===== CONFIG =====
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ===== TEXT EXTRACTION =====
def extract_pdf_to_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_docx_to_text(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

# ===== PROMPTS =====
SYSTEM_PROMPT = """
You are a deterministic text-structuring assistant.
Do NOT interpret or add meaning.
"""

TASK_TEMPLATE = """
From the BRD text below, consolidate dependent fragments
into auditable requirements.
Output JSON only.

BRD TEXT:
{brd_text}
"""

# ===== API =====
@app.route("/structure", methods=["POST"])
def structure():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    if file.filename.endswith(".pdf"):
        text = extract_pdf_to_text(file)
    elif file.filename.endswith(".docx"):
        text = extract_docx_to_text(file)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    prompt = TASK_TEMPLATE.format(brd_text=text)

    response = model.generate_content(
        contents=[
            {"role": "system", "parts": [SYSTEM_PROMPT]},
            {"role": "user", "parts": [prompt]}
        ]
    )

    return jsonify({"result": response.text})

if __name__ == "__main__":
    app.run(port=8000)
