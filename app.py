import streamlit as st
import time
import pandas as pd

# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="BRD Analyzer (Mock)",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------
if "step" not in st.session_state:
    st.session_state.step = "empty"

if "results" not in st.session_state:
    st.session_state.results = []

if "file_name" not in st.session_state:
    st.session_state.file_name = None

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("🤖 BRD Analyzer")
    st.caption("Mock Version (No ML / LLM)")

    uploaded_file = st.file_uploader(
        "Upload BRD (PDF / DOCX)",
        type=["pdf", "docx"]
    )

    if uploaded_file:
        st.session_state.file_name = uploaded_file.name
        st.session_state.step = "processing"

    st.divider()
    st.markdown("**Recent Files (Mock)**")
    st.write("- Project_Phoenix_V1.docx")
    st.write("- Legacy_System_Req.pdf")

# -----------------------------
# Empty View
# -----------------------------
if st.session_state.step == "empty":
    st.title("Welcome to BRD Analyzer")
    st.write(
        "Upload a Business Requirement Document to analyze clarity, "
        "detect ambiguity, and generate test cases."
    )

# -----------------------------
# Processing View
# -----------------------------
elif st.session_state.step == "processing":
    st.title(f"Analyzing {st.session_state.file_name}")

    with st.spinner("AI is analyzing the document..."):
        time.sleep(2)  # mock processing
        st.session_state.results = MOCK_REQUIREMENTS
        st.session_state.step = "results"

# -----------------------------
# Results View
# -----------------------------
elif st.session_state.step == "results":

    st.header(st.session_state.file_name)

    # ---- Stats ----
    total = len(st.session_state.results)
    clear = len([r for r in st.session_state.results if r["status"] == "Clear"])
    unclear = total - clear

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Requirements", total)
    col2.metric("Clear", clear)
    col3.metric("Needs Review", unclear)

    st.divider()

    # ---- Filter ----
    tab = st.radio(
        "Filter",
        ["All", "Clear", "Unclear"],
        horizontal=True
    )

    if tab == "Clear":
        data = [r for r in st.session_state.results if r["status"] == "Clear"]
    elif tab == "Unclear":
        data = [r for r in st.session_state.results if r["status"] == "Unclear"]
    else:
        data = st.session_state.results

    # ---- List ----
    for r in data:
        with st.expander(f"ID-{r['id']} | {r['status']} | {r['category']}"):
            st.write(r["text"])

            if r["status"] == "Unclear":
                st.warning(r["issue"])
                st.text_area(
                    "AI Suggestion",
                    r["suggestion"],
                    key=f"suggestion_{r['id']}"
                )

            if r["testCase"]:
                st.subheader("Generated Test Case")
                st.code(r["testCase"], language="gherkin")

    st.divider()

    # ---- Export ----
    df = pd.DataFrame(st.session_state.results)
    st.download_button(
        "⬇ Export CSV",
        df.to_csv(index=False),
        file_name="brd_analysis_mock.csv"
    )
