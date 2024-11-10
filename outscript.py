import os
#F67E14 is the bound
import subprocess
import cv2
import numpy as np
from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)

# In-memory storage for rate limiting (timestamp of requests)
request_times = {}

MAX_REQUESTS_PER_MINUTE = 30
MAX_IMAGE_WIDTH = 5000
MAX_IMAGE_HEIGHT = 5000

def check_image_size(image):
    height, width = image.shape[:2]
    if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
        return False
    return True

# Function to track requests and apply rate limiting
def check_rate_limit(remote_addr):
    current_time = time.time()

    # Get the list of timestamps for this IP address
    if remote_addr not in request_times:
        request_times[remote_addr] = []

    # Remove timestamps older than 60 seconds
    request_times[remote_addr] = [t for t in request_times[remote_addr] if current_time - t <= 60]

    # Check if there are more than MAX_REQUESTS_PER_MINUTE requests
    if len(request_times[remote_addr]) >= MAX_REQUESTS_PER_MINUTE:
        return False

    # Record the current request timestamp
    request_times[remote_addr].append(current_time)
    return True

@app.route('/process_image', methods=['POST'])
@limiter.limit("30 per minute")  # Apply rate limiting
def process_image_endpoint():
    # Get the image from the POST request (assuming it's uploaded as multipart/form-data)
    remote_addr = get_remote_address()

    # Check if the rate limit has been exceeded
    if not check_rate_limit(remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    #change code flow to first save the image, then run it through
    img = Image.open(file)
    img = np.array(img)  # Convert PIL image to numpy array (OpenCV format)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert from RGB to BGR for OpenCV
    cv2.imwrite('input/input.png', img)
    #run the subprocess
    try:
        subprocess.run(['python', 'run.py',
    '--model_type', 'dpt_swin2_large_384',
    '--input_path', 'input',
    '--output_path', 'output'
    ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Model failed with error: {e}")
        return jsonify({"error": "Model failed to process image"}), 400
    img = load_image('output/input-dpt_swin2_large_384.png')
    try:
        hotspots = detect_hotspots(img)
        return jsonify(hotspots)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load_image(path, timeout=120):
    start_time = time.time()

    # Wait until the output image is available or timeout is reached
    while not os.path.exists(path):
        # Check if the timeout has been exceeded
        if time.time() - start_time > timeout:
            print(f"Timeout reached: Unable to process image in {timeout} seconds.")
            return None  # Return None or raise an exception based on your needs
        time.sleep(0.1)  # Check every 100 ms
    # Load and return the image
    return cv2.imread(path)

def detect_hotspots(image, threshold=200, min_area=50):
    # Load the image and convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply threshold to isolate high-intensity pixels (white regions)
    _, binary_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)

    # Find contours of white regions
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # List to store the coordinates and intensity of each hotspot
    hotspots = []
    for contour in contours:
        # Filter out small contours based on area
        if cv2.contourArea(contour) >= min_area:
            # Calculate the centroid of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Collect pixel intensities from the contour
                contour_pixels = []
                for point in contour:
                    x, y = point[0]
                    contour_pixels.append(gray_image[y, x])

                # Sort the intensities in descending order and take the top 10 most intense pixels
                contour_pixels.sort(reverse=True)

                # Take the average of the top 10 intense pixels (or fewer if there are less than 10)
                top_intensity_pixels = contour_pixels[:10]
                avg_intensity = np.sum(top_intensity_pixels).astype(np.int32)  / len(top_intensity_pixels) if top_intensity_pixels else 0
                
                # Add the centroid coordinates and intensity to the list
                hotspots.append((calculate_angle_with_fov(gray_image,cx,cy), avg_intensity))

    return hotspots
def calculate_angle_with_fov(image, x, y, fov_degrees=70):
    rows, cols = image.shape[:2]

    # Calculate the center of the image
    center = (cols // 2, rows // 2)

    # Calculate the differences in x and y from the center
    dx = x - center[0]

    # Calculate the angle in radians using atan2
    angle_rad = np.arctan2(0, dx)  # atan2 only needs dx for horizontal angle

    # Convert the angle to degrees
    angle_deg = np.degrees(angle_rad)

    # Normalize the angle to be in the range [0, 360)
    if angle_deg < 0:
        angle_deg += 360

    # Calculate the scaling factor based on the FOV
    fov_scale = fov_degrees / cols  # degrees per pixel

    # Adjust the angle to match the field of view (FOV)
    fov_angle = (dx * fov_scale) - (fov_degrees / 2)  # Center the angle at 0 degrees

    return fov_angle + fov_degrees // 2



if __name__ == '__main__':
    app.run(debug=True)
