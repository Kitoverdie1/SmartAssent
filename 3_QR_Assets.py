import streamlit as st
import pandas as pd
import os

EXCEL_PATH = "Smart Asset Lab.xlsx"

st.set_page_config(page_title="QR Assets", page_icon="📁", layout="wide")
st.title("📁 จัดการข้อมูลครุภัณฑ์ (QR Assets)")

# โหลดข้อมูล
@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_PATH).fillna("")
    return df

df = load_data()

# ค้นหา
search = st.text_input("🔍 ค้นหารหัสเครื่องมือ / AssetID / ชื่ออุปกรณ์")
if search:
    results = df[
        df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
    ]
else:
    results = df.copy()

st.dataframe(results, use_container_width=True)

# เลือกอุปกรณ์เพื่อแก้ไข
selected = st.selectbox(
    "เลือกอุปกรณ์เพื่อแก้ไข",
    options=results.index,
    format_func=lambda x: f"{df.at[x, 'รหัสเครื่องมือห้องปฏิบัติการ']} - {df.at[x, 'ชื่อ']}"
)

item = df.loc[selected]

st.subheader("✏️ แบบฟอร์มแก้ไขข้อมูล")
col1, col2 = st.columns(2)

with col1:
    name = st.text_input("ชื่อ", item["ชื่อ"])
    asset_id = st.text_input("AssetID", item["AssetID"])
    code = st.text_input("รหัสเครื่องมือห้องปฏิบัติการ", item["รหัสเครื่องมือห้องปฏิบัติการ"])

with col2:
    location = st.text_input("สถานที่ใช้งาน (ปัจจุบัน)", item["สถานที่ใช้งาน (ปัจจุบัน)"])
    owner = st.text_input("ผู้รับผิดชอบ (ปัจจุบัน)", item["ผู้รับผิดชอบ (ปัจจุบัน)"])

# ปุ่มบันทึก
if st.button("💾 บันทึกข้อมูล"):
    df.at[selected, "ชื่อ"] = name
    df.at[selected, "AssetID"] = asset_id
    df.at[selected, "รหัสเครื่องมือห้องปฏิบัติการ"] = code
    df.at[selected, "สถานที่ใช้งาน (ปัจจุบัน)"] = location
    df.at[selected, "ผู้รับผิดชอบ (ปัจจุบัน)"] = owner

    df.to_excel(EXCEL_PATH, index=False)
    st.success("บันทึกข้อมูลสำเร็จแล้ว 🎉")
