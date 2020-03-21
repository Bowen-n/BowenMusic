import json
import math
import urllib

import requests


class QQMusicApi():
    def __init__(self):
        self.sip = 'http://dl.stream.qqmusic.qq.com/'


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

        # print(search_result)
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
            # 'cookie': , 
            'origin': 'https://y.qq.com',
            'referer': 'https://y.qq.com/portal/player.html',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

        result = self._request(url=vkey_url, headers=headers)

        # result = self._request(url=vkey_url)
        # print(result['req_0']['data'])

        purl = result['req_0']['data']['midurlinfo'][0]['purl']
        
        if purl == "":
            print('no purl')
            return None

        # get guid and vkey
        # self.guid = purl.split('&')[0].split('=')[-1]
        # self.vkey = purl.split('&')[1].split('=')[-1]
        return self.sip + purl


    def convert_interval(self, interval):
        
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


    def _request(self, url, params=None, headers=None):
        ''' return response dict '''
        return json.loads(requests.get(url, params=params, headers=headers).text)





'''

api = QQMusicApi()
search_result = api.search('告白气球')

url = api.get_url(search_result[0]['song_mid'])
print(url)
urllib.request.urlretrieve(url, '告白气球.m4a')
'''
