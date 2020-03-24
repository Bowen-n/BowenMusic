import base64
import binascii
import codecs
import json
import math
import os
import urllib

import requests
from Cryptodome.Cipher import AES


def convert_interval(interval):
    ''' convert interval(s) to   `str` -  hour:min:sec '''
    hour = math.floor(interval / 3600)
    interval %= 3600
    minu = math.floor(interval / 60)
    sec = interval % 60

    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)
    
    if minu < 10:
        minu = '0' + str(minu)
    else:
        minu = str(minu)

    if sec < 10:
        sec = '0' + str(sec)
    else:
        sec = str(sec)
    
    if hour == '00':
        return minu + ':' + sec
    else:
        return hour + ':' + minu + ':' + sec


class QQMusicApi():
    ''' Ref: https://jsososo.com/#/article?id=5a6254c0c4 '''

    def __init__(self):
        self.sip = 'http://dl.stream.qqmusic.qq.com/'
        self.name = 'qq'

    def search(self, page, keyword):
        ''' search according to keyword 
        keyword - `str`
        '''
        search_url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"

        params = {
            'format': 'json',
            'w': keyword,
            'n': 10, # 10 items
            'p': page,
            'cr': 1
        }

        result = self._request(search_url, params)
        result = result['data']['song']['list']

        search_result = []


        for item in result:
            info = {}
            info['interval'] = item['interval']
            info['song_mid'] = item['songmid']
            info['media_mid'] = item['media_mid'] if 'media_mid' in item.keys() else None
            info['song_name'] = item['songname']
            info['album_name'] = item['albumname']
            info['album_mid'] = item['albummid']
            
            singer_list = []
            for singer in item['singer']:
                singer_list.append(singer['name'])
            info['singer_list'] = singer_list     

            image_url = 'https://y.gtimg.cn/music/photo_new/T002R300x300M000' + info['album_mid'] + '.jpg'
            info['image_url'] = image_url
            search_result.append(info)

        return search_result

    
    def get_url(self, song_mid):
        ''' get guid and vkey
        Args:
            song_mid - `str` song mid
        '''

        vkey_url = "https://u.y.qq.com/cgi-bin/musicu.fcg?-=getplaysongvkey9649193568019525&g_tk=105169251&loginUin=501894013&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data=%7B%22req%22%3A%7B%22module%22%3A%22CDN.SrfCdnDispatchServer%22%2C%22method%22%3A%22GetCdnDispatch%22%2C%22param%22%3A%7B%22guid%22%3A%224120992304%22%2C%22calltype%22%3A0%2C%22userip%22%3A%22%22%7D%7D%2C%22req_0%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%224120992304%22%2C%22songmid%22%3A%5B%22{}%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%22501894013%22%2C%22loginflag%22%3A1%2C%22platform%22%3A%2220%22%7D%7D%2C%22comm%22%3A%7B%22uin%22%3A501894013%2C%22format%22%3A%22json%22%2C%22ct%22%3A24%2C%22cv%22%3A0%7D%7D".format(song_mid)

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': # vip songs need vip's cookie 
            'origin': 'https://y.qq.com',
            'referer': 'https://y.qq.com/portal/player.html',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

        result = self._request(url=vkey_url, headers=headers)

        purl = result['req_0']['data']['midurlinfo'][0]['purl']
        
        if purl == "":
            print('no purl')
            return None

        return self.sip + purl


    def _request(self, url, params=None, headers=None):
        ''' return response dict '''
        return json.loads(requests.get(url, params=params, headers=headers).text)


