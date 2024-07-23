from flask import Flask, Response
import cv2
import numpy as np
from segment_anything import SamPredictor, sam_model_registry

app = Flask(__name__)

# SAM 모델 초기화
sam = sam_model_registry["default"](checkpoint="path/to/sam_vit_h_4b8939.pth")
predictor = SamPredictor(sam)

def generate_frames():
    camera = cv2.VideoCapture(0)  # 웹캠 열기
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # SAM 적용
            predictor.set_image(frame)
            masks, _, _ = predictor.predict(
                point_coords=None,
                point_labels=None,
                box=None,
                multimask_output=False,
            )
            
            # 마스크를 프레임에 오버레이
            mask = masks[0]
            frame[mask] = frame[mask] * 0.5 + np.array([0, 0, 255]) * 0.5
            
            # JPEG로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)