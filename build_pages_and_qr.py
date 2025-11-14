#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build per-asset QR codes linking directly to Streamlit Cloud page:
https://gpqgy3cvkjoblhckidqhaf.streamlit.app/qr_detail?code=<asset_id>

Input: Smart Asset Lab.xlsx
Output:
  - SmartAsset_QR_Pages/qrcodes/<slug>.png
  - SmartAsset_QR_Pages/pages/<slug>.html
  - SmartAsset_QR_Pages/qr_labels_A4_pages.pdf
"""

import os, re, html, sys
import pandas as pd
from pathlib import Path
import qrcode
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

# -----------------------------
# SETTINGS
# -----------------------------
EXCEL_PATH = "Smart Asset Lab.xlsx"
OUT = Path("SmartAsset_QR_Pages")
PAGES = OUT / "pages"
QRPNG = OUT / "qrcodes"

# ❗ Streamlit Cloud URL ที่คุณให้มา
STREAMLIT_BASE = "https://gpqgy3cvkjoblhckidqhaf.streamlit.app/qr_detail?code="


# -----------------------------
# HELPERS
# -----------------------------
def pick_id(row):
    """เลือก Asset ID ที่ดีที่สุด"""
    keys = [
        "รหัสเครื่องมือห้องปฏิบัติการ", "AssetID", "รหัสครุภัณฑ์",
        "รหัส", "Code", "ID", "Asset Id", "Asset_ID"
    ]
    for k in keys:
        if k in row and pd.notna(row[k]) and str(row[k]).strip():
            return str(row[k]).strip()
    return f"ROW-{int(row.name) + 1}"


def slugify(s):
    s = str(s or "").strip()
    s = re.sub(r"[^\w\-]+", "-", s, flags=re.UNICODE)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "item"


def render_page(title, rows):
    """สร้าง HTML แบบ Bootstrap (เฉพาะดู ไม่แก้ไข)"""
    form_rows = ""
    for label, val in rows:
        sval = "" if pd.isna(val) else str(val)
        sval = html.escape(sval)
        form_rows += f"""
        <div class="mb-3 row">
            <label class="col-sm-3 col-form-label fw-semibold">{html.escape(str(label))}</label>
            <div class="col-sm-9">
                <input type="text" class="form-control" value="{sval}" readonly>
            </div>
        </div>"""

    return f"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{{background:#f8fafc}}
.card{{max-width:880px;margin:32px auto;border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.06)}}
.card-header{{background:#0d6efd;color:white;border-top-left-radius:16px;border-top-right-radius:16px}}
</style>
</head>
<body>
<div class="card">
    <div class="card-header">
        <h4 class="m-0">ข้อมูลเครื่องมือห้องปฏิบัติการ</h4>
    </div>
    <div class="card-body">
        {form_rows}
        <div class="mt-4 text-center text-muted">© Smart Asset — QR Detail Page</div>
    </div>
</div>
</body>
</html>"""


# -----------------------------
# MAIN
# -----------------------------
def main():
    if not Path(EXCEL_PATH).exists():
        print("[ERROR] ไม่พบไฟล์ Excel:", EXCEL_PATH)
        sys.exit(1)

    OUT.mkdir(exist_ok=True)
    PAGES.mkdir(exist_ok=True)
    QRPNG.mkdir(exist_ok=True)

    df = pd.read_excel(EXCEL_PATH).dropna(how="all").reset_index(drop=True)

    prefer = [
        "ลำดับ","ชื่อ","รหัสเครื่องมือห้องปฏิบัติการ","AssetID","ปี","ยี่ห้อ","โมเดล",
        "หมายเลขเครื่อง","ต้นทุนต่อหน่วย","สถานะ","สถานที่ใช้งาน (ปัจจุบัน)",
        "ผู้รับผิดชอบ (ปัจจุบัน)","รูปภาพ","QR Code"
    ]

    records = []

    used_slugs = set()

    for _, row in df.iterrows():
        asset_id = pick_id(row)
        slug = slugify(asset_id)

        if slug in used_slugs:
            i = 2
            while f"{slug}-{i}" in used_slugs:
                i += 1
            slug = f"{slug}-{i}"
        used_slugs.add(slug)

        rows_kv = []
        used = set()
        for k in prefer:
            if k in row:
                rows_kv.append((k, row[k])); used.add(k)
        for k in row.index:
            if k not in used:
                rows_kv.append((k, row[k]))

        html_str = render_page(asset_id, rows_kv)
        html_file = PAGES / f"{slug}.html"
        html_file.write_text(html_str, encoding="utf-8")

        # --------------------------
        # สร้าง URL สำหรับ QR → ชี้ไป Streamlit Cloud
        # --------------------------
        page_url = f"{STREAMLIT_BASE}{asset_id}"

        # --------------------------
        # สร้าง QR
        # --------------------------
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )
        qr.add_data(page_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img.save(QRPNG / f"{slug}.png", "PNG")

        records.append((asset_id, slug, page_url))

    # --------------------------
    # สร้าง PDF แนว A4 3x8
    # --------------------------
    c = canvas.Canvas(str(OUT / "qr_labels_A4_pages.pdf"), pagesize=A4)
    page_w, page_h = A4

    left, right, top, bottom = 10*mm, 10*mm, 12*mm, 12*mm
    cols, rows = 3, 8

    cell_w = (page_w - left - right) / cols
    cell_h = (page_h - top - bottom) / rows

    pngs = sorted(QRPNG.glob("*.png"))

    for i, png in enumerate(pngs):
        if i and i % (cols * rows) == 0:
            c.showPage()
        pos = i % (cols * rows)
        r = pos // cols
        col = pos % cols

        x0 = left + col * cell_w
        y0 = page_h - top - (r+1)*cell_h

        im = Image.open(png)
        iw, ih = im.size
        target_w, target_h = 42*mm, 52*mm

        aspect = iw / ih
        w = target_w
        h = w / aspect
        if h > target_h:
            h = target_h
            w = h * aspect

        x = x0 + (cell_w - w) / 2
        y = y0 + (cell_h - h) / 2

        c.drawImage(ImageReader(im), x, y, width=w, height=h)

    c.save()

    print("\n✨ สร้าง QR และ HTML สำเร็จแล้ว!")
    print("📁 โฟลเดอร์:", OUT.as_posix())
    print("🟦 Streamlit URL ตัวอย่าง:")
    print("    ", STREAMLIT_BASE + "<asset_id>")


if __name__ == "__main__":
    main()
