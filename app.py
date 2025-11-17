import streamlit as st
import pandas as pd
from pathlib import Path

# ==============================
# 1) ตั้งค่าและตัวแปรพื้นฐาน
# ==============================
st.set_page_config(
    page_title="Smart Asset QR – Detail from Excel",
    page_icon="🩺",
    layout="wide",
)

# โฟลเดอร์โปรเจ็กต์เดียวกับ app.py
BASE_DIR = Path(__file__).resolve().parent

# ไฟล์ Excel หลัก
EXCEL_PATH = BASE_DIR / "Smart Asset Lab.xlsx"

# ชื่อคอลัมน์สำคัญใน Excel (ต้องตรงกับหัวคอลัมน์จริง)
COL_CODE = "รหัสเครื่องมือห้องปฏิบัติการ"  # ใช้เป็น key จาก QR
COL_IMAGE = "รูปภาพ"                         # เก็บ path รูปภาพ

# โฟลเดอร์ที่จะเก็บรูปภาพที่อัปโหลดใหม่
IMAGE_FOLDER = BASE_DIR / "asset_images"


# ==============================
# 2) ฟังก์ชันโหลด / เซฟ Excel
# ==============================
@st.cache_data
def load_data() -> pd.DataFrame:
    """อ่านข้อมูลจาก Excel แล้วคืนค่า DataFrame"""
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel: {EXCEL_PATH.name}")
    df = pd.read_excel(EXCEL_PATH).dropna(how="all").reset_index(drop=True)
    return df


def save_data(df: pd.DataFrame):
    """บันทึก DataFrame กลับไปที่ Excel และเคลียร์ cache"""
    df.to_excel(EXCEL_PATH, index=False)
    load_data.clear()


