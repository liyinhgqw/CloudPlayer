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

from player.Song import Song

class PlayList(object):
  '''
  Current playing playlist
  '''
  MUSIC_PATTERN = ["*.mp3", ]
    
  def __init__(self, liblist=None):
    self.list = []
    self._lock = threading.Lock()
    if liblist:
      for lib in liblist:
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
      load_list = [filehandle for filehandle in PlayList.locate(self.MUSIC_PATTERN, lib)]
      for song_path in load_list:
        song = Song(song_path)
        if song.parseMeta():
          self.list.append(song)
    self.shuffle()
      
  def append(self, song):
    with self._lock:
      self.list.append(song)      
  def add(self, song):
    with self._lock:
      self.list.append(song)
      self.shuffle()
  def delete(self, song):
    with self._lock:
      self.list.remove(song)
      self.shuffle()
  def addList(self, song_list):
    for song in song_list:
      self.add(song)
    self.shuffle()
  def delList(self, song_list):
    for song in song_list:
      self.delete(song)
    self.shuffle()
  def size(self):
    return len(self.list)
  def shuffle(self):
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

  def __init__(self, liblist=None):
    self.__createPipeline()
    self.__tagged = False
    self.playList = PlayList(liblist)
    print self.playList.list
    if self.playList.size() > 0:
      self.nextSong()
  
  def __createPipeline(self, fake=False):
    self.__pipeline = gst.element_factory_make("playbin2", "player")
    if fake:
      fakesink = gst.element_factory_make("fakesink", "fakesink")
      self.__pipeline.set_property("video-sink", fakesink)
      self.__pipeline.set_property("audio-sink", fakesink)
    bus = self.__pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self.__onMessage)
    
    self.state = self.State.stop

  def __handleBad(self, song):
    self.stop()
    self.playList.delete(song)
    self.nextSong()
  def __onMessage(self, bus, message):
    t = message.type
    if t == gst.MESSAGE_ERROR:
      print "error: %s" % (self.cur_song.meta['path'])
      self.__handleBad(self.cur_song)
    elif t == gst.MESSAGE_TAG:
      taglist = message.parse_tag()
      for key in taglist.keys():
        try:
          if not key in self.cur_song.meta:
            self.cur_song.meta[key] = taglist[key]
        except:
          return False
      if not self.__tagged:
        self.__tagged = True
        print 'title:', self.cur_song.meta['title']
        print 'artist:', self.cur_song.meta['artist']
        print 'album:', self.cur_song.meta['album']
    elif t == gst.MESSAGE_EOS:
      self.stop()
      self.nextSong()
  
  def nextSong(self):
    self.stop()
    self.__tagged = False
    if self.playList.size() == 0:
      print 'Empty play list.'
      exit(1)
    song = self.playList.pop()
    self.play(song)
          
  def play(self, song=None):
    if self.state == self.State.playing:
      return
    elif self.state == self.State.pause and song is None:
      self.__pipeline.set_state(gst.STATE_PLAYING)
      self.state = self.State.playing
    elif song:
      self.cur_song = song
      self.__pipeline.set_property('uri', self.uri(song.meta['path']))
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
  
  def uri(self, _path):
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
  liblist = []
  for i in range(1, len(sys.argv)):
    liblist.append(sys.argv[i])
  player = Player(liblist)
  while True:
    gtk.main()
        
