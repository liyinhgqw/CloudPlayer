# !/usr/bin/python
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
import tagpy

class Song(object):
  '''
  Metadata of a song
  '''
  def __init__(self, path=None):
    self.meta = {'path':path}
  
  @staticmethod
  def getExt(path):
    try:
      pos = path.rindex('.')
    except:
      return ''
    if not pos:
      return ''
    else:
      return path[pos:]
    
  def parseMeta(self):
    try:
      tagref = tagpy.FileRef(self.meta['path'])
      tags = tagref.tag()
      audio = tagref.audioProperties()
      title = tags.title
      artist = tags.artist
      album = tags.album
      comment = tags.comment
      genre = tags.genre
      year = tags.year
      track = tags.track
      length = audio.length
      channels = audio.channels
      bitrate = audio.bitrate
      samplerate = audio.sampleRate
    except:
      print "%s is not an audio file" % self.meta['path']
      return False
    self.meta['title'] = title
    self.meta['artist'] = artist
    self.meta['album'] = album
    self.meta['comment'] = comment
    self.meta['genre'] = genre
    self.meta['year'] = year
    self.meta['track'] = track
    self.meta['length'] = length
    self.meta['channels'] = channels
    self.meta['bitrate'] = bitrate
    self.meta['samlerate'] = samplerate
    print self.__repr__()
    return True
  
  def __repr__(self):
    return "%s/%s/%02d/%s%s" % (self.meta['artist'], 
                                   self.meta['album'], self.meta['track'], self.meta['title'], 
                                   Song.getExt(self.meta['path']))