# ==============================
# 3) หน้าแสดงข้อมูลจาก code ใน URL
# ==============================
def render_asset_from_query() -> bool:
    """
    ถ้า URL มี ?code=LAB-AS-001 → แสดงและแก้ไขข้อมูลจาก Excel
    กดบันทึกแล้วจะเขียนทับแถวเดิมใน Excel
    """
    # 3.1 อ่านค่า code จาก URL (?code=XXXX)
    params = st.experimental_get_query_params()
    code = params.get("code", [None])[0]

    if not code:
        # ถ้าไม่มี code เลย แสดงว่าไม่ได้มาจาก QR → ให้ main ไปทำหน้าอื่นแทน
        return False

    st.markdown("## ข้อมูลจาก Google Sheet / Excel")
    st.caption(f"รหัสจาก URL: `{code}`")

    # 3.2 โหลดข้อมูลทั้งหมดจากไฟล์ Excel
    try:
        df = load_data()
    except Exception as e:
        st.error(f"อ่านไฟล์ Excel ไม่สำเร็จ: {e}")
        return True

    # 3.3 ตรวจว่ามีคอลัมน์รหัสที่ใช้หา row จริงไหม
    if COL_CODE not in df.columns:
        st.error(f"ไม่พบคอลัมน์ `{COL_CODE}` ในไฟล์ Excel")
        return True

    # 3.4 หาแถวที่รหัสตรงกับ code
    match_idx = df[df[COL_CODE].astype(str) == str(code)].index
    if len(match_idx) == 0:
        st.warning(f"ไม่พบข้อมูลสำหรับรหัส `{code}` ในไฟล์ Excel")
        return True

    row_idx = match_idx[0]   # index ของแถวเป้าหมาย
    row = df.loc[row_idx]    # Series ของข้อมูลในแถวนั้น

    # -----------------------------
    # 4) สร้างฟอร์มให้แก้ไขทุกคอลัมน์
    # -----------------------------
    col_names = list(df.columns)
    new_values = {}            # เก็บค่าที่แก้ไขจากฟอร์ม
    uploaded_image_file = None # เก็บไฟล์รูปใหม่ (ถ้ามีอัปโหลด)

    with st.form("edit_from_qr"):
        for i in range(0, len(col_names), 2):
            c1, c2 = st.columns(2)

            # ===== ช่องซ้าย =====
            col_name1 = col_names[i]
            val1 = row.get(col_name1, "")
            if pd.isna(val1):
                val1 = ""

            with c1:
                if col_name1 == COL_IMAGE:
                    # ช่องรูปภาพ: text + preview + uploader
                    new_values[col_name1] = st.text_input(
                        str(col_name1),
                        value=str(val1),
                        key=f"txt_{col_name1}_left",
                    )

                    # แสดงรูปเดิม ถ้า path ไม่ว่างและไฟล์อยู่จริง
                    if str(val1).strip():
                        img_path = BASE_DIR / str(val1)
                        if img_path.exists():
                            st.image(
                                str(img_path),
                                caption="รูปภาพปัจจุบัน",
                                use_container_width=True,
                            )

                    uploaded = st.file_uploader(
                        "อัปโหลดรูปภาพใหม่",
                        type=["png", "jpg", "jpeg"],
                        key="upload_image_left",
                    )
                    if uploaded is not None:
                        uploaded_image_file = uploaded
                        st.image(
                            uploaded,
                            caption="รูปที่อัปโหลด (ยังไม่บันทึก)",
                            use_container_width=True,
                        )
                        st.caption("รูปใหม่จะถูกบันทึกเมื่อกดปุ่ม 'บันทึกข้อมูล'")
                else:
                    new_values[col_name1] = st.text_input(
                        str(col_name1),
                        value=str(val1),
                        key=f"txt_{col_name1}_left",
                    )

            # ===== ช่องขวา =====
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
                                st.image(
                                    str(img_path),
                                    caption="รูปภาพปัจจุบัน",
                                    use_container_width=True,
                                )

                        uploaded = st.file_uploader(
                            "อัปโหลดรูปภาพใหม่",
                            type=["png", "jpg", "jpeg"],
                            key="upload_image_right",
                        )
                        if uploaded is not None:
                            uploaded_image_file = uploaded
                            st.image(
                                uploaded,
                                caption="รูปที่อัปโหลด (ยังไม่บันทึก)",
                                use_container_width=True,
                            )
                            st.caption("รูปใหม่จะถูกบันทึกเมื่อกดปุ่ม 'บันทึกข้อมูล'")
                    else:
                        new_values[col_name2] = st.text_input(
                            str(col_name2),
                            value=str(val2),
                            key=f"txt_{col_name2}_right",
                        )

        submitted = st.form_submit_button("💾 บันทึกข้อมูล")

    # -----------------------------
    # 5) เมื่อกดบันทึก → เขียนกลับ Excel
    # -----------------------------
    if submitted:
        try:
            # 5.1 ถ้ามีอัปโหลดรูปใหม่ → เซฟไฟล์ + แก้ path ในคอลัมน์รูปภาพ
            if uploaded_image_file is not None:
                IMAGE_FOLDER.mkdir(exist_ok=True)
                suffix = Path(uploaded_image_file.name).suffix.lower()
                if suffix not in [".png", ".jpg", ".jpeg"]:
                    suffix = ".png"
                img_filename = f"{code}{suffix}"
                save_path = IMAGE_FOLDER / img_filename

                with open(save_path, "wb") as f:
                    f.write(uploaded_image_file.getbuffer())

                # เก็บ path แบบ relative ลงใน Excel เช่น asset_images/LAB-AS-001.png
                rel_path = save_path.relative_to(BASE_DIR)
                new_values[COL_IMAGE] = str(rel_path)

            # 5.2 อัปเดตค่าใน DataFrame ทุกคอลัมน์ของแถวนี้
            for col_name, val in new_values.items():
                df.at[row_idx, col_name] = val

            # 5.3 บันทึกกลับไปเป็นไฟล์ Excel
            save_data(df)

            st.success("บันทึกข้อมูลลง Excel เรียบร้อยแล้ว ✅")
        except Exception as e:
            st.error(f"บันทึกไม่สำเร็จ: {e}")

    st.markdown(
        "> หน้านี้อ่านข้อมูลจาก `Smart Asset Lab.xlsx` ตามรหัสจาก QR "
        "สามารถแก้ไขทุกช่อง และเมื่อกด 'บันทึกข้อมูล' จะเขียนทับแถวเดิมในไฟล์ Excel "
        "(รวมถึง path รูปภาพถ้ามีอัปโหลดใหม่ด้วย)"
    )

    return True


# ==============================
# 4) หน้าอื่น (กรณีไม่มี code ใน URL)
# ==============================
def render_overview():
    st.markdown("## ภาพรวม Smart Asset QR")
    st.write(
        """
- สแกน QR → เปิดหน้านี้ด้วย `?code=รหัสเครื่องมือห้องปฏิบัติการ`
- หน้าแสดงข้อมูลจาก Excel และแก้ไขได้
- กดบันทึกแล้วข้อมูลในไฟล์ Excel จะถูกอัปเดตทันที
        """
    )
    st.info("ลองเรียก URL แบบ `...?code=LAB-AS-001` ดูเพื่อทดสอบ")


# ==============================
# 5) main
# ==============================
def main():
    # ถ้ามี code ใน URL → แสดงหน้าแก้ไขจาก QR
    shown = render_asset_from_query()
    # ถ้าไม่มี code → แสดงหน้า overview
    if not shown:
        render_overview()


if __name__ == "__main__":
    main()
