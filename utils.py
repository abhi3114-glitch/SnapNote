from PIL import Image
import os
import tempfile

def save_to_pdf(image_array, output_path="output.pdf"):
    """
    Converts a numpy image array (BGR) to a PDF file using reportlab.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    
    # Convert BGR (OpenCV) to RGB (Pillow)
    rgb_image = image_array[:, :, ::-1]  # BGR to RGB
    pil_image = Image.fromarray(rgb_image)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        pil_image.save(tmp_file.name, quality=95)
        tmp_path = tmp_file.name

    # Create PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    page_width, page_height = A4
    
    # Calculate image dimensions to fit page with margins
    margin = 28  # ~10mm in points
    max_width = page_width - 2 * margin
    max_height = page_height - 2 * margin
    
    img_width, img_height = pil_image.size
    
    # Scale to fit
    scale = min(max_width / img_width, max_height / img_height)
    draw_width = img_width * scale
    draw_height = img_height * scale
    
    # Center on page
    x = (page_width - draw_width) / 2
    y = page_height - margin - draw_height
    
    c.drawImage(tmp_path, x, y, width=draw_width, height=draw_height)
    c.save()

    # Cleanup
    try:
        os.remove(tmp_path)
    except:
        pass

    return output_path
