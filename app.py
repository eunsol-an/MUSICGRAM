from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbmusicgram


## HTML을 주는 부분
@app.route('/')
def index():
   return render_template('index.html')

@app.route('/talk')
def talk():
   return render_template('talk.html')

@app.route('/album', methods=['GET'])
def list_album():
    albums = list(db.albums.find({}, {'_id': False}).sort('like', -1))
    return jsonify({'all_albums':albums})

## API 역할을 하는 부분
@app.route('/album', methods=['POST'])
def save_album():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    image = soup.select_one('meta[property="og:image"]')['content']
    title = soup.select_one('meta[property="og:title"]')['content']


    doc = {
        'title': title,
        'image': image,
        'url': url_receive,
        'comment': comment_receive,
        'like': 0
    }

    db.albums.insert_one(doc)

    return jsonify({'msg':'당신의 인생곡을 남겨 주셔서 감사합니다!'})

@app.route('/album/like', methods=['POST'])
def like_album():
    title_receive = request.form['title_give']

    target_album = db.albums.find_one({'title':title_receive})
    current_like = target_album['like']

    new_like = current_like + 1

    db.albums.update_one({'title': title_receive}, {'$set': {'like': new_like}})

    return jsonify({'msg': '좋아요 완료!'})

@app.route('/album/talk', methods=['POST'])
def save_talk():
    nickname_recive = request.form['nickname_give']
    talk_recive = request.form['talk_give']
    date_recive = request.form['date_give']

    doc = {
        'nickname': nickname_recive,
        'talk': talk_recive,
        'date': date_recive,
    }

    db.talks.insert_one(doc)

    return jsonify({'msg': '당신의 이야기를 남겨 주셔서 감사합니다!'})

@app.route('/album/talk', methods=['GET'])
def list_talk():
    talks = list(db.talks.find({}, {'_id': False}).sort('date',-1))
    return jsonify({'all_talks': talks})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)