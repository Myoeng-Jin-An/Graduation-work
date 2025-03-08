from flask import Flask, render_template, jsonify
from pymongo import MongoClient

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
    videos = list(collection.find().sort('date', -1))  # 날짜 기준 내림차순으로 정렬
    for video in videos:
        video['_id'] = str(video['_id'])  # ObjectId를 문자열로 변환
    return jsonify(videos)

if __name__ == '__main__':
    app.run(debug=True)
