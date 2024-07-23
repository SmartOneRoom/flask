from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np

app = Flask(__name__)
camera = cv2.VideoCapture(0)

# 간단한 세그멘테이션을 위한 함수 (실제 구현에서는 더 복잡한 알고리즘을 사용해야 합니다)
def simple_segmentation(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    return res

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

def generate_segmentation(color):
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # 간단한 색상 기반 세그멘테이션 (예: 빨간색)
            lower_color = np.array([0, 100, 100])
            upper_color = np.array([10, 255, 255])
            segmented_frame = simple_segmentation(frame, lower_color, upper_color)
            ret, buffer = cv2.imencode('.jpg', segmented_frame)
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
    return Response(generate_segmentation('red'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/search', methods=['POST'])
def search_object():
    data = request.json
    search_text = data.get('text', '')
    # 여기에 실제 검색 로직을 구현해야 합니다.
    # 현재는 단순히 검색 텍스트를 반환합니다.
    return jsonify({'result': f'Searching for: {search_text}'})

if __name__ == '__main__':
    app.run(debug=True)
