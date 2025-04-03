# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

from resources.lib.common import Common


class Cache:

    def __init__(self):
        # キャッシュディレクトリ
        self.cache = os.path.join(Common.PROFILE_PATH, 'cache', 'heic2jpeg')
        # ディレクトリが無ければ作成
        os.makedirs(self.cache, exist_ok=True)

    def clear(self):
        shutil.rmtree(self.cache)

    def convert(self, uuid, heic_file):
        # 出力ファイル
        out_dir = os.path.join(self.cache, uuid[0])
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f'{uuid}.jpeg')
        # 画像変換実行
        # rasberry piでは以下を実行してheif-convertをインストールする
        # > sudo apt install libheif-examples
        if os.path.isfile(out_file) is False:
            #command = 'sips --setProperty format jpeg "{infile}" --out "{outfile}"'.format(infile=heic_file, outfile=out_file)
            command = 'heif-convert "{infile}" "{outfile}"'.format(infile=heic_file, outfile=out_file)
            subprocess.call(command, shell=True)
        return out_file
