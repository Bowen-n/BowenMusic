# BowenMusic
**Project for IS305**: 支持qq音乐、网易云、咪咕的音乐播放器。桌面版基于`PyQt5`，命令行版使用`Cmd`

### Structure
```
|-- qss                    .qss file for the style of GUI
|-- resource               icons
|-- src                    codes
|---- api.py               APIs of qq/neteasecloud/migu music
|---- component.py         Widgets inherit from `QLabel` and `QLineEdit`
|---- module.py            Four main modules: Header, Navigation, Mainlist, PlayWidgets
|---- MusicDesktop.py      Main window
|---- webdriver.py         Get qq music cookies using Selenium
|-- userdata               cookie, download music and playlist created by the user
```
### Use
Requirements: `$ pip install -r requirements.txt`

Desktop version: `$ python ./src/MusicDesktop.py`

Command version: `$ python ./src/cmd_version/MusicCmd.py`

### API
[NeteaseCloudMusic API](https://github.com/Bowenduan/BowenMusic/wiki/NeteaseCloudMusic-API)

### Screenshot
##### 搜索歌曲
![search](demo/search.jpg)
##### 歌单
![playlist](demo/playlist.jpg)
##### Command
![command_v1](demo/cmd_v1.jpg)
### Progress
2020.3.10 - 2020.3.15
* QQ Music API 调研已完成，可获取歌信息和URL，会员歌曲需要绿钻用户Cookie
* 图标准备，资源为[Iconfont](https://www.iconfont.cn/) 和 [easyicon](https://www.easyicon.net/)
* 基本界面的完成，包括Header, Navigation, Mainlist, Player 四个模块

2020.3.19
* 完成**global**音乐的双击下载与播放功能
* 问题
  * Album图片的显示不完整，更改了图片源后显示依然不变

2020.3.20
* 完成Navigation事件绑定，包括我的歌单，在线音乐，本地音乐
* 增加了将在线音乐添加到我的歌单的功能
* 问题
  * ~~Player排本问题（有的歌名特别长，把其他按钮挤到了最右边)~~
  * 最好设计成QQ音乐一样的滚动歌名（对于长歌名）

2020.3.21 
* 完成Player播放时间和滚动条的对应
* 调整Navigation栏目的间距和宽度（界面美化）
* 支持了多个歌单的“加入歌单”功能以及Navigation中多歌单的显示
* 完成歌单播放，对于本地音乐和歌单，播放里面的一首歌就将本地或对应歌单的所有歌加入后台播放列表中，并完成顺序、单曲循环、随机播放三种模式的功能

2020.3.23
* 完成网易云搜索歌曲（专辑、歌手）API，完成[网易云API文档](https://github.com/Bowenduan/BowenMusic/wiki/NeteaseCloudMusic-API)
* 问题
  ```python 
  from Crypto.Cipher import AES
  ```
  报错的原因是Crypto只支持32位，需要安装[pycryptodome](https://github.com/Legrandin/pycryptodome)，建议使用`pip install pycryptodomex`安装，然后
  ```python
  from Cryptodome.Cipher import AES
  ```

2020.3.24
* 将选择音乐源放在Navigation栏的在线音乐中
* 添加网易云搜索、播放、加入歌单功能
* 完成**咪咕音乐API**
* 添加咪咕搜索、播放、加入歌单功能

2020.3.25
* *webdriver.py* :使用selenium自动登录QQ音乐网页并获取cookie保存json文件，需在`self.account`和`self.password`中填入账号密码
```python 
class QQMusicWebdriver():
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.browser.get('https://y.qq.com/')
        self.account = ''  # your qq id
        self.password = '' # your password
```
* QQMusicAPI中增加从本地json文件读取cookie
* 针对没有QQvip的cookie而无法下载歌曲的处理

2020.3.26
* 新建歌单功能

2020.3.27
* 删除、重命名歌单
* 新建歌单后的QLineEdit焦点设置

2020.3.28
* 本地音乐中增加播放、从本地删除功能
* 歌单中增加播放、从歌单删除功能
* 如果userdata/music中有其他奇怪的文件会报错的问题

2020.3.29 :musical_note: **Desktop version finished**
* Player部件排版调整，不会因为歌名长度不一而部件移动 
  * Question 如何在QLabel中实现滚动字幕 ?

2020.3.30
* 完成命令行版展示歌单功能

### TODO
* [x] 网易云音乐API
* [x] 咪咕音乐API
* [x] 添加歌单功能
* [x] Player排版问题（歌名长度不一致）
* [x] 从歌单中删除歌
* [ ] 歌曲信息以滚动的方式显示 **ScrollLabel** in */src/component.py*
* [ ] :triangular_flag_on_post: 添加命令行版本(Windows & Linux & MacOS) 使用强大的**mpv**播放器，以及`python-mpv`接口