from flask import Flask, render_template, jsonify, request, Response
from pymongo import MongoClient
import cv2

app = Flask(__name__, template_folder='templates')  # 템플릿 폴더를 'templates'로 설정

# MongoDB 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['video_database']
collection = db['videos']

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

# 비디오 스트림 생성기
def generate_video_stream(camera_id=0):
    # OpenCV를 사용하여 카메라 스트림 캡처
    cap = cv2.VideoCapture(camera_id)
    while True:
        success, frame = cap.read()
        if not success:
            break
        # 프레임을 JPEG 형식으로 인코딩
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        # 멀티파트 응답 생성
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
