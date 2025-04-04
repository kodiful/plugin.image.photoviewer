# -*- coding: utf-8 -*-

import os
import sys
import locale
import sqlite3
from datetime import datetime
from urllib.parse import urlencode

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.common import Common
from resources.lib.holiday import Holiday
from resources.lib.cache import Cache
from resources.lib.map import Map


class App(Common):

    def __init__(self, lib_path):
        # ロケール設定（日付フォーマットのため）
        locale.setlocale(locale.LC_ALL, '')
        # photoslibrary配下のディレクトリ
        self.img_dir = os.path.join(lib_path, 'resources', 'derivatives', 'masters')
        self.org_dir = os.path.join(lib_path, 'originals')
        # DB初期化
        self.conn = sqlite3.connect(os.path.join(lib_path, 'database', 'Photos.sqlite'))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # epoch時間変換関数
        def strftime(epochtime, format='%Y-%m-%d %H:%M:%S'):
            return datetime.fromtimestamp(epochtime + 978307200).strftime(format)
        self.conn.create_function('STRFTIME', -1, strftime)
        # 祝祭日判定クラス初期化
        self.holiday = Holiday(os.path.join(self.DATA_PATH, 'data.db'))

    # 検索結果表示
    def show_photos(self):
        for uuid, kind, dirname, filename, lat, long, timestamp in self.cursor.fetchall():
            img_path = os.path.join(self.img_dir, dirname, '%s_4_5005_c.jpeg' % uuid)
            org_path = os.path.join(self.org_dir, dirname, filename)
            is_video = kind == 1 and os.path.exists(org_path)
            has_latlong = lat > -180.0 and long > -180.0
            if kind in (0, 1) and os.path.exists(img_path):
                # タイトル
                title = [self.holiday.convert(timestamp, self.STR(30919))]  # 2025年01月23日(木) 12:34
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
                    contextmenu.append((self.STR(30014), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'action': 'show_map', 'uuid': uuid, 'lat': lat, 'long': long}))))
                    contextmenu.append((self.STR(30011), 'Container.Update(%s?%s)' % (sys.argv[0], urlencode({'action': 'search_nearby', 'lat': lat, 'long': long}))))
                contextmenu.append((self.STR(30016), 'Container.Update(%s)' % sys.argv[0]))
                contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
                item.addContextMenuItems(contextmenu, replaceItems=True)
                url = '%s?%s' % (sys.argv[0], urlencode({'action': action, 'path': path}))
                xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    def show_count(self, count):
        return f'[COLOR khaki]▶ {count} photos[/COLOR]'

    # トップ
    def show_top(self):
        item = xbmcgui.ListItem(self.STR(30001))
        item.setArt({'icon': self.CALENDAR, 'thumb': self.CALENDAR})
        contextmenu = []
        contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
        item.addContextMenuItems(contextmenu, replaceItems=True)
        query = urlencode({'action': 'select_years'})
        url = '%s?%s' % (sys.argv[0], query)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        # ピープル
        item = xbmcgui.ListItem(self.STR(30003))
        item.setArt({'icon': self.PEOPLE, 'thumb': self.PEOPLE})
        contextmenu = []
        contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
        item.addContextMenuItems(contextmenu, replaceItems=True)
        query = urlencode({'action': 'select_people'})
        url = '%s?%s' % (sys.argv[0], query)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        # モーメント
        item = xbmcgui.ListItem(self.STR(30006))
        item.setArt({'icon': self.MOMENT, 'thumb': self.MOMENT})
        contextmenu = []
        contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
        item.addContextMenuItems(contextmenu, replaceItems=True)
        query = urlencode({'action': 'select_moments'})
        url = '%s?%s' % (sys.argv[0], query)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        #
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    # ピープル選択＆検索
    def select_people(self):
        sql = '''SELECT ZPERSON.ZFULLNAME AS FULL_NAME, COUNT(*)
        FROM ZPERSON
        INNER JOIN ZDETECTEDFACE ON ZPERSON.Z_PK=ZDETECTEDFACE.ZPERSONFORFACE
        INNER JOIN ZASSET ON ZDETECTEDFACE.ZASSETFORFACE=ZASSET.Z_PK
        WHERE ZFULLNAME IS NOT ""
        GROUP BY FULL_NAME'''
        self.cursor.execute(sql)
        for person, count in self.cursor.fetchall():
            item = xbmcgui.ListItem(' '.join([person, self.show_count(count)]))
            item.setArt({'icon': self.PEOPLE, 'thumb': self.PEOPLE})
            contextmenu = []
            contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'search_people', 'person': person})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    def search_people(self, person):
        sql = '''SELECT DISTINCT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZPERSON
        INNER JOIN ZDETECTEDFACE ON ZPERSON.Z_PK=ZDETECTEDFACE.ZPERSONFORFACE
        INNER JOIN ZASSET ON ZDETECTEDFACE.ZASSETFORFACE=ZASSET.Z_PK
        WHERE ZPERSON.ZFULLNAME = :person
        ORDER BY ZASSET.ZDATECREATED DESC'''
        self.cursor.execute(sql, {'person': person})
        self.show_photos()

    # モーメント選択＆検索
    def select_moments(self):
        sql = '''SELECT ZMOMENT.ZTITLE, COUNT(*)
        FROM ZASSET JOIN ZMOMENT ON ZASSET.ZMOMENT = ZMOMENT.Z_PK
        WHERE ZMOMENT.ZTITLE IS NOT NULL AND ZMOMENT.ZENDDATE > ZMOMENT.ZSTARTDATE
        GROUP BY ZMOMENT.ZTITLE
        ORDER BY ZMOMENT.ZAPPROXIMATELATITUDE DESC'''
        self.cursor.execute(sql)
        for title, count in self.cursor.fetchall():
            item = xbmcgui.ListItem(' '.join([title, self.show_count(count)]))
            item.setArt({'icon': self.MOMENT, 'thumb': self.MOMENT})
            contextmenu = []
            contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'search_moments', 'title': title})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    def search_moments(self, title):
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET JOIN ZMOMENT ON ZASSET.ZMOMENT = ZMOMENT.Z_PK
        WHERE ZMOMENT.ZTITLE = :title
        ORDER BY ZASSET.ZDATECREATED'''
        self.cursor.execute(sql, {'title': title})
        self.show_photos()

    # 日付選択
    def select_years(self):
        sql = '''SELECT STRFTIME(ZDATECREATED, '%Y'), COUNT(*)
        FROM ZASSET
        GROUP BY STRFTIME(ZDATECREATED, '%Y')
        ORDER BY ZDATECREATED DESC'''
        self.cursor.execute(sql)
        for year, count in self.cursor.fetchall():
            title = self.datetime(f'{year}').strftime(self.STR(30916))
            item = xbmcgui.ListItem(' '.join([title, self.show_count(count)]))
            item.setArt({'icon': self.CALENDAR, 'thumb': self.CALENDAR})
            contextmenu = []
            contextmenu.append((self.STR(30010) % title, 'Container.Update(%s?%s)' % (sys.argv[0], urlencode({'action': 'search_year', 'year': year}))))
            contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'select_months', 'year': year})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    def select_months(self, year):
        sql = '''SELECT STRFTIME(ZDATECREATED, '%m'), COUNT(*)
        FROM (SELECT * FROM ZASSET WHERE STRFTIME(ZDATECREATED, '%Y') = :year)
        GROUP BY STRFTIME(ZDATECREATED, '%m')
        ORDER BY ZDATECREATED'''
        self.cursor.execute(sql, {'year': year})
        for month, count in self.cursor.fetchall():
            title = self.datetime(f'{year}-{month}').strftime(self.STR(30917))
            item = xbmcgui.ListItem(' '.join([title, self.show_count(count)]))
            item.setArt({'icon': self.CALENDAR, 'thumb': self.CALENDAR})
            contextmenu = []
            contextmenu.append((self.STR(30010) % title, 'Container.Update(%s?%s)' % (sys.argv[0], urlencode({'action': 'search_month', 'year': year, 'month': month}))))
            contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'select_days', 'year': year, 'month': month})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    def select_days(self, year, month):
        sql = '''SELECT STRFTIME(ZDATECREATED, '%d'), COUNT(*)
        FROM (SELECT * FROM ZASSET WHERE STRFTIME(ZDATECREATED, '%Y-%m') = :month)
        GROUP BY STRFTIME(ZDATECREATED, '%d')
        ORDER BY ZDATECREATED'''
        self.cursor.execute(sql, {'month': f'{year}-{month}'})
        for day, count in self.cursor.fetchall():
            title = self.holiday.convert(f'{year}-{month}-{day}', self.STR(30918))
            item = xbmcgui.ListItem(' '.join([title, self.show_count(count)]))
            item.setArt({'icon': self.CALENDAR, 'thumb': self.CALENDAR})
            contextmenu = []
            contextmenu.append((self.STR(30015), 'Addon.OpenSettings(%s)' % self.ADDON_ID))
            item.addContextMenuItems(contextmenu, replaceItems=True)
            query = urlencode({'action': 'search_day', 'year': year, 'month': month, 'day': day})
            url = '%s?%s' % (sys.argv[0], query)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

    # 日付指定検索
    def search_year(self, year):
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE STRFTIME(ZDATECREATED, '%Y') = :year
        ORDER BY ZDATECREATED'''
        self.cursor.execute(sql, {'year': f'{year}'})
        self.show_photos()

    def search_month(self, year, month):
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE STRFTIME(ZDATECREATED, '%Y-%m') = :month
        ORDER BY ZDATECREATED'''
        self.cursor.execute(sql, {'month': f'{year}-{month}'})
        self.show_photos()

    def search_day(self, year, month, day):
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE STRFTIME(ZDATECREATED, '%Y-%m-%d') = :day
        ORDER BY ZDATECREATED'''
        self.cursor.execute(sql, {'day': f'{year}-{month}-{day}'})
        self.show_photos()

    # 周辺撮影地検索
    def search_nearby(self, lat, long):
        # 東京近辺の10kmあたりの度数差
        # 緯度（南北） 約 0.0898 度
        # 経度（東西） 約 0.1108 度
        range = int(self.GET('search_range').replace('km', ''))
        limit = int(self.GET('search_limit'))
        sql = '''SELECT ZASSET.ZUUID, ZASSET.ZKIND, ZASSET.ZDIRECTORY, ZASSET.ZFILENAME, ZASSET.ZLATITUDE, ZASSET.ZLONGITUDE, STRFTIME(ZASSET.ZDATECREATED)
        FROM ZASSET
        WHERE ABS(ZASSET.ZLATITUDE - :lat)/0.00898 < :range AND ABS(ZASSET.ZLONGITUDE - :long)/0.01108 < :range
        ORDER BY ABS(ZASSET.ZLATITUDE - :lat)/0.00898 + ABS(ZASSET.ZLONGITUDE - :long)/0.01108
        LIMIT :limit'''
        self.cursor.execute(sql, {'lat': lat, 'long': long, 'range': range, 'limit': limit})
        self.show_photos()

    # 地図表示
    def show_map(self, uuid, lat, long):
        path = Map().convert(uuid, lat, long)
        if path is None:
            pass
        else:
            xbmc.executebuiltin('ShowPicture(%s)' % path)

    # 画像表示
    def show_picture(self, path):
        xbmc.executebuiltin('ShowPicture(%s)' % path)

    # 動画再生
    def play_media(self, path):
        xbmc.executebuiltin('PlayMedia(%s)' % path)
