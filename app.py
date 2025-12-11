import streamlit as st
import cv2
import numpy as np
import processor
import utils
import os

st.set_page_config(page_title="SnapNote", page_icon="📝", layout="wide")

st.title("📝 SnapNote - Clean Note Generator")
st.markdown("Upload a photo of your notes, and we'll clean it up for you!")
st.caption("v2.0 - Auto-Crop OFF by default")

# Sidebar
st.sidebar.header("Settings")
input_method = st.sidebar.radio("Input Method", ["Upload Image", "Camera"])
enhance_mode = st.sidebar.selectbox("Enhancement Mode", ["Original", "Grayscale", "Scan", "High Contrast"], index=2)
if enhance_mode == "Scan":
    st.sidebar.info("Scan mode uses adaptive thresholding to create a clean black & white look.")

# processing inputs
# Only show perspective toggle if we are not in simple generic modes if needed, but keeping it always on is fine
use_perspective = st.sidebar.checkbox("Auto-Crop & Deskew", value=False, help="Enable to auto-detect document edges. Works best with photos of documents on contrasting backgrounds.")


def load_image(uploaded_file):
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    return image

image = None

if input_method == "Upload Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = load_image(uploaded_file)
else:
    camera_file = st.camera_input("Take a picture")
    if camera_file is not None:
        image = load_image(camera_file)

if image is not None:
    # Process first, before setting up columns
    processed_image = None
    error_msg = None
    
    try:
        processed_image = processor.process_image(image, use_perspective=use_perspective, enhance_mode=enhance_mode)
    except Exception as e:
        import traceback
        error_msg = f"Error: {e}\n{traceback.format_exc()}"
    
    # Creating columns for side-by-side comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original")
        # Convert BGR to RGB for Streamlit display
        original_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        st.image(original_rgb)

    with col2:
        st.subheader("Processed")
        if error_msg:
            st.error(error_msg)
            st.error("Try disabling 'Auto-Crop & Deskew' if the image is too complex.")
        elif processed_image is not None:
            # Debug info
            st.caption(f"Size: {processed_image.shape}")
            # Convert for display
            if len(processed_image.shape) == 2:
                display_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2RGB)
            else:
                display_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            st.image(display_image)
        else:
            st.error("Processing returned no result.")
                
    # Export Options
    if processed_image is not None:
        st.divider()
        st.subheader("Export")
        
        # Convert to PDF
        if st.button("Generate PDF"):
            pdf_path = "processed_note.pdf"
            # Need to convert back to color for PDF function if it is grayscale single channel
            if len(processed_image.shape) == 2:
                processed_image_color = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
            else:
                processed_image_color = processed_image
                
            utils.save_to_pdf(processed_image_color, pdf_path)
            
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name="snapnote_export.pdf",
                    mime="application/pdf"
                )
            st.success("PDF Generated!")

else:
    st.info("Please upload an image or take a photo to start.")

st.markdown("---")
st.text("Built with Streamlit & OpenCV")

