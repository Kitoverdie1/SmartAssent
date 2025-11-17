import streamlit as st
from pathlib import Path
import pandas as pd

# ==============================
# ตั้งค่าหน้าแอป + Sidebar เริ่มต้นพับเก็บ
# ==============================
st.set_page_config(
    page_title="Smart Asset QR – MEM System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"
EXCEL_PATH = BASE_DIR / "Smart Asset Lab.xlsx"

# คอลัมน์หลัก
COL_CODE = "รหัสเครื่องมือห้องปฏิบัติการ"
COL_IMAGE = "รูปภาพ"  # คอลัมน์เก็บ path รูปภาพ
IMAGE_FOLDER = BASE_DIR / "asset_images"  # โฟลเดอร์เก็บรูปใหม่ที่อัปโหลด


# ==============================
# 1) ระบบ Login แบบง่าย
# ==============================
VALID_USERS = {
    "admin": "1234",
    "staff001": "pass001",
    "staff002": "pass002",
}

def check_login(username: str, password: str) -> bool:
    if not username or not password:
        return False
    return VALID_USERS.get(username) == password

LOGIN_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #0b486b, #0f6480);
        color: #f9fafb;
    }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }

    .mem-login-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem 3rem 1rem;
    }
    .mem-login-inner {
        max-width: 460px;
        width: 100%;
        text-align: center;
    }
    .mem-icon-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        font-size: 40px;
        background: rgba(255,255,255,0.08);
    }
    .mem-title h1 {
        font-size: 2.4rem;
        margin: 0 0 .25rem 0;
        font-weight: 600;
        color: #f9fafb;
    }
    .mem-title h3 {
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.9;
        margin: 0;
    }
    .mem-card {
        margin-top: 2.5rem;
        background: rgba(255,255,255,0.98);
        border-radius: 18px;
        box-shadow:
            0 18px 45px rgba(0,0,0,0.45),
            0 0 0 1px rgba(255,255,255,0.25);
        padding: 2rem 2.5rem 1.75rem 2.5rem;
        text-align: left;
    }
    .mem-card-title {
        text-align: center;
        font-size: 1.25rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1.2rem;
    }
    .mem-input > div > input {
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
        background: #f9fafb !important;
        height: 44px;
        padding-left: 2.3rem !important;
        font-size: 0.95rem;
    }
    .mem-input label { display: none !important; }
    .mem-icon-left {
        position: absolute;
        left: 14px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.9rem;
        color: #9ca3af;
    }
    .mem-btn-login button {
        width: 100%;
        border-radius: 12px;
        height: 46px;
        font-size: 1rem;
        font-weight: 500;
        border: none;
        background: #e5e7eb;
        color: #111827;
        margin-top: 0.9rem;
    }
    .mem-btn-login button:hover {
        background: #d1d5db;
    }
    .mem-helper {
        margin-top: 0.75rem;
        font-size: 0.8rem;
        color: #6b7280;
        text-align: center;
    }
