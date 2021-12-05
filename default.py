# -*- coding: utf-8 -*-
# We need this in order to use add-on paths like
# 'plugin://plugin.video.plexkodiconnect.MOVIES' in the Kodi video database
from logging import getLogger
import sys
import os

import xbmcvfs
import xbmcgui
import xbmcplugin
import xbmcaddon

# Import from the main pkc add-on
__addon__ = xbmcaddon.Addon(id='plugin.video.plexkodiconnect')
__temp_path__ = os.path.join(__addon__.getAddonInfo('path'), 'resources', 'lib')
__base__ = xbmcvfs.translatePath(__temp_path__.encode('utf-8'))
sys.path.append(__base__)

import transfer, loghandler

loghandler.config()
LOG = getLogger('PLEX.TVSHOWS')


def play():
    """
    Start up playback_starter in main Python thread
    """
    LOG.debug('Full sys.sys.argv received: %s', sys.argv)
    # Put the request into the 'queue'
    if not sys.argv[2]:
        # Browsing to a tv show from a tv show info dialog - picked up
        # by kodimonitor.py and its method OnAdd
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())
        return
    else:
        request = f'{sys.argv[2]}&handle={int(sys.argv[1])}'
        if 'resume:true' in sys.argv:
            request += '&resume=1'
        elif 'resume:false' in sys.argv:
            request += '&resume=0'
        transfer.plex_command(f'PLAY-{request}')
    if int(sys.argv[1]) == -1:
        # Handle -1 received, not waiting for main thread
        return
    # Wait for the result
    result = transfer.wait_for_transfer(source='main')
    if result is True:
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())
        # Tell main thread that we're done
        transfer.send(True, target='main')
    else:
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, result)


if __name__ == '__main__':
    LOG.info('PKC add-on for tv shows started')
    play()
    LOG.info('PKC add-on for tv shows stopped')
