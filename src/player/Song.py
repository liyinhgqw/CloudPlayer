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
#import tagpy
from hsaudiotag import auto

class Song(object):
  '''
  Metadata of a song
  '''
  def __init__(self, path=None):
    self.meta = {'path':path, 'artist':'', 'title':'', 'album':'', 'track':0, 'bitrate':0}
    
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
      
  # depreciated
  def parseMeta(self):
    try:      
#      tagref = tagpy.FileRef(self.meta['path'])
#      tags = tagref.tag()
#      audio = tagref.audioProperties()
#      title = tags.title
#      artist = tags.artist
#      album = tags.album
#      comment = tags.comment
#      genre = tags.genre
#      year = tags.year
#      track = tags.track
#      length = audio.length
#      channels = audio.channels
#      bitrate = audio.bitrate
#      samplerate = audio.sampleRate

      meta = auto.File(self.meta['path'])

    except:
      print "%s is not an audio file" % self.meta['path']
      return False
    self.meta['title'] = meta.title
    self.meta['artist'] = meta.artist
    self.meta['album'] = meta.album
    self.meta['comment'] = meta.comment
    self.meta['genre'] = meta.genre
    self.meta['year'] = meta.year
    self.meta['track'] = meta.track
    self.meta['size'] = meta.size
    self.meta['audio_size'] = meta.audio_size
    self.meta['audio_offset'] = meta.audio_offset
    self.meta['bitrate'] = meta.bitrate
    self.meta['samle_rate'] = meta.sample_rate
    return True
  
  def __repr__(self):
    return "%s/%s/%02d/%s%s" % (self.meta['artist'], 
                                   self.meta['album'], self.meta['track'], self.meta['title'], 
                                   Song.getExt(self.meta['path']))

  