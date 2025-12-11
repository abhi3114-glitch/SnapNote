import cv2
import numpy as np

def order_points(pts):
    """
    Order points in top-left, top-right, bottom-right, bottom-left order.
    """
    rect = np.zeros((4, 2), dtype="float32")
    
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

def four_point_transform(image, pts):
    """
    Obtain a consistent "bird's eye view" of the image using the perspective transform.
    """
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coord or the top-right and top-left x-coord
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coord or the top-left and bottom-left y-coord
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warped

def find_document_contour(image):
    """
    Finds the largest 4-sided contour in the image which is likely the document.
    Returns None if no suitable contour is found.
    """
    h, w = image.shape[:2]
    image_area = h * w
    min_area = image_area * 0.2  # Document must be at least 20% of image
    
    # Resize for faster processing
    scale = 1.0
    if h > 1000:
        scale = 1000.0 / h
        proc_img = cv2.resize(image, (int(w * scale), int(h * scale)))
    else:
        proc_img = image.copy()
        
    gray = cv2.cvtColor(proc_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Try multiple edge detection thresholds
    for canny_low, canny_high in [(30, 100), (50, 150), (75, 200)]:
        edged = cv2.Canny(gray, canny_low, canny_high)
        
        # Dilate to close gaps in edges
        kernel = np.ones((3, 3), np.uint8)
        edged = cv2.dilate(edged, kernel, iterations=1)
        
        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
        
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            if len(approx) == 4:
                # Check if this contour is large enough
                contour_area = cv2.contourArea(approx)
                scaled_min_area = min_area * (scale ** 2)
                
                if contour_area >= scaled_min_area:
                    return approx.reshape(4, 2) / scale
    
    return None

def apply_adaptive_threshold(image):
    """
    Converts image to grayscale and applies processing to get a clean scanned look.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Use adaptive threshold which works better for documents
    # Block size 11, C constant 2 for good text detection
    thresh = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2)
    
    return thresh

def increase_contrast(image, alpha=1.5, beta=0):
    """
    Increase contrast (alpha) and brightness (beta).
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def process_image(image, use_perspective=True, enhance_mode="Scan"):
    """
    Main processing pipeline.
    enhance_mode: "Original", "Grayscale", "Scan", "High Contrast"
    """
    output = image.copy()
    
    if use_perspective:
        contour = find_document_contour(image)
        if contour is not None:
            output = four_point_transform(image, contour)
        else:
            # Fallback: Just return original if no contour found
            pass 
            
    if enhance_mode == "Grayscale":
        output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    elif enhance_mode == "Scan":
        output = apply_adaptive_threshold(output)
    elif enhance_mode == "High Contrast":
        output = increase_contrast(output, alpha=2.0, beta=-50) # Strong contrast
        
    return output
