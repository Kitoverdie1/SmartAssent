# pages/2_Smart_Asset_Dashboard.py

import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# การตั้งค่าไฟล์หลัก
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent  # โฟลเดอร์ SmartAsset_QR_App_ready
EXCEL_PATH = BASE_DIR / "Smart Asset Lab.xlsx"
QRCODE_DIR = BASE_DIR / "qrcodes"                 # โฟลเดอร์เก็บรูป QR (.png)

st.set_page_config(page_title="Smart Asset Dashboard", page_icon="📊", layout="wide")

st.markdown("## 📊 Dashboard ครุภัณฑ์ & แบบฟอร์มแก้ไขข้อมูล")

# =========================
# โหลดข้อมูลจาก Excel
# =========================
if not EXCEL_PATH.exists():
    st.error(f"ไม่พบไฟล์ Excel: {EXCEL_PATH.name}")
    st.stop()

df = pd.read_excel(EXCEL_PATH).dropna(how="all").reset_index(drop=True)

# คอลัมน์ที่ใช้หลัก ๆ
COL_NAME = "ชื่อ"
COL_CODE = "รหัสเครื่องมือห้องปฏิบัติการ"
COL_ASSET = "AssetID"
COL_LOC = "สถานที่ใช้งาน (ปัจจุบัน)"
COL_OWNER = "ผู้รับผิดชอบ (ปัจจุบัน)"

# =========================
# ตารางข้อมูลทั้งหมด
# =========================
with st.expander("📋 ตารางข้อมูลครุภัณฑ์ทั้งหมด", expanded=True):
    search = st.text_input("🔍 ค้นหาจากชื่อ / รหัส / AssetID", "")
    if search:
        mask = (
            df[COL_NAME].astype(str).str.contains(search, case=False, na=False) |
            df[COL_CODE].astype(str).str.contains(search, case=False, na=False) |
            df[COL_ASSET].astype(str).str.contains(search, case=False, na=False)
        )
        st.dataframe(df[mask], use_container_width=True, height=300)
    else:
        st.dataframe(df, use_container_width=True, height=300)

# =========================
# เลือกอุปกรณ์สำหรับแก้ไข
# =========================
st.markdown("### เลือกอุปกรณ์เพื่อแก้ไข")

if df.empty:
    st.warning("ยังไม่มีข้อมูลในไฟล์ Excel")
    st.stop()

# list ให้เลือก: "LAB-AS-001 - ชื่ออุปกรณ์"
options = [
    f"{row[COL_CODE]} - {row[COL_NAME]}"
    for _, row in df.iterrows()
]

selected = st.selectbox("เลือกจากรหัส/ชื่อ", options)

# หา index ของแถวที่เลือก
selected_code = selected.split(" - ")[0]
row_idx = df[df[COL_CODE] == selected_code].index[0]
row = df.loc[row_idx]

# =========================
# ฟอร์มแก้ไขข้อมูล
# =========================
st.markdown("### 📝 แบบฟอร์มแก้ไขข้อมูล")

with st.form("edit_form"):
    col1, col2 = st.columns(2)

    with col1:
        new_name = st.text_input("ชื่อ", value=str(row.get(COL_NAME, "")))
        new_asset = st.text_input("AssetID", value=str(row.get(COL_ASSET, "")))
        new_code = st.text_input("รหัสเครื่องมือห้องปฏิบัติการ", value=str(row.get(COL_CODE, "")))

    with col2:
        new_loc = st.text_input("สถานที่ใช้งาน (ปัจจุบัน)", value=str(row.get(COL_LOC, "")))
        new_owner = st.text_input("ผู้รับผิดชอบ (ปัจจุบัน)", value=str(row.get(COL_OWNER, "")))

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

if submitted:
    # อัปเดตค่าลง DataFrame
    df.at[row_idx, COL_NAME] = new_name
    df.at[row_idx, COL_ASSET] = new_asset
    df.at[row_idx, COL_CODE] = new_code
    df.at[row_idx, COL_LOC] = new_loc
    df.at[row_idx, COL_OWNER] = new_owner

    # เขียนกลับลง Excel (เขียนทั้งชีต)
    try:
        df.to_excel(EXCEL_PATH, index=False)
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว ✅")
    except Exception as e:
        st.error(f"บันทึกไม่สำเร็จ: {e}")

# ใช้ code ล่าสุด (เผื่อผู้ใช้แก้ในฟอร์ม)
current_code = new_code if submitted else str(row.get(COL_CODE, ""))

# =========================
# 🔗 ส่วนแสดง QR ที่ใช้แสดงข้อมูล
# =========================
st.markdown("---")
st.markdown("### 📇 QR Code ที่ใช้ในการแสดงข้อมูล")

qr_path = QRCODE_DIR / f"{current_code}.png"

col_qr, col_info = st.columns([1, 2])

with col_qr:
    if qr_path.exists():
        st.image(str(qr_path), caption=f"QR ของรหัส {current_code}", use_column_width=True)
    else:
        st.warning(f"ไม่พบไฟล์ QR: {qr_path.name} ในโฟลเดอร์ qrcodes")

with col_info:
    st.markdown("#### 🔗 ลิงก์สำหรับสแกนดูข้อมูลครุภัณฑ์")

    # 👉 TODO: เปลี่ยน BASE_URL เป็น URL จริงหลังจาก deploy
    BASE_URL = "https://gpqgy3cvkjoblhckidqhaf.streamlit.app/"  # แก้เป็น URL ที่ใช้จริง
    detail_url = f"{BASE_URL}/?code={current_code}"

    st.code(detail_url, language="text")
    st.caption(
        "เวลาสร้าง QR ใหม่ สามารถใช้ลิงก์นี้เป็นเนื้อหาใน QR ได้ "
        "(เปลี่ยน BASE_URL ให้ตรงกับ URL ของระบบที่ deploy จริง)"
    )
