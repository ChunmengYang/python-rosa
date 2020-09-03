#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pygame import mixer 
from time import sleep

def playmusic():
	mixer.init()
	mixer.music.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/1.wav")
	mixer.music.play()

playmusic()

while True:
	sleep(10)


