from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import torch
from ultralytics import FastSAM
from ultralytics.models.fastsam import FastSAMPrompt

app = Flask(__name__)
camera = cv2.VideoCapture(0)

# FastSAM 모델 로드
model = FastSAM("FastSAM-s.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
print(f"Model loaded: {model is not None}")

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
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Run inference on the frame
            results = model(frame, device=device, retina_masks=True, imgsz=640, conf=0.4, iou=0.9)

            # Prepare a Prompt Process object
            prompt_process = FastSAMPrompt(frame, results, device=device)

            # Everything prompt
            ann = prompt_process.everything_prompt()

            # Get the mask
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
    data = request.json
    search_text = data.get('text', '')
    return jsonify({'result': f'Searching for: {search_text}'})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)