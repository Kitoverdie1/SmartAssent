import streamlit as st
from pathlib import Path
import pandas as pd

# ==============================
# ตั้งค่าหน้าแอป
# ==============================
st.set_page_config(
    page_title="Smart Asset QR – ภาพรวม",
    page_icon="🩺",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"
EXCEL_PATH = BASE_DIR / "Smart Asset Lab.xlsx"

# ชื่อคอลัมน์ใน Excel (แก้ให้ตรงกับไฟล์จริงได้)
COL_NAME = "ชื่อ"
COL_CODE = "รหัสเครื่องมือห้องปฏิบัติการ"
COL_ASSET = "AssetID"
COL_LOC = "สถานที่ใช้งาน (ปัจจุบัน)"
COL_OWNER = "ผู้รับผิดชอบ (ปัจจุบัน)"


# ==============================
# โหลดข้อมูลจาก Excel (cache ไว้)
# ==============================
@st.cache_data
def load_data():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel: {EXCEL_PATH.name}")
    df = pd.read_excel(EXCEL_PATH).dropna(how="all").reset_index(drop=True)
    return df


# ==============================
# เมนูด้านข้าง
# ==============================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🩺 Smart Asset QR")

        # ไม่ใช้ page_link("app.py") แล้ว เพราะทำให้พังบน Cloud
        st.markdown("**📌 ภาพรวม / แสดงจาก QR**")
        st.markdown("---")

        # หน้า Login
        if (PAGES_DIR / "1_Login.py").exists():
            st.page_link(
                "pages/1_Login.py",
                label="🔐 เข้าสู่ระบบ / จัดการข้อมูล",
            )
        else:
            st.caption("⚠️ ไม่พบไฟล์ pages/1_Login.py")

        # หน้า Dashboard สินทรัพย์
        if (PAGES_DIR / "2_Smart_Asset_Dashboard.py").exists():
            st.page_link(
                "pages/2_Smart_Asset_Dashboard.py",
                label="📊 Dashboard ครุภัณฑ์",
            )

        # หน้า QR Assets / ป้าย QR
        if (PAGES_DIR / "3_QR_Assets.py").exists():
            st.page_link(
                "pages/3_QR_Assets.py",
                label="📇 จัดการ QR / ป้าย 3×8",
            )

        st.markdown("---")
        st.caption("📂 โฟลเดอร์: SmartAsset_QR_App_ready")


# ==============================
# แสดงรายละเอียดจาก ?code=
# ==============================
def render_asset_from_query() -> bool:
    """
    ถ้า URL มี ?code=LAB-AS-001 → แสดงรายละเอียดจาก Excel
    ถ้าไม่มี code ให้คืนค่า False เพื่อไปแสดงหน้า overview
    """
    params = st.experimental_get_query_params()
    code = params.get("code", [None])[0]

    if not code:
        # ไม่มี code ใน URL
        return False

    st.markdown("## 📄 รายละเอียดครุภัณฑ์ (จาก QR Code)")
    st.caption(f"รหัสจาก URL: `{code}`")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"อ่านไฟล์ Excel ไม่สำเร็จ: {e}")
        return True

    if COL_CODE not in df.columns:
        st.error(f"ไม่พบคอลัมน์ `{COL_CODE}` ในไฟล์ Excel")
        return True

    # หาแถวที่รหัสตรงกับ code จาก URL
    match = df[df[COL_CODE].astype(str) == str(code)]

    if match.empty:
        st.warning(f"ไม่พบข้อมูลสำหรับรหัส `{code}` ในไฟล์ Excel")
        return True

    row = match.iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("ชื่อ", value=str(row.get(COL_NAME, "")), disabled=True)
        st.text_input("AssetID", value=str(row.get(COL_ASSET, "")), disabled=True)
        st.text_input("รหัสเครื่องมือห้องปฏิบัติการ", value=str(row.get(COL_CODE, "")), disabled=True)

    with col2:
        st.text_input("สถานที่ใช้งาน (ปัจจุบัน)", value=str(row.get(COL_LOC, "")), disabled=True)
        st.text_input("ผู้รับผิดชอบ (ปัจจุบัน)", value=str(row.get(COL_OWNER, "")), disabled=True)

    st.info("หน้านี้คือโหมดอ่านข้อมูลจากการสแกน QR (ถ้าจะแก้ไข ให้ไปหน้า Dashboard/หน้าแก้ไขข้อมูล)")

    st.markdown("---")
    return True


# ==============================
# หน้า “ภาพรวม” ปกติ
# ==============================
def render_overview():
    st.markdown("## ภาพรวมระบบ")

    st.markdown(
        """
- สร้างหน้า **HTML รายครุภัณฑ์** จากไฟล์ Excel  
- ทำ **QR Code** ให้สแกนแล้วไปยังหน้าข้อมูลครุภัณฑ์แต่ละชิ้น  
- มีหน้า **Dashboard** สำหรับค้นหา/พรีวิว/ดาวน์โหลดไฟล์ PNG  
- รองรับการรวมเป็น **ป้าย A4 3×8** สำหรับพิมพ์แปะที่ครุภัณฑ์
        """
    )

    st.info(
        "ถ้าต้องการทดสอบสแกน QR ให้ใช้ลิงก์รูปแบบ: "
        "`https://<subdomain>.streamlit.app/?code=LAB-AS-001` "
        "โดยเปลี่ยน `code` ให้ตรงกับรหัสเครื่องมือใน Excel"
    )


# ==============================
# main
# ==============================
def main():
    render_sidebar()

    # ถ้า URL มี ?code=... ให้แสดงรายละเอียดจาก Excel
    shown = render_asset_from_query()

    # ถ้าไม่มี ?code= หรือแสดงไม่ได้ → แสดงหน้า overview แทน
    if not shown:
        render_overview()


if __name__ == "__main__":
    main()