</style>
"""

def render_login_page():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    if "login_error" not in st.session_state:
        st.session_state.login_error = ""

    st.markdown('<div class="mem-login-wrapper"><div class="mem-login-inner">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="mem-title">
            <div class="mem-icon-circle">📋</div>
            <h1>MEM System</h1>
            <h3>Medical Equipment Management System</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mem-card">', unsafe_allow_html=True)
    st.markdown('<div class="mem-card-title">เข้าสู่ระบบ</div>', unsafe_allow_html=True)

    # ฟอร์ม Login
    st.markdown(
        '<div style="position:relative;" class="mem-input">'
        '<span class="mem-icon-left">👤</span>',
        unsafe_allow_html=True,
    )
    username = st.text_input(
        "",
        placeholder="Username or staff code",
        label_visibility="collapsed",
        key="login_username_main",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="position:relative; margin-top:0.6rem;" class="mem-input">'
        '<span class="mem-icon-left">🔒</span>',
        unsafe_allow_html=True,
    )
    password = st.text_input(
        "",
        type="password",
        placeholder="Password",
        label_visibility="collapsed",
        key="login_password_main",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="mem-btn-login">', unsafe_allow_html=True)
    btn_clicked = st.button("Login")
    st.markdown("</div>", unsafe_allow_html=True)

    if btn_clicked:
        if check_login(username.strip(), password.strip()):
            st.session_state.logged_in = True
            st.session_state.login_user = username.strip()
            st.session_state.login_error = ""
            st.experimental_rerun()
        else:
            st.session_state.logged_in = False
            st.session_state.login_user = ""
            st.session_state.login_error = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"

    if st.session_state.get("login_error"):
        st.error(st.session_state.login_error)
    elif st.session_state.get("logged_in"):
        st.success(f"เข้าสู่ระบบแล้วในชื่อ: {st.session_state.login_user}")

    st.markdown(
        '<div class="mem-helper">หากลืมรหัสผ่าน กรุณาติดต่อผู้ดูแลระบบ</div>',
        unsafe_allow_html=True,
    )

    st.markdown("</div></div>", unsafe_allow_html=True)


def logout():
    st.session_state.logged_in = False
    st.session_state.login_user = ""
    st.experimental_rerun()


# ==============================
# 2) ส่วนระบบ Smart Asset เดิม (QR / แก้ไข / รูปภาพ)
# ==============================
@st.cache_data
def load_data():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel: {EXCEL_PATH.name}")
    df = pd.read_excel(EXCEL_PATH).dropna(how="all").reset_index(drop=True)
    return df


def render_sidebar():
    with st.sidebar:
        st.markdown("### 🩺 Smart Asset QR")
        st.markdown(f"👤 ผู้ใช้: **{st.session_state.get('login_user','-')}**")
        if st.button("ออกจากระบบ"):
            logout()

        st.markdown("---")
        st.markdown("**📌 ภาพรวม / แสดงจาก QR**")

        if (PAGES_DIR / "2_Smart_Asset_Dashboard.py").exists():
            st.page_link(
                "pages/2_Smart_Asset_Dashboard.py",
                label="Smart Asset Dashboard",
            )
        if (PAGES_DIR / "3_QR_Assets.py").exists():
            st.page_link(
                "pages/3_QR_Assets.py",
                label="QR Assets",
            )

        st.markdown("---")
        st.caption("📂 โฟลเดอร์: SmartAsset_QR_App_ready")


def render_asset_from_query() -> bool:
    params = st.experimental_get_query_params()
    code = params.get("code", [None])[0]

    if not code:
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

    match_idx = df[df[COL_CODE].astype(str) == str(code)].index
    if len(match_idx) == 0:
        st.warning(f"ไม่พบข้อมูลสำหรับรหัส `{code}` ในไฟล์ Excel")
        return True

    row_idx = match_idx[0]
    row = df.loc[row_idx]

    st.markdown("### ข้อมูลจาก Google Sheet / Excel")

    col_names = list(df.columns)
    new_values = {}
    uploaded_image_file = None

    with st.form("edit_from_qr"):
        for i in range(0, len(col_names), 2):
            c1, c2 = st.columns(2)

            col_name1 = col_names[i]
            val1 = row.get(col_name1, "")
            if pd.isna(val1):
                val1 = ""

            with c1:
                if col_name1 == COL_IMAGE:
                    new_values[col_name1] = st.text_input(
                        str(col_name1),
                        value=str(val1),
                        key=f"txt_{col_name1}_left",
                    )
                    if str(val1).strip():
                        img_path = BASE_DIR / str(val1)
                        if img_path.exists():
                            st.image(str(img_path), caption="รูปภาพปัจจุบัน", use_container_width=True)

                    uploaded = st.file_uploader(
                        "อัปโหลดรูปภาพใหม่",
                        type=["png", "jpg", "jpeg"],
                        key="upload_image_left",
                    )
                    if uploaded is not None:
                        uploaded_image_file = uploaded
                        st.image(uploaded, caption="รูปที่อัปโหลด (ยังไม่บันทึก)", use_container_width=True)
                        st.caption("รูปใหม่จะถูกบันทึกเมื่อกดปุ่ม 'บันทึกข้อมูล'")
                else:
                    new_values[col_name1] = st.text_input(
                        str(col_name1),
                        value=str(val1),
                        key=f"txt_{col_name1}_left",
                    )

            if i + 1 < len(col_names):
                col_name2 = col_names[i + 1]
                val2 = row.get(col_name2, "")
                if pd.isna(val2):
                    val2 = ""

                with c2:
                    if col_name2 == COL_IMAGE:
                        new_values[col_name2] = st.text_input(
                            str(col_name2),
                            value=str(val2),
                            key=f"txt_{col_name2}_right",
                        )
                        if str(val2).strip():
                            img_path = BASE_DIR / str(val2)
                            if img_path.exists():
                                st.image(str(img_path), caption="รูปภาพปัจจุบัน", use_container_width=True)

                        uploaded = st.file_uploader(
                            "อัปโหลดรูปภาพใหม่",
                            type=["png", "jpg", "jpeg"],
                            key="upload_image_right",
                        )
                        if uploaded is not None:
                            uploaded_image_file = uploaded
                            st.image(uploaded, caption="รูปที่อัปโหลด (ยังไม่บันทึก)", use_container_width=True)
                            st.caption("รูปใหม่จะถูกบันทึกเมื่อกดปุ่ม 'บันทึกข้อมูล'")
                    else:
                        new_values[col_name2] = st.text_input(
                            str(col_name2),
                            value=str(val2),
                            key=f"txt_{col_name2}_right",
                        )

        submitted = st.form_submit_button("💾 บันทึกข้อมูล")

    if submitted:
        try:
            if uploaded_image_file is not None:
                IMAGE_FOLDER.mkdir(exist_ok=True)
                suffix = Path(uploaded_image_file.name).suffix.lower()
                if suffix not in [".png", ".jpg", ".jpeg"]:
                    suffix = ".png"
                img_filename = f"{code}{suffix}"
                save_path = IMAGE_FOLDER / img_filename

                with open(save_path, "wb") as f:
                    f.write(uploaded_image_file.getbuffer())

                rel_path = save_path.relative_to(BASE_DIR)
                new_values[COL_IMAGE] = str(rel_path)

            for col_name, val in new_values.items():
                df.at[row_idx, col_name] = val

            df.to_excel(EXCEL_PATH, index=False)
            load_data.clear()
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว ✅")
        except Exception as e:
            st.error(f"บันทึกไม่สำเร็จ: {e}")

    st.info(
        "หน้านี้อ่านข้อมูลจากการสแกน QR โดยดึงทุกคอลัมน์จากแถวใน Google Sheet/Excel "
        "สามารถแก้ไขข้อมูลได้ทุกช่อง และอัปโหลดรูปใหม่ให้แสดงแทนรูปเดิมได้"
    )
    st.markdown("---")
    return True


def render_overview():
    st.markdown("## ภาพรวมระบบ Smart Asset QR / MEM System")
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
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.login_user = ""

    # ถ้ายังไม่ login → แสดงหน้า Login เต็มจอ
    if not st.session_state.logged_in:
        render_login_page()
        return

    # ถ้า login แล้ว → แสดงระบบ Smart Asset ตามเดิม
    render_sidebar()
    shown = render_asset_from_query()
    if not shown:
        render_overview()


if __name__ == "__main__":
    main()
