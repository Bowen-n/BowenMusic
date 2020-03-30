import os
# os.environ['PATH'] = os.path.dirname(__file__) + os.pathsep + os.environ['PATH']

import mpv
player = mpv.MPV(ytdl=True)
print('start playing')
player.play('userdata\music\烟火里的尘埃_29004400.m4a')
player.wait_for_playback()