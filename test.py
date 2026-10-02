import streamlit as st

st.set_page_config(page_title="HTML Test")

st.markdown("""
<style>
.box {
    background: linear-gradient(135deg, #020617, #2563eb);
    color: white;
    padding: 40px;
    border-radius: 20px;
    font-size: 35px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="box">
    AcademicDoc AI
</div>
""", unsafe_allow_html=True)