from hashlib import sha256
from io import BytesIO

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw
from rapidocr import RapidOCR

st.set_page_config(page_title="Image OCR", layout="wide")
st.title("Image Text Extractor")
st.write("Upload an image to recognize its text, review confidence scores, and download the results.")


@st.cache_resource
def load_ocr_engine():
    return RapidOCR()


uploaded_file = st.file_uploader(
    "Choose an image",
    type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
)

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    file_digest = sha256(image_bytes).hexdigest()

    if st.session_state.get("file_digest") != file_digest:
        st.session_state.file_digest = file_digest
        st.session_state.ocr_rows = None

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    st.image(image, caption=uploaded_file.name, use_container_width=True)

    if st.button("Extract text"):
        with st.spinner("Reading text from the image..."):
            result = load_ocr_engine()(image)
            boxes = result.boxes.tolist() if result.boxes is not None else []
            texts = result.txts or []
            scores = result.scores or []
            st.session_state.ocr_rows = [
                {"Text": text, "Confidence": float(score), "Box": box}
                for text, score, box in zip(texts, scores, boxes)
            ]

    rows = st.session_state.get("ocr_rows")
    if rows is not None:
        if not rows:
            st.warning("No text was detected. Try an image with clearer or larger text.")
        else:
            min_confidence = st.slider(
                "Minimum confidence",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
            )
            visible_rows = [row for row in rows if row["Confidence"] >= min_confidence]
            extracted_text = "\n".join(row["Text"] for row in visible_rows)

            st.subheader("Extracted text")
            st.text_area("Edit or copy the recognized text", extracted_text, height=220)

            left, right = st.columns(2)
            with left:
                st.write("Recognized lines")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"Text": row["Text"], "Confidence": round(row["Confidence"], 3)}
                            for row in visible_rows
                        ]
                    ),
                    hide_index=True,
                    use_container_width=True,
                )

            with right:
                annotated_image = image.copy()
                draw = ImageDraw.Draw(annotated_image)
                for row in visible_rows:
                    points = [tuple(map(int, point)) for point in row["Box"]]
                    draw.polygon(points, outline="lime", width=3)
                st.write("Detected text locations")
                st.image(annotated_image, use_container_width=True)

            st.download_button(
                "Download text file",
                data=extracted_text,
                file_name="recognized_text.txt",
                mime="text/plain",
            )
            st.download_button(
                "Download results as CSV",
                data=pd.DataFrame(
                    [
                        {"Text": row["Text"], "Confidence": row["Confidence"]}
                        for row in visible_rows
                    ]
                ).to_csv(index=False),
                file_name="recognized_text.csv",
                mime="text/csv",
            )
else:
    st.info("Supported formats: PNG, JPG, JPEG, BMP, TIF, and TIFF.")
