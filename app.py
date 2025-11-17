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

# ชื่อคอลัมน์หลักที่ใช้ค้นหา (รหัสเครื่องมือห้องปฏิบัติการ)
COL_CODE = "รหัสเครื่องมือห้องปฏิบัติการ"


# ==============================
# โหลดข้อมูลจาก Excel (cache ไว้ แต่เคลียร์เมื่อบันทึก)
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

        # หน้า app เอง (ไม่ใช้ page_link เพราะเคยทำให้พังบน Cloud)
        st.markdown("**📌 ภาพรวม / แสดงจาก QR**")
        st.markdown("---")

        # หน้า Login
        if (PAGES_DIR / "1_Login.py").exists():
            st.page_link(
                "pages/1_Login.py",
                label="Login",
            )

        # หน้า Dashboard สินทรัพย์
        if (PAGES_DIR / "2_Smart_Asset_Dashboard.py").exists():
            st.page_link(
                "pages/2_Smart_Asset_Dashboard.py",
                label="Smart Asset Dashboard",
            )

        # หน้า QR Assets / ป้าย QR
        if (PAGES_DIR / "3_QR_Assets.py").exists():
            st.page_link(
                "pages/3_QR_Assets.py",
                label="QR Assets",
            )

        st.markdown("---")
        st.caption("📂 โฟลเดอร์: SmartAsset_QR_App_ready")


# ==============================
# แสดง + แก้ไขรายละเอียดจาก ?code=
# ==============================
def render_asset_from_query() -> bool:
    """
    ถ้า URL มี ?code=LAB-AS-001 → แสดงรายละเอียดจาก Excel
    ให้แก้ไขข้อมูลทุกคอลัมน์ได้ แล้วบันทึกกลับลง Excel
    ถ้าไม่มี code ให้คืนค่า False เพื่อไปแสดงหน้า overview
    """
    params = st.experimental_get_query_params()
    code = params.get("code", [None])[0]

    if not code:
        # ไม่มี code ใน URL
        return False

    st.markdown("## 📄 รายละเอียดครุภัณฑ์ (จาก QR Code)")
    st.caption(f"รหัสจาก URL: `{code}`")

    # โหลดข้อมูลทั้งหมด
    try:
        df = load_data()
    except Exception as e:
        st.error(f"อ่านไฟล์ Excel ไม่สำเร็จ: {e}")
        return True

    if COL_CODE not in df.columns:
        st.error(f"ไม่พบคอลัมน์ `{COL_CODE}` ในไฟล์ Excel")
        return True

    # หา row ที่ตรงกับ code
    match_idx = df[df[COL_CODE].astype(str) == str(code)].index
    if len(match_idx) == 0:
        st.warning(f"ไม่พบข้อมูลสำหรับรหัส `{code}` ในไฟล์ Excel")
        return True

    row_idx = match_idx[0]
    row = df.loc[row_idx]

    st.markdown("### ข้อมูลจาก Google Sheet / Excel")

    col_names = list(df.columns)
    new_values = {}

    # ใช้ form เพื่อให้มีปุ่มบันทึก
    with st.form("edit_from_qr"):
        for i in range(0, len(col_names), 2):
            c1, c2 = st.columns(2)

            # ช่องซ้าย
            col_name1 = col_names[i]
            val1 = row.get(col_name1, "")
            # แปลง NaN เป็นสตริงว่าง
            if pd.isna(val1):
                val1 = ""
            with c1:
                new_values[col_name1] = st.text_input(
                    str(col_name1),
                    value=str(val1)
                )

            # ช่องขวา (ถ้ามีคอลัมน์คู่)
            if i + 1 < len(col_names):
                col_name2 = col_names[i + 1]
                val2 = row.get(col_name2, "")
                if pd.isna(val2):
                    val2 = ""
                with c2:
                    new_values[col_name2] = st.text_input(
                        str(col_name2),
                        value=str(val2)
                    )

        submitted = st.form_submit_button("💾 บันทึกข้อมูล")

    # ถ้ากดบันทึก → อัปเดต DataFrame แล้วเขียนกลับลง Excel
    if submitted:
        try:
            for col_name, val in new_values.items():
                df.at[row_idx, col_name] = val

            df.to_excel(EXCEL_PATH, index=False)

            # เคลียร์ cache แล้วโหลดใหม่ให้ข้อมูลอัปเดตทันที
            load_data.clear()
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว ✅")
        except Exception as e:
            st.error(f"บันทึกไม่สำเร็จ: {e}")

    st.info(
        "หน้านี้อ่านข้อมูลจากการสแกน QR โดยดึงทุกคอลัมน์จากแถวใน Google Sheet/Excel "
        "และสามารถแก้ไขแล้วบันทึกกลับได้ หากต้องการดูภาพรวมหลายรายการให้ใช้หน้า Smart Asset Dashboard แทน"
    )

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

    # ถ้า URL มี ?code=... ให้แสดง + แก้ไขรายละเอียดจาก Excel
    shown = render_asset_from_query()

    # ถ้าไม่มี ?code= หรือแสดงไม่ได้ → แสดงหน้า overview แทน
    if not shown:
        render_overview()


if __name__ == "__main__":
    main()
