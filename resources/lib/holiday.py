# -*- coding: utf-8 -*-

import sqlite3
import locale

from resources.lib.common import Common


class Holiday(Common):

    def __init__(self, db_path):
        # ロケール設定（日付フォーマットのため）
        locale.setlocale(locale.LC_ALL, '')
        # DB初期化
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def is_holiday(self, date):
        sql = 'SELECT date FROM holidays WHERE date = :date'
        self.cursor.execute(sql, {'date': date})
        result = self.cursor.fetchone()
        return result

    def convert(self, timestamp, format):
        # timestamp: 2025-04-05 12:34:00
        # format: %Y年%m月%d日(%a) %H:%M
        # return: [COLOR blue]2025年04月05日(土) 12:34[/COLOR]
        text = Common.datetime(timestamp).strftime(format)
        w = Common.weekday(timestamp)
        if w == 6 or self.is_holiday(timestamp[:10]):
            # 日曜日/祝祭日
            text = f'[COLOR red]{text}[/COLOR]'
        elif w == 5:
            # 土曜日
            text = f'[COLOR blue]{text}[/COLOR]'
        return text
