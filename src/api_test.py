import requests

url = 'http://127.0.0.1:5000/music/search'

params = {'api': 'netease', 'keywords': '告白气球'}

# test search
# print('GET: ' + requests.get(url, params).text)
print('POST: ' + requests.post(url, params).text)

# test url
print(requests.post('http://127.0.0.1:5000/music/url', {'api': 'netease', 'song_id': 452804665}).text)
