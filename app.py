from flask import Flask, render_template, jsonify, request, Response
import cv2
import numpy as np
import base64
import os

app = Flask(__name__, 
            static_folder='static',  # specify the static folder
            template_folder='templates')  # specify the templates folder

class ColorDetector:
    def __init__(self):
        self.colors = {
            "Red": [(0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)],
            "Green": [(35, 50, 50), (85, 255, 255)],
            "Blue": [(100, 50, 50), (130, 255, 255)],
            "Yellow": [(20, 100, 100), (35, 255, 255)],
            "Orange": [(10, 100, 100), (20, 255, 255)],
            "Purple": [(130, 50, 50), (160, 255, 255)],
            "Pink": [(140, 50, 100), (170, 255, 255)],
            "Cyan": [(85, 50, 50), (100, 255, 255)],
            "White": [(0, 0, 180), (180, 30, 255)],
            "Gray": [(0, 0, 50), (180, 30, 180)],
            "Black": [(0, 0, 0), (180, 255, 50)],
            "Brown": [(10, 50, 50), (30, 255, 255)],
            "Lime": [(35, 50, 50), (85, 255, 255)],
            "Teal": [(85, 50, 50), (95, 255, 255)],
            "Lavender": [(130, 50, 50), (160, 255, 255)],
            "Beige": [(10, 10, 180), (30, 50, 255)],
            "Gold": [(25, 50, 50), (35, 255, 255)],
            "Silver": [(0, 0, 200), (180, 30, 230)],
            "Indigo": [(130, 50, 50), (140, 255, 255)],
            "Maroon": [(0, 50, 50), (10, 255, 150)],
            "Peach": [(5, 50, 200), (15, 255, 255)],
            "Coral": [(0, 50, 50), (15, 255, 255)],
            "Salmon": [(5, 50, 50), (15, 255, 255)],
            "Chartreuse": [(35, 50, 50), (85, 255, 255)],
            "Aquamarine": [(85, 50, 50), (95, 255, 255)],
            "Seafoam": [(85, 50, 50), (100, 255, 255)],
            "Periwinkle": [(130, 50, 50), (160, 255, 255)],
            "Fuchsia": [(140, 50, 100), (160, 255, 255)],
            "Violet": [(130, 50, 50), (160, 255, 255)],
            "Azure": [(160, 50, 50), (180, 255, 255)],
            "Turquoise": [(85, 50, 50), (95, 255, 255)],
            "Mint": [(85, 50, 50), (90, 255, 255)],
            "Plum": [(130, 50, 50), (160, 255, 255)],
            "Wheat": [(15, 10, 180), (30, 50, 255)],
            "Khaki": [(15, 50, 50), (30, 255, 255)],
            "RoyalBlue": [(100, 50, 50), (130, 255, 255)],
            "SkyBlue": [(100, 50, 50), (130, 255, 255)],
            "Olive": [(35, 50, 50), (85, 255, 255)],
            "Mauve": [(140, 50, 100), (170, 255, 255)],
            "Amber": [(30, 50, 50), (45, 255, 255)],
            "Carmine": [(0, 50, 50), (10, 255, 150)],
            "Emerald": [(35, 50, 50), (80, 255, 255)],
            "Sapphire": [(100, 50, 50), (130, 255, 255)],
            "Turquoise": [(85, 50, 50), (95, 255, 255)],
            "Cobalt": [(100, 50, 50), (130, 255, 255)],
            "Jade": [(40, 50, 50), (70, 255, 255)],
            "Amethyst": [(130, 50, 50), (160, 255, 255)],
            "Rose": [(140, 50, 100), (170, 255, 255)],
            "Fuchsia": [(140, 50, 50), (160, 255, 255)],
            "Tangerine": [(15, 50, 50), (30, 255, 255)],
            "Celeste": [(100, 50, 50), (130, 255, 255)],
            "LavenderBlush": [(130, 50, 50), (160, 255, 255)],
            "Honeydew": [(85, 50, 50), (100, 255, 255)],
            "MossGreen": [(35, 50, 50), (70, 255, 255)],
            "PeacockBlue": [(85, 50, 50), (95, 255, 255)],
            "SpringGreen": [(35, 50, 50), (85, 255, 255)],
            "TurquoiseBlue": [(85, 50, 50), (100, 255, 255)],
            "PaleGreen": [(40, 50, 50), (70, 255, 255)],
            "Chartreuse": [(35, 50, 50), (85, 255, 255)],
            "Goldenrod": [(25, 50, 50), (35, 255, 255)],
        }

    def get_closest_color(self, hsv_value):
        min_diff = float('inf')
        closest_color = "Unknown"
        
        hsv_np = np.array(hsv_value)
        
        for color_name, hsv_ranges in self.colors.items():
            if len(hsv_ranges) == 2:
                lower, upper = np.array(hsv_ranges[0]), np.array(hsv_ranges[1])
                if all(lower <= hsv_np) and all(hsv_np <= upper):
                    center = (lower + upper) / 2
                    diff = np.sum(np.abs(hsv_np - center))
                    if diff < min_diff:
                        min_diff = diff
                        closest_color = color_name
            else:
                lower1, upper1, lower2, upper2 = [np.array(x) for x in hsv_ranges]
                for lower, upper in [(lower1, upper1), (lower2, upper2)]:
                    if all(lower <= hsv_np) and all(hsv_np <= upper):
                        center = (lower + upper) / 2
                        diff = np.sum(np.abs(hsv_np - center))
                        if diff < min_diff:
                            min_diff = diff
                            closest_color = color_name
        
        return closest_color

detector = ColorDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect_color', methods=['POST'])
def detect_color():
    try:
        data = request.json
        if not data or 'image' not in data or 'x' not in data or 'y' not in data:
            return jsonify({'error': 'Missing required data'}), 400

        image_data = data['image'].split(',')[1]
        x = int(data['x'])
        y = int(data['y'])
        
        # Decode base64 image
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400

        # Convert to HSV and detect color
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
            hsv_color = hsv_frame[y, x]
            color_name = detector.get_closest_color(hsv_color)
            bgr_color = cv2.cvtColor(np.uint8([[hsv_color]]), cv2.COLOR_HSV2BGR)[0][0]
            rgb_color = tuple(map(int, bgr_color[::-1]))
            return jsonify({
                'color_name': color_name,
                'rgb_color': rgb_color
            })
        else:
            return jsonify({'error': 'Coordinates out of bounds'}), 400

    except Exception as e:
        app.logger.error(f"Error in detect_color: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/video_feed')
def video_feed():
    try:
        cap = cv2.VideoCapture(0)
        def generate_frames():
            while True:
                success, frame = cap.read()
                if not success:
                    break
                else:
                    frame = cv2.flip(frame, 1)
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            cap.release()
        
        return Response(generate_frames(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        app.logger.error(f"Error in video_feed: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)