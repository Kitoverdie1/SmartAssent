import streamlit as st
from auth import login_form, is_authed

st.set_page_config(page_title="Login", page_icon="🔐", layout="wide")

if is_authed():
    st.success("คุณเข้าสู่ระบบแล้ว ✔")
    st.page_link("pages/2_Smart_Asset_Dashboard.py",
                 label="ไปหน้า Dashboard ➜", icon="📊")
else:
    st.header("🔐 เข้าสู่ระบบ")
    login_form()
