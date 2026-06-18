import streamlit as st


APP_TITLE = "AI Data Insight Assistant"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Data Insight Assistant")

st.write(
    "A safe, explainable assistant for exploring CSV datasets "
    "and generating business insights."
)

st.success("Milestone 1 setup is working successfully.")

st.caption(
    "CSV uploads, dataset profiling, charts, and AI analysis "
    "will be added in future milestones."
)