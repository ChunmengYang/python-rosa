#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pygame import mixer 
from time import sleep
import os
import json
import board
import neopixel

LED_PIN = board.D21
LED_COUNT = 165
LED_BRIGHTNESS = 0.2
LED_ORDER = neopixel.GRB

class COLOR:
	BLACK = (0, 0, 0)
	GREEN = (0, 255, 0)
	RED = (255, 0, 0)
	BLUE = (0, 0, 255)

pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False,
pixel_order=LED_ORDER)
pixels.fill(COLOR.GREEN)
pixels.show()

MUSIC_DIR_PATH = "./music"

def playmusic(musicfile, jsonfile):

	if not os.path.exists(jsonfile):
		return

	mixer.init()
	mixer.music.load(musicfile)

	data = None
	with open(jsonfile, 'r') as f:
		data = json.load(f)
	if data:
		beat_times = data["beat_times"]
		beat_pitches = data["beat_pitches"]
		
		pre_beat_time = 0
		index = 0
		mixer.music.play()
		for beat_time in beat_times:
			pixels.fill(COLOR.BLACK)
			pixels.show()

			if beat_pitches[index] > 700:
				sleep(beat_time - pre_beat_time - 0.04)
				pixels.fill(COLOR.RED)
				pixels.show()
			else:
				sleep(beat_time - pre_beat_time)

			pre_beat_time = beat_time
			index += 1
	
	mixer.music.stop()



dirs = os.listdir(MUSIC_DIR_PATH)
for file in dirs:
	if os.path.isdir(MUSIC_DIR_PATH + '/' + file):
		continue

	lower_file = file.lower()
	index = -1	
	if lower_file.endswith('.mp3'):
		index = lower_file.rfind('.mp3')
	elif lower_file.endswith('.wav'):
		index = lower_file.rfind('.wav')

	if index > 0:
		jsonfile = file[0:index] + '.json'
		
		playmusic(MUSIC_DIR_PATH + '/' + file, MUSIC_DIR_PATH + '/' + jsonfile)
