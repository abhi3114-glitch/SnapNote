# SnapNote

A document scanning tool that transforms photos of handwritten notes into clean, digitized images. Built with Python, OpenCV, and Streamlit.

## Features

- **Image Upload and Camera Capture**: Accept images via file upload or webcam snapshot
- **Document Detection**: Automatic edge detection and perspective correction (optional)
- **Multiple Enhancement Modes**:
  - Original: No processing
  - Grayscale: Convert to grayscale
  - Scan: Adaptive thresholding for clean black and white output
  - High Contrast: Enhanced contrast for faded documents
- **PDF Export**: Generate single-page PDFs from processed images
- **Real-time Preview**: Side-by-side comparison of original and processed images

## Requirements

- Python 3.11 or 3.12 (Python 3.14 is not yet supported by numpy)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abhi3114-glitch/SnapNote.git
   cd SnapNote
   ```

2. Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser at `http://localhost:8501`

3. Upload an image or use your webcam to capture notes

4. Adjust settings in the sidebar:
   - Select Enhancement Mode (Scan mode recommended for handwritten notes)
   - Enable/disable Auto-Crop and Deskew

5. Download the processed image as PDF

## Project Structure

```
SnapNote/
├── app.py              # Streamlit web interface
├── processor.py        # Image processing pipeline
├── utils.py            # PDF generation utilities
├── requirements.txt    # Python dependencies
└── README.md
```

## Technical Details

### Image Processing Pipeline

1. **Document Detection**: Uses Canny edge detection and contour approximation to find document boundaries
2. **Perspective Transform**: Applies four-point perspective transformation for deskewing
3. **Enhancement**: 
   - CLAHE (Contrast Limited Adaptive Histogram Equalization) for local contrast improvement
   - Bilateral filtering for noise reduction while preserving edges
   - Adaptive thresholding for clean binary output

### Dependencies

- streamlit: Web application framework
- opencv-python-headless: Computer vision operations
- numpy: Numerical computing
- reportlab: PDF generation
- Pillow: Image handling

## Configuration

The Auto-Crop feature works best with:
- Documents photographed on contrasting backgrounds
- Clear document edges visible in the image
- Sufficient lighting

For documents without clear edges, disable Auto-Crop for best results.

## License

MIT License
