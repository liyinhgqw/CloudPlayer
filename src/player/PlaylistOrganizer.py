#!/usr/bin/python
import pygst
pygst.require("0.10")
import gst
import pygtk
import gtk
import gtk.glade
import os
import sys
import shutil
import threading
from random import shuffle

from player.Song import Song
from player.Player import PlayList

class PlaylistOrganizer(object):
  '''
  organize play list
  '''

  @staticmethod
  def organize(src, target=None):
    overlap = False
    if target is None:
      overlap = True
      target = src + ".tmp"
    bitrates = {}
    load_list = [filehandle for filehandle in PlayList.locate(PlayList.MUSIC_PATTERN, src)]
    for song_path in load_list:
      song = Song(song_path)
      if song.parseMeta():
        target_path = os.path.join(target, repr(song))
        if target_path in bitrates:
          if song.meta['bitrate'] <= bitrates[target_path]:
            continue
        bitrates[target_path] = song.meta['bitrate']
        try:
          os.makedirs(os.path.dirname(target_path))
        except:
          pass
        try:
          shutil.copy2(song_path, target_path)
        except:
          pass
    
    shutil.rmtree(src)
    if overlap:
      try:
        shutil.move(target, src)
      except:
        pass
if __name__ == '__main__':
  PlaylistOrganizer.organize(sys.argv[1])
  