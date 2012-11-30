#!/usr/bin/python
import pygst
pygst.require("0.10")
import gst
import pygtk
import gtk
import gtk.glade
import os
import sys
import threading
from random import shuffle

class Song(object):
  '''
  Metadata of a song
  '''
  def __init__(self, path=None):
    self.meta = {'path':path,
                 'title':'',
                 'artist':'',
                 'album':'',
                 'bitrate':'', 'minimum-bitrate':'', 'maximum-bitrate':'',
                 'container-format':'',
                 'has-crc':False,
                 'channel-mode':'',
                 'audio-codec':''}

class PlayList(object):
  '''
  Current playing playlist
  '''
  MUSIC_PATTERN = ["*.mp3", ]
    
  def __init__(self, lib=None):
    self.list = []
    self._lock = threading.Lock()
    if lib:
      self.load(lib)
  
  @staticmethod
  def locate(patterns, root):
    for path, dirs, files in os.walk(os.path.abspath(root)):
      # make the compiler happy
      dirs = dirs
      for filehandle in [os.path.abspath(os.path.join(path, filename)) for filename in files]:
        yield filehandle
            
  # lib: physical dir
  # should only be called when initialize
  def load(self, lib):
    with self._lock:
      self.list = []
      load_list = [filehandle for filehandle in PlayList.locate(self.MUSIC_PATTERN, lib)]
      for song_path in load_list:
        self.list.append(Song(song_path))
    self.shuffle()  
      
  def add(self, song):
    with self._lock:
      self.list.append(song)
  def delete(self, song):
    with self._lock:
      self.list.remove(song)
  def addList(self, song_list):
    for song in song_list:
      self.add(song)
  def delList(self, song_list):
    for song in song_list:
      self.delete(song)
  def size(self):
    return len(self.list)
  def shuffle(self):
    with self._lock:
      self.indices = range(0, self.size())
      shuffle(self.indices)
  def pop(self):
    with self._lock:
      if self.size() == 0:
        return None
      head = self.indices[0]
      nextsong = self.list[head]
      self.indices.pop(0)
      self.indices.append(head)
     
      return nextsong

  
class Player(object):
  '''
  Player for the client
  '''
  
  class State(object):
    playing = 0
    pause = 1
    stop = 2

  def __init__(self, lib=None):
    self.__createPipeline()
    self.__tagged = False
    self.playList = PlayList(lib)
    if self.playList.size() > 0:
      self.nextSong()
  
  def __createPipeline(self):
    self.__pipeline = gst.element_factory_make("playbin2", "player")
    bus = self.__pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self.__onMessage)
    
    self.state = self.State.stop

  def __onMessage(self, bus, message):
    t = message.type
    if t == gst.MESSAGE_ERROR:
      print "error ..."
    elif t == gst.MESSAGE_TAG:
      taglist = message.parse_tag()
      for key in taglist.keys():
        try:
          self.cur_song.meta[key] = taglist[key]
        except:
          return False
      if not self.__tagged:
        self.__tagged = True
        print 'title', self.cur_song.meta['title']
        print 'artist', self.cur_song.meta['artist']
        print 'album', self.cur_song.meta['album']
    elif t == gst.MESSAGE_EOS:
      self.stop()
      self.nextSong()
  
  def nextSong(self):
    self.stop()
    self.tagged = False
    song = self.playList.pop()
    self.play(song)
          
  def play(self, song=None):
    if self.state == self.State.playing:
      return
    elif self.state == self.State.pause and song is None:
      self.__pipeline.set_state(gst.STATE_PLAYING)
      self.state = self.State.playing
    elif song:
      self.cur_song = Song(os.path.abspath(song.meta['path']))
      self.__pipeline.set_property('uri', self.__uri(song.meta['path']))
      self.__pipeline.set_state(gst.STATE_PLAYING)
      self.state = self.State.playing
    
  
  def pause(self):
    if self.state == self.State.stop:
      return
    self.__pipeline.set_state(gst.STATE_PAUSED)
    self.state = self.State.pause
  
  def stop(self):
    self.__pipeline.set_state(gst.STATE_NULL)
    self.state = self.State.stop
  
  def __uri(self, _path):
    return 'file://' + os.path.abspath(_path)
  

    
class SimplePlayer(Player):
  '''
  Simple Player
  '''
  def __init__(self, lib=None):
    self.play_list = PlayList()
    if lib:
      self.play_list.load(lib)
  def shuffle(self):
    self.play_list.shuffle()
      

if __name__ == '__main__':
  player = Player(sys.argv[1])
  gtk.main()
        
