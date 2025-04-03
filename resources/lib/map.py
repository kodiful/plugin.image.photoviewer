# -*- coding: utf-8 -*-

import os
import sys
import shutil

from resources.lib.common import Common

# staticmap
sys.path.append(os.path.join(Common.RESOURCES_PATH, 'extra'))
from staticmap import StaticMap, CircleMarker


class Map:

    ZOOM = 15

    def __init__(self):
        # キャッシュディレクトリ
        self.cache = os.path.join(Common.PROFILE_PATH, 'cache', 'staticmap')
        # ディレクトリが無ければ作成
        os.makedirs(self.cache, exist_ok=True)

    def clear(self):
        shutil.rmtree(self.cache)

    def convert(self, uuid, lat, long):
        # 出力ファイル
        out_dir = os.path.join(self.cache, uuid[0])
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f'{uuid}.png')
        # 画像変換実行
        if os.path.isfile(out_file) is False:
            m = StaticMap(600, 400)
            marker = CircleMarker((long, lat), 'red', 12)
            m.add_marker(marker)
            image = m.render(zoom=self.ZOOM)
            image.save(out_file)
        return out_file
