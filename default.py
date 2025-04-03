import os
import sys
import sqlite3
import locale
from datetime import datetime
from urllib.parse import parse_qs
from urllib.parse import urlencode

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.common import Common
from resources.lib.cache import Cache
from resources.lib.map import Map


if __name__ == '__main__':

    # ロケール設定（日付フォーマットのため）
    locale.setlocale(locale.LC_ALL, '')

    # photoslibrary配下のディレクトリ/DB
    #lib_path = os.path.join(os.getenv('HOME'), 'Pictures', Common.STR(30000))
    lib_path = Common.GET('libpath')
    db_path = os.path.join(lib_path, 'database', 'Photos.sqlite')
    img_dir = os.path.join(lib_path, 'resources', 'derivatives', 'masters')
    org_dir = os.path.join(lib_path, 'originals')

    # DB初期化（Photos.sqlite）
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # epoch時間変換関数
        def strftime(epochtime, format='%Y-%m-%d %H:%M:%S'):
            return datetime.fromtimestamp(epochtime + 978307200).strftime(format)
        conn.create_function('STRFTIME', -1, strftime)
    else:
        Common.notify(Common.STR(30500))
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)        
        sys.exit()

    # DB初期化（data.db）
    conn2 = sqlite3.connect(os.path.join(Common.DATA_PATH, 'data.db'))
    cursor2 = conn2.cursor()

    # 祝祭日判定
    def is_holiday(date):
        sql = 'SELECT COUNT(date) FROM holidays WHERE date = :date'
        cursor2.execute(sql, {'date': date})
        count, = cursor2.fetchone()
        return count > 0

    # 検索結果表示
    def show_photos(cursor):
        for uuid, kind, dirname, filename, lat, long, timestamp in cursor.fetchall():
            img_path = os.path.join(img_dir, dirname, '%s_4_5005_c.jpeg' % uuid)
            org_path = os.path.join(org_dir, dirname, filename)
            is_video = kind == 1 and os.path.exists(org_path)
            has_latlong = lat > -180.0 and long > -180.0
            if kind in (0, 1) and os.path.exists(img_path):
                # タイトル
                title = Common.datetime(timestamp).strftime(Common.STR(30919))  # 2025年01月23日(木) 12:34
                w = Common.weekday(timestamp)
                if w == 6 or is_holiday(timestamp[:10]):  # 日曜日/祝祭日
                    title = [f'[COLOR red]{title}[/COLOR]']
                elif w == 5:  # 土曜日
                    title = [f'[COLOR blue]{title}[/COLOR]']
                else:
                    title = [title]
                if has_latlong:
                    title.append('[COLOR lightgreen][GPS][/COLOR]')
                if is_video:
                    title.append('[COLOR lightgreen][VIDEO][/COLOR]')
                # アクション
                if os.path.exists(org_path):
                    _, ext = os.path.splitext(org_path)
                    ext = ext[1:].lower()
                    if kind == 1:
                        action, path = 'play_media', org_path
                    elif ext == 'heic':
                        action, path = 'show_picture', Cache().convert(uuid, org_path)
                    else:
                        action, path = 'show_picture', org_path
                else:
                    action, path = 'show_picture', img_path
                # 表示
                item = xbmcgui.ListItem(' '.join(title))
                item.setArt({'icon': img_path, 'thumb': img_path})
                contextmenu = []
                if has_latlong:
                    contextmenu.append((Common.STR(30014), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'action': 'show_map', 'uuid': uuid, 'lat': lat, 'long': long}))))
                    contextmenu.append((Common.STR(30011), 'Container.Update(%s?%s)' % (sys.argv[0], urlencode({'action': 'search_nearby', 'lat': lat, 'long': long}))))
                contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
                item.addContextMenuItems(contextmenu, replaceItems=True)
                url = '%s?%s' % (sys.argv[0], urlencode({'action': action, 'path': path}))
                xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    #
    # トップ
    #

    args = parse_qs(sys.argv[2][1:])
    for key in args.keys():
        args[key] = args[key][0]

    action = args.get('action', None)
    if action is None:
        # ライブラリ
        item = xbmcgui.ListItem(Common.STR(30001))
        item.setArt({'icon': Common.CALENDAR, 'thumb': Common.CALENDAR})
        contextmenu = []
        contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
        item.addContextMenuItems(contextmenu, replaceItems=True)
        query = urlencode({'action': 'select_years'})
        url = '%s?%s' % (sys.argv[0], query)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        # ピープル
        item = xbmcgui.ListItem(Common.STR(30003))
        item.setArt({'icon': Common.PEOPLE, 'thumb': Common.PEOPLE})
        contextmenu = []
        contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
        item.addContextMenuItems(contextmenu, replaceItems=True)
        query = urlencode({'action': 'select_people'})
        url = '%s?%s' % (sys.argv[0], query)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        # モーメント
        item = xbmcgui.ListItem(Common.STR(30006))
        item.setArt({'icon': Common.MOMENT, 'thumb': Common.MOMENT})
        contextmenu = []
        contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
        item.addContextMenuItems(contextmenu, replaceItems=True)
        query = urlencode({'action': 'select_moments'})
        url = '%s?%s' % (sys.argv[0], query)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        #
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    #
    # ピープル選択＆検索
    #

    elif action == 'select_people':
        sql = '''SELECT DISTINCT ZPERSON.ZFULLNAME AS FULL_NAME
        FROM ZPERSON
        INNER JOIN ZDETECTEDFACE ON ZPERSON.Z_PK=ZDETECTEDFACE.ZPERSONFORFACE
        INNER JOIN ZASSET ON ZDETECTEDFACE.ZASSETFORFACE=ZASSET.Z_PK
        WHERE ZPERSON.ZFULLNAME IS NOT ""'''
        cursor.execute(sql)
        for person, in cursor.fetchall():
            item = xbmcgui.ListItem(person)
            item.setArt({'icon': Common.PEOPLE, 'thumb': Common.PEOPLE})
            contextmenu = []
            contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'search_people', 'person': person})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)
    elif action == 'search_people':
        sql = '''SELECT DISTINCT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZPERSON
        INNER JOIN ZDETECTEDFACE ON ZPERSON.Z_PK=ZDETECTEDFACE.ZPERSONFORFACE
        INNER JOIN ZASSET ON ZDETECTEDFACE.ZASSETFORFACE=ZASSET.Z_PK
        WHERE ZPERSON.ZFULLNAME = :person
        ORDER BY ZASSET.ZDATECREATED DESC'''
        cursor.execute(sql, {'person': args.get('person')})
        show_photos(cursor)

    #
    # モーメント選択＆検索
    #

    elif action == 'select_moments':
        sql = '''SELECT DISTINCT ZTITLE
        FROM ZMOMENT
        WHERE ZTITLE IS NOT NULL
        ORDER BY ZAPPROXIMATELATITUDE DESC'''
        cursor.execute(sql)
        for title, in cursor.fetchall():
            item = xbmcgui.ListItem(title)
            item.setArt({'icon': Common.MOMENT, 'thumb': Common.MOMENT})
            contextmenu = []
            contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'search_moments', 'title': title})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)
    elif action == 'search_moments':
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET JOIN ZMOMENT ON ZASSET.ZMOMENT = ZMOMENT.Z_PK
        WHERE ZMOMENT.ZTITLE = :title
        ORDER BY ZASSET.ZDATECREATED'''
        cursor.execute(sql, {'title': args.get('title')})
        show_photos(cursor)

    #
    # 日付選択
    #

    elif action == 'select_years':
        sql = '''SELECT DISTINCT STRFTIME(ZDATECREATED, '%Y')
        FROM ZASSET
        ORDER BY ZDATECREATED DESC'''
        cursor.execute(sql)
        for year, in cursor.fetchall():
            title = Common.datetime(f'{year}').strftime(Common.STR(30916))  # 2025年
            item = xbmcgui.ListItem(title)
            item.setArt({'icon': Common.CALENDAR, 'thumb': Common.CALENDAR})
            contextmenu = []
            contextmenu.append((Common.STR(30010) % title, 'Container.Update(%s?%s)' % (sys.argv[0], urlencode({'action': 'search_year', 'year': year}))))
            contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'select_months', 'year': year})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)
    elif action == 'select_months':
        year = args.get('year')
        sql = '''SELECT DISTINCT STRFTIME(ZDATECREATED, '%m')
        FROM (SELECT * FROM ZASSET WHERE STRFTIME(ZDATECREATED, '%Y') = :year)
        ORDER BY ZDATECREATED'''
        cursor.execute(sql, {'year': year})
        for month, in cursor.fetchall():
            title = Common.datetime(f'{year}-{month}').strftime(Common.STR(30917))  # 2025年03月
            item = xbmcgui.ListItem(title)
            item.setArt({'icon': Common.CALENDAR, 'thumb': Common.CALENDAR})
            contextmenu = []
            contextmenu.append((Common.STR(30010) % title, 'Container.Update(%s?%s)' % (sys.argv[0], urlencode({'action': 'search_month', 'year': year, 'month': month}))))
            contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'select_days', 'year': year, 'month': month})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)
    elif action == 'select_days':
        year = args.get('year')
        month = args.get('month')
        sql = '''SELECT DISTINCT STRFTIME(ZDATECREATED, '%d')
        FROM (SELECT * FROM ZASSET WHERE STRFTIME(ZDATECREATED, '%Y-%m') = :month)
        ORDER BY ZDATECREATED'''
        cursor.execute(sql, {'month': f'{year}-{month}'})
        for day, in cursor.fetchall():
            title = Common.datetime(f'{year}-{month}-{day}').strftime(Common.STR(30918))  # 2025年03月06日(木)
            w = Common.weekday(f'{year}-{month}-{day}')
            if w == 6 or is_holiday(f'{year}-{month}-{day}'):  # 日曜日/祝祭日
                title = f'[COLOR red]{title}[/COLOR]'
            elif w == 5:  # 土曜日
                title = f'[COLOR blue]{title}[/COLOR]'
            item = xbmcgui.ListItem(title)
            item.setArt({'icon': Common.CALENDAR, 'thumb': Common.CALENDAR})
            contextmenu = []
            contextmenu.append((Common.STR(30015), 'Addon.OpenSettings(%s)' % Common.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'search_day', 'year': year, 'month': month, 'day': day})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    #
    # 日付指定検索
    #

    elif action == 'search_year':
        year = args.get('year')
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE STRFTIME(ZDATECREATED, '%Y') = :year
        ORDER BY ZDATECREATED'''
        cursor.execute(sql, {'year': f'{year}'})
        show_photos(cursor)
    elif action == 'search_month':
        year = args.get('year')
        month = args.get('month')
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE STRFTIME(ZDATECREATED, '%Y-%m') = :month
        ORDER BY ZDATECREATED'''
        cursor.execute(sql, {'month': f'{year}-{month}'})
        show_photos(cursor)
    elif action == 'search_day':
        year = args.get('year')
        month = args.get('month')
        day = args.get('day')
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE STRFTIME(ZDATECREATED, '%Y-%m-%d') = :day
        ORDER BY ZDATECREATED'''
        cursor.execute(sql, {'day': f'{year}-{month}-{day}'})
        show_photos(cursor)

    #
    # 周辺撮影地検索
    #

    elif action == 'search_nearby':
        # 東京近辺の10kmあたりの度数差
        # 緯度（南北） 約 0.0898 度
        # 経度（東西） 約 0.1108 度
        lat = args.get('lat')
        long = args.get('long')
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE ABS(ZASSET.ZLATITUDE - :lat)/0.0898 < 1 AND ABS(ZASSET.ZLONGITUDE - :long)/0.1108 < 1
        ORDER BY ABS(ZASSET.ZLATITUDE - :lat)/0.0898 + ABS(ZASSET.ZLONGITUDE - :long)/0.1108
        LIMIT 100'''
        cursor.execute(sql, {'lat': float(lat), 'long': float(long)})
        show_photos(cursor)

    #
    # その他
    #

    elif action == 'show_picture':
        xbmc.executebuiltin('ShowPicture(%s)' % args.get('path'))
    elif action == 'play_media':
        xbmc.executebuiltin('PlayMedia(%s)' % args.get('path'))
    elif action == 'show_map':
        map_path = Map().convert(args.get('uuid'), float(args.get('lat')), float(args.get('long')))
        xbmc.executebuiltin('ShowPicture(%s)' % map_path)
    else:
        Common.log('unknown action:', action)

