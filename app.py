from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import torch
from ultralytics import FastSAM
from ultralytics.models.fastsam import FastSAMPrompt

app = Flask(__name__)
camera = cv2.VideoCapture(0)

# FastSAM 모델 로드
model = FastSAM("FastSAM-x.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
print(f"Model loaded: {model is not None}")

# 전역 변수로 search_text 선언
search_text = ""

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_segmentation():
    global search_text
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Run inference on the frame
            results = model(frame, device=device, retina_masks=True, imgsz=640, conf=0.4, iou=0.9)

            # Prepare a Prompt Process object
            prompt_process = FastSAMPrompt(frame, results, device=device)

            if search_text:
                # Text prompt
                ann = prompt_process.text_prompt(text=f"a photo of a {search_text}")
            else:
                # Everything prompt if no search text
                ann = prompt_process.everything_prompt()

            # Initialize output as the original frame
            output = frame

            # Check if ann is not None and has masks
            if ann is not None and isinstance(ann, list) and len(ann) > 0:
                if hasattr(ann[0], 'masks') and len(ann[0].masks) > 0:
                    mask = ann[0].masks.data[0].cpu().numpy()

                    # Create a colored mask
                    colored_mask = np.zeros_like(frame)
                    colored_mask[mask == 1] = [0, 255, 0]  # Green color for the mask

                    # Blend the original frame with the colored mask
                    alpha = 0.5  # Transparency factor
                    output = cv2.addWeighted(frame, 1, colored_mask, alpha, 0)

            ret, buffer = cv2.imencode('.jpg', output)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/segmentation_feed')
def segmentation_feed():
    return Response(generate_segmentation(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/search', methods=['POST'])
def search_object():
    global search_text
    data = request.json
    search_text = data.get('text', '')
    return jsonify({'result': f'Searching for: {search_text}'})

# 모델 테스트
test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
test_results = model(test_image, device=device, retina_masks=True, imgsz=640, conf=0.4, iou=0.9)
print(f"Test results: {test_results}")

if __name__ == '__main__':
    app.run(debug=True, threaded=True)