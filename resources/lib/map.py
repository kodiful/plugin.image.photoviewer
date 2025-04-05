# -*- coding: utf-8 -*-

import os
import sys
import shutil

from resources.lib.common import Common

import xbmcgui

# staticmap
sys.path.append(os.path.join(Common.RESOURCES_PATH, 'extra'))
from staticmap import StaticMap, CircleMarker


class Map(Common):

    # zoom=数値 を変えることで、広域〜詳細まで調整可能
	# 数値が大きいほど詳細表示（地図の範囲は狭くなる）

    # 5  国レベル（日本全体）
    # 10 都道府県レベル
    # 14 市区町村レベル（街並）
    # 18 建物や道路レベル

    ZOOM = [
        f'1 ({Common.STR(30040)})',  # 世界
        f'2',
        f'3',
        f'4 ({Common.STR(30041)})',  # 国
        f'5',
        f'6',
        f'7',
        f'8 ({Common.STR(30042)})',  # 都道府県
        f'9',
        f'10',
        f'11',
        f'12 ({Common.STR(30043)})',  # 市区町村
        f'13',
        f'14',
        f'15',
        f'16 ({Common.STR(30044)})',  # 町名/丁目
        f'17',
        f'18'
    ]

    def __init__(self):
        # キャッシュディレクトリ
        self.cache = os.path.join(self.PROFILE_PATH, 'cache', 'staticmap')
        # ディレクトリが無ければ作成
        os.makedirs(self.cache, exist_ok=True)

    def clear(self):
        shutil.rmtree(self.cache)

    def convert(self, uuid, lat, long):
        # ズーム設定
        preselect = int(self.GET('zoom'))
        index = xbmcgui.Dialog().select(self.STR(30202), self.ZOOM, preselect=preselect)
        if index == -1:  # cancel
            return None
        self.SET('zoom', str(index))
        zoom = index + 1
        # 出力ファイル
        out_dir = os.path.join(self.cache, str(zoom), uuid[0])
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f'{uuid}.png')
        # 画像変換実行
        if os.path.isfile(out_file) is False:
            m = StaticMap(600, 400)
            marker = CircleMarker((long, lat), 'red', 12)
            m.add_marker(marker)
            image = m.render(zoom)
            image.save(out_file)
        return out_file
