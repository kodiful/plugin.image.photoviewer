# -*- coding: utf-8 -*-

import os
import calendar
import traceback
import inspect
from datetime import datetime

import xbmc
import xbmcaddon
import xbmcvfs


class Common:

    # アドオン情報
    ADDON = xbmcaddon.Addon()
    ADDON_ID = ADDON.getAddonInfo('id')

    STR = ADDON.getLocalizedString
    GET = ADDON.getSetting
    SET = ADDON.setSetting

    # ディレクトリパス
    PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
    PLUGIN_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
    DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
    ICON_PATH = os.path.join(DATA_PATH, 'icons')

    # サムネイル
    PICTURE = os.path.join(ICON_PATH, 'images.png')
    MOVIE = os.path.join(ICON_PATH, 'video.png')
    PEOPLE = os.path.join(ICON_PATH, 'actor.png')
    MOMENT = os.path.join(ICON_PATH, 'favourite.png')
    MEMORY = os.path.join(ICON_PATH, 'favourite.png')
    CALENDAR = os.path.join(ICON_PATH, 'calendar.png')

    # 通知
    @staticmethod
    def notify(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        name = addon.getAddonInfo('name')
        # デフォルト設定
        if options.get('error'):
            image = 'DefaultIconError.png'
            level = xbmc.LOGERROR
        else:
            image = 'DefaultIconInfo.png'
            level = xbmc.LOGINFO
        # ポップアップする時間
        duration = options.get('duration', 10000)
        # ポップアップアイコン
        image = options.get('image', image)
        # メッセージ
        messages = ' '.join(map(lambda x: str(x), messages))
        # ポップアップ通知
        xbmc.executebuiltin(f'Notification("{name}","{messages}",{duration},"{image}")')
        # ログ出力
        Common.log(messages, level=level)


    # ログ
    @staticmethod
    def log(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        # ログレベル、メッセージを設定
        if isinstance(messages[0], Exception):
            level = options.get('level', xbmc.LOGERROR)
            message = '\n'.join(list(map(lambda x: x.strip(), traceback.TracebackException.from_exception(messages[0]).format())))
            if len(messages[1:]) > 0:
                message += ': ' + ' '.join(map(lambda x: str(x), messages[1:]))
        else:
            level = options.get('level', xbmc.LOGINFO)
            frame = inspect.currentframe().f_back
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            name = frame.f_code.co_name
            id = addon.getAddonInfo('id')
            message = f'Addon "{id}", File "{filename}", line {lineno}, in {name}'
            if len(messages) > 0:
                message += ': ' + ' '.join(map(lambda x: str(x), messages))
        # ログ出力
        xbmc.log(message, level)

    @staticmethod
    def datetime(datetimestr):
        # 2023-04-20 05:00:00 -> datetime(2023, 4, 20, 5, 0, 0)
        datetimestr = datetimestr + '1970-01-01 00:00:00'[len(datetimestr):]  # padding
        date, time = datetimestr.split(' ')
        year, month, day = map(int, date.split('-'))
        h, m, s = map(int, time.split(':'))
        return datetime(year, month, day, h, m, s)

    @staticmethod
    def weekday(datetimestr):
        # 2023-04-20 05:00:00 -> calendar.weekday(2023, 4, 20) -> 3
        datetimestr = datetimestr + '1970-01-01 00:00:00'[len(datetimestr):]  # padding
        date, _ = datetimestr.split(' ')
        year, month, day = map(int, date.split('-'))
        return calendar.weekday(year, month, day)
