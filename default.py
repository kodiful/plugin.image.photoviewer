# -*- coding: utf-8 -*-

import os
import sys
from urllib.parse import parse_qs

import xbmc

from resources.lib.common import Common
from resources.lib.app import App


# 写真ライブラリのパス
lib_path = Common.GET('libpath')

# 指定されたパスにDBがない場合は通知
if os.path.exists(os.path.join(lib_path, 'database', 'Photos.sqlite')) is False:
    Common.notify(Common.STR(30500))
    xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
    sys.exit()

# 処理インスタンス
app = App(lib_path)

# 引数
args = parse_qs(sys.argv[2][1:])
for key in args.keys():
    args[key] = args[key][0]

# アクション
action = args.get('action', None)

# トップ
if action is None:
    app.show_top()

# ピープル選択＆検索
elif action == 'select_people':
    app.select_people()

elif action == 'search_people':
    person = args.get('person')
    app.search_people(person)

# モーメント選択＆検索
elif action == 'select_moments':
    app.select_moments()

elif action == 'search_moments':
    title = args.get('title')
    app.search_moments(title)

# 日付選択
elif action == 'select_years':
    app.select_years()

elif action == 'select_months':
    year = args.get('year')
    app.select_months(year)

elif action == 'select_days':
    year = args.get('year')
    month = args.get('month')
    app.select_days(year, month)

# 日付指定検索
elif action == 'search_year':
    year = args.get('year')
    app.search_year(year)

elif action == 'search_month':
    year = args.get('year')
    month = args.get('month')
    app.search_month(year, month)

elif action == 'search_day':
    year = args.get('year')
    month = args.get('month')
    day = args.get('day')
    app.search_day(year, month, day)

# 周辺撮影地検索
elif action == 'search_nearby':
    lat = args.get('lat')
    long = args.get('long')
    app.search_nearby(float(lat), float(long))

# 地図表示
elif action == 'show_map':
    uuid = args.get('uuid')
    lat = args.get('lat')
    long = args.get('long')
    app.show_map(uuid, float(lat), float(long))

# 画像表示
elif action == 'show_picture':
    path = args.get('path')
    app.show_picture(path)

# 動画再生
elif action == 'play_media':
    path = args.get('path')
    app.play_media(path)

# 未知のアクション
else:
    app.log('unknown action:', action)

app.conn.close()
app.holiday.conn.close()
