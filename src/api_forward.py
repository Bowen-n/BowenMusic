from flask import Flask, redirect, url_for, request
from api import MiguMusicAPI, NeteaseCloudMusicAPI, QQMusicApi

API_DICT = {
    'qq': QQMusicApi(),
    'netease': NeteaseCloudMusicAPI(),
    'migu': MiguMusicAPI()}

app = Flask(__name__)

@app.route('/')
def main():
    return redirect(url_for('music'))

@app.route('/music')
def music():
    return 'Welcome to BowenMusic'

@app.route('/music/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        api = request.args.get('api')
        keywords = request.args.get('keywords')
    elif request.method == 'POST':
        api = request.form.get('api')
        keywords = request.form.get('keywords')
    
    if api not in API_DICT:
        return {'error': 'Only support qq, netease, migu.'}

    music_api = API_DICT[api]
    results = music_api.search(keywords)

    return_list = []
    for item in results:
        return_list.append({
                'song_name': item['song_name'],
                'song_id': item['song_mid'],
                'singers': item['singer_list'],
                'album_name': item['album_name'],
                'interval': item['interval'],
                'url': item['url'] if 'url' in item else None
            })
    return {'result': return_list}


@app.route('/music/url', methods=['GET', 'POST'])
def url():
    if request.method == 'GET':
        api = request.args.get('api')
        song_id = request.args.get('song_id')
    elif request.method == 'POST':
        api = request.form.get('api')
        song_id = request.form.get('song_id')
    
    if api not in ['qq', 'netease']:
        return {'error': 'Only support qq, netease.'}
    music_api = API_DICT[api]

    url = music_api.get_url(song_id)
    return {'url': url}

        
if __name__ == '__main__':
    app.run()
