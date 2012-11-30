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

class Player(object):
  '''
  Player for the client
  '''
  
  class State(object):
    playing = 0
    pause = 1
    stop = 2

  def __init__(self):
    self.__pipeline = gst.element_factory_make("playbin", "player")
    self.state = self.State.stop
    
  def play(self, song=None):
    if self.state == self.State.playing:
      return
    elif self.state == self.State.pause and song is None:
      self.__pipeline.set_state(gst.STATE_PLAYING)
    else:  
      self.cur_song = os.path.abspath(song)
      self.__pipeline.set_property('uri', self.__uri(song))
      print self.__uri(song)
      self.__pipeline.set_state(gst.STATE_PLAYING)
    self.state = self.State.playing
    
  
  def pause(self):
    if self.state == self.State.stop:
      return
    self.__pipeline.set_state(gst.STATE_PAUSED)
    self.state = self.State.pause
  
  def stop(self):
    self.__pipeline.set_state(gst.STATE_READY)
  
  def __uri(self, _path):
    return 'file://' + os.path.abspath(_path)
  

class PlayList(object):
  '''
  Current playing playlist
  '''
  def __init__(self):
    self.list = []
    self._lock = threading.Lock()
  
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
    with self._lock:
      self.shuffle()
  def delList(self, song_list):
    for song in song_list:
      self.delete(song)
    with self._lock:
      self.shuffle()
  def size(self):
    return len(self.list)
  def shuffle(self):
    with self._lock:
      self.indices = shuffle(range(0, self.size()))
  def pop(self):
    with self._lock:
      if self.size() == 0:
        yield None
      head = self.indices[0]
      self.indices.pop()
      self.indices.append(head)
      yield self.list[head]  
    
  
if __name__ == '__main__':
  player = Player()
  player.play(sys.argv[1])
  gtk.main()
        