class NeteaseCloudMusicAPI():
    ''' Ref: https://www.jianshu.com/p/5379d35ed646 '''

    def __init__(self):
        self.name = 'netease'
        self.base_url = 'http://music.163.com/'
        self.header={
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'https://music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/70.0.3538.110 Safari/537.36'
        }

        # constant for cipher
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nonce = b'0CoJUm6Qyw8W8jud'
        self.pubKey = '010001'

    def search(self, keyword, type, offset=0, limit=30):
        '''
        type - 
            1: 单曲     10: 专辑   100: 歌手    1000: 歌单 
            1002: 用户  1004: MV   1006: 歌词   1009: 电台
        '''
        url = self.base_url + 'weapi/cloudsearch/get/web?csrf_token='
        req = {
            's': keyword, 
            'type': type, 
            'offset': offset, 
            'total':'true', 
            'limit': limit
        }
        response = requests.post(url, data=self._encrypted_request(req), headers=self.header)
        result = json.loads(response.text)
        song_list = result['result']['songs']
        
        search_result = []
        for item in song_list:
            info = {}
            info['song_name'] = item['name']
            info['song_mid'] = item['id']
            info['album_name'] = item['al']['name']
            info['album_mid'] = item['al']['id']
            info['interval'] = int(int(item['dt'])/1000)
            singer_list = []
            for singer in item['ar']:
                singer_list.append(singer['name'])
            
            info['singer_list'] = singer_list
            search_result.append(info)

        return search_result
    

    def get_url(self, song_id, br=128000):
        url = self.base_url + 'weapi/song/enhance/player/url?csrf_token='
        req = {
            'ids': [song_id],
            'br': br
        }
        response = requests.post(url, data=self._encrypted_request(req), headers=self.header)
        result = json.loads(response.text)

        return result['data'][0]['url']
        

    def _create_secret_key(self, size):
        ''' reimplement of function a
        Generate random string
        '''
        return binascii.hexlify(os.urandom(size))[:16]

    def _aes_encrypt(self, text, secKey):
        pad = 16 - len(text.encode()) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(secKey, AES.MODE_CBC, '0102030405060708'.encode('utf8'))
        ciphertext = encryptor.encrypt(text.encode('utf8'))
        ciphertext = base64.b64encode(ciphertext).decode('utf8')
        return ciphertext

    def _rsa_encrypt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = int(bytes.hex(text), 16) ** int(pubKey, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)
    
    def _encrypted_request(self, text):
        text = json.dumps(text)
        secKey = self._create_secret_key(16)
        encText = self._aes_encrypt(self._aes_encrypt(text, self.nonce), secKey)
        encSecKey = self._rsa_encrypt(secKey, self.pubKey, self.modulus)
        return  {
            'params': encText,
            'encSecKey': encSecKey
        }


class MiguMusicAPI():
    def __init__(self):
        self.headers = {
            'Host': 'm.music.migu.cn',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Mobile Safari/537.36',
        }
        self.url = 'http://m.music.migu.cn/migu/remoting/scr_search_tag?'
        self.name = 'migu'

    def search(self, keyword):
        params = {
            'rows': 20,
            'type': 2,
            'keyword': keyword,
            'pgc': 1
        }

        response = requests.get(self.url, params, headers=self.headers)
        result = json.loads(response.text)
        result = result['musics']

        search_result = []
        for item in result:
            # print(item)
            info = {}
            info['song_name'] = item['songName']
            info['song_mid'] = item['id']
            info['album_name'] = item['albumName']
            info['album_mid'] = item['albumId']
            info['interval'] = None
            info['singer_list'] = item['singerName']
            info['url'] = item['mp3']
            search_result.append(info)

        return search_result

# test NeteaseCloudMusicAPI
# keyword = '我的一个道姑朋友'
# api = NeteaseCloudMusicAPI()
# print(api.search(keyword, 1))
# print(api.get_url(song_id='1367452194'))

# test MiguMusicAPI
# api = MiguMusicAPI()
# print(api.search('告白气球'))


# test QQMusicApi
# api = QQMusicApi()
# search_result = api.search('告白气球')
# url = api.get_url(search_result[0]['song_mid'])
# print(url)
# urllib.request.urlretrieve(url, '告白气球.m4a')

