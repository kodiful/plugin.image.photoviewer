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
    ADDON_URL = 'plugin://%s' % ADDON_ID

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
    MOMENT = os.path.join(ICON_PATH, 'flag.png')
    MEMORY = os.path.join(ICON_PATH, 'favourite.png')
    CALENDAR = os.path.join(ICON_PATH, 'calendar.png')

    @staticmethod
    def notify(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        # ポップアップする時間
        time = options.get('time', 10000)
        # ポップアップアイコン
        image = options.get('image', None)
        if image:
            pass
        elif options.get('error', False):
            image = 'DefaultIconError.png'
        else:
            image = 'DefaultIconInfo.png'
        # メッセージ
        messages = ' '.join(map(lambda x: str(x), messages))
        # ログ出力
        Common.log(messages, error=options.get('error', False))
        # ポップアップ通知
        xbmc.executebuiltin('Notification("%s","%s",%d,"%s")' % (addon.getAddonInfo('name'), messages, time, image))

    @staticmethod
    def log(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        # ログレベル、メッセージを設定
        if isinstance(messages[0], Exception):
            level = xbmc.LOGERROR
            message = '\n'.join([
                ''.join(list(traceback.TracebackException.from_exception(messages[0]).format())),
                ' '.join(map(lambda x: str(x), messages[1:]))
            ])
        else:
            level = xbmc.LOGINFO
            frame = inspect.currentframe().f_back
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            name = frame.f_code.co_name
            message = ': '.join([
                addon.getAddonInfo('id'),
                f'{filename}({lineno}) {name}',
                ' '.join(map(lambda x: str(x), messages))])
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
