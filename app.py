import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import zipfile

st.set_page_config(layout="wide")
st.title("🤖 CertiFyAI - Smart Certificate Generator")

# Load template
st.markdown("## 📄 Step 1: Upload Certificate Template (PNG/JPG)")
template_file = st.file_uploader("Choose certificate template", type=["png", "jpg", "jpeg"])
if template_file:
    template_img = Image.open(template_file)
    st.image(template_img, caption="Template Preview", use_column_width=True)

    # Load Excel or CSV
    st.markdown("## 📊 Step 2: Upload Winner Data (Excel/CSV)")
    data_file = st.file_uploader("Choose Excel or CSV file", type=["xlsx", "csv"])
    if data_file:
        df = pd.read_excel(data_file) if data_file.name.endswith(".xlsx") else pd.read_csv(data_file)
        st.success(f"File loaded successfully with {len(df)} rows.")
        st.write("Detected Columns:", list(df.columns))

        st.markdown("## 🧩 Step 3: Configure Fields")

        field_settings = []
        for column in df.columns:
            with st.expander(f"⚙️ Settings for `{column}`"):
                x = st.number_input(f"X Position for `{column}`", min_value=0, max_value=2000, value=600, key=f"x_{column}")
                y = st.number_input(f"Y Position for `{column}`", min_value=0, max_value=2000, value=400, key=f"y_{column}")
                font_size = st.slider(f"Font Size for `{column}`", 10, 100, 36, key=f"fs_{column}")
                font_color = st.color_picker(f"Font Color for `{column}`", "#000000", key=f"fc_{column}")
                field_settings.append({
                    "column": column,
                    "x": x,
                    "y": y,
                    "font_size": font_size,
                    "font_color": font_color
                })

        # Font load (fallback to default if arial not found)
        try:
            font_path = "arial.ttf"
            ImageFont.truetype(font_path, 20)
        except:
            font_path = None
            st.warning("⚠️ 'arial.ttf' not found. Using default font.")

        def generate_certificate(row):
            cert = template_img.copy()
            draw = ImageDraw.Draw(cert)
            for field in field_settings:
                text = str(row.get(field["column"], "")).strip()
                font = ImageFont.truetype(font_path, field["font_size"]) if font_path else ImageFont.load_default()
                text_width = draw.textbbox((0, 0), text, font=font)[2]
                draw.text((field["x"] - text_width // 2, field["y"]), text, font=font, fill=field["font_color"])
            return cert

        # Preview
        st.markdown("## 🔍 Step 4: Preview")
        if st.button("Show Preview (First Entry)"):
            preview_cert = generate_certificate(df.iloc[0])
            st.image(preview_cert, caption="📄 Certificate Preview", use_column_width=True)

        # Generate ZIP
        st.markdown("## 🚀 Step 5: Generate All Certificates")
        if st.button("Generate and Download ZIP"):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
                for idx, row in df.iterrows():
                    cert_img = generate_certificate(row)
                    buffer = BytesIO()
                    cert_img.save(buffer, format="PDF")
                    buffer.seek(0)
                    filename = f"certificate_{idx+1}.pdf"
                    zipf.writestr(filename, buffer.read())

            st.success("✅ All certificates generated!")
            st.download_button("📥 Download Certificates ZIP", data=zip_buffer.getvalue(), file_name="certificates.zip", mime="application/zip")

