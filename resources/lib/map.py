# -*- coding: utf-8 -*-

import os
import sys
import shutil

from resources.lib.common import Common

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

    def __init__(self):
        # キャッシュディレクトリ
        self.cache = os.path.join(self.PROFILE_PATH, 'cache', 'staticmap')
        # ディレクトリが無ければ作成
        os.makedirs(self.cache, exist_ok=True)
        # ズーム
        self.zoom = int(self.GET('zoom').split(' ')[0])

    def clear(self):
        shutil.rmtree(self.cache)

    def convert(self, uuid, lat, long):
        # 出力ファイル
        out_dir = os.path.join(self.cache, str(self.zoom), uuid[0])
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f'{uuid}.png')
        # 画像変換実行
        if os.path.isfile(out_file) is False:
            m = StaticMap(600, 400)
            marker = CircleMarker((long, lat), 'red', 12)
            m.add_marker(marker)
            image = m.render(zoom=self.zoom)
            image.save(out_file)
        return out_file
