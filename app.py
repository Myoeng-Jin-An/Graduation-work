from flask import Flask, render_template, jsonify, request, Response
from pymongo import MongoClient
import cv2
import torch
import numpy as np
from collections import deque
from mmaction.apis.inferencers import MMAction2Inferencer

app = Flask(__name__, template_folder='templates')  # 템플릿 폴더를 'templates'로 설정

# MongoDB 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['video_database']
collection = db['videos']

# 이상행동 AI 모델 로드
config_path_abnormal = "model/이상행동/tsm_imagenet-pretrained-r50_8xb16-1x1x8-100e_kinetics400-rgb.py"
checkpoint_path_abnormal = "model/이상행동/tsm_imagenet-pretrained-r50_8xb16-1x1x8-50e_kinetics400-rgb_20220831-64d69186.pth"

model_abnormal = MMAction2Inferencer(
    rec=config_path_abnormal,
    rec_weights=checkpoint_path_abnormal,
    device="cuda:0",
    input_format="array"
)

# 구매행동 AI 모델 로드
config_path_purchase = "model/구매행동/tsm_imagenet-pretrained-r50_8xb16-1x1x8-100e_kinetics400-rgb.py"
checkpoint_path_purchase = "model/구매행동/best_acc_top1_epoch_8.pth"

model_purchase = MMAction2Inferencer(
    rec=config_path_purchase,
    rec_weights=checkpoint_path_purchase,
    device="cuda:0",
    input_format="array"
)

SEQUENCE_LENGTH = 1
HYPER_VALUE_STEAL = 0.9  # 이상 행동 감지 임계값

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recodingvideos.html')
def recodingvideos():
    return render_template('recodingvideos.html')

@app.route('/api/videos')
def get_videos():
    # 최근 5개의 영상 가져오기
    videos = list(collection.find().sort('date', -1).limit(5))
    # 필요한 데이터만 추출
    video_list = [
        {"date": video['date'], "time": video['time'], "url": video['url']}
        for video in videos
    ]
    return jsonify(video_list)

# 비디오 스트림 생성기 (AI 분석 적용)
def generate_video_stream(camera_id=0):
    cap = cv2.VideoCapture(camera_id)
    frames = deque(maxlen=SEQUENCE_LENGTH)

    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frames.append(frame)
        if len(frames) != SEQUENCE_LENGTH:
            continue  # 충분한 프레임이 쌓일 때까지 대기

        # 이상행동 AI 모델 예측
        results_abnormal = model_abnormal(inputs=np.array(frames))
        _, preds_steal = results_abnormal["predictions"][0]["rec_scores"][0]

        # 구매행동 AI 모델 예측
        results_purchase = model_purchase(inputs=np.array(frames))
        _, preds_purchase = results_purchase["predictions"][0]["rec_scores"][0]

        # 프레임에 예측 결과 추가
        text_abnormal = f"Steal Probability: {round(preds_steal, 4)}"
        color_abnormal = (0, 255, 0) if preds_steal < HYPER_VALUE_STEAL else (0, 0, 255)
        cv2.putText(frame, text_abnormal, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color_abnormal, 2)

        text_purchase = f"Purchase Probability: {round(preds_purchase, 4)}"
        color_purchase = (0, 255, 0) if preds_purchase < 0.5 else (0, 0, 255)  # 임의의 임계값 사용
        cv2.putText(frame, text_purchase, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color_purchase, 2)

        if preds_steal > HYPER_VALUE_STEAL:
            cv2.putText(frame, "⚠️ Abnormal Action Detected!", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        if preds_purchase > 0.5:  # 임의의 임계값 사용
            cv2.putText(frame, "✔️ Purchase Action Detected!", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# 실시간 카메라 스트림을 위한 엔드포인트
@app.route('/video_feed')
def video_feed():
    camera_id = int(request.args.get('camera_id', 0)) # 기본 카메라 ID는 0
    return Response(generate_video_stream(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stream-url')
def get_stream_url():
    camera_id = request.args.get('camera_id')
    # 카메라 ID에 따라 실시간 스트림 URL을 반환
    stream_urls = {
        '1': 'http://yourserver.com/stream1',
        '2': 'http://yourserver.com/stream2',
        '3': 'http://yourserver.com/stream3',
        '4': 'http://yourserver.com/stream4',
    }
    url = stream_urls.get(camera_id, '')
    return jsonify({'url': url})

if __name__ == '__main__':
    app.run(debug=True)
