#!/usr/bin/python
# -*- coding: UTF-8 -*-

import librosa
import numpy as np
import os
import json

MUSIC_DIR_PATH = "./music"

def load_music(filepath):
	print("=========loac music %s=========" %(filepath))

	# 节拍点的音高
	beat_pitches = []
	# 节拍点的八音12度的强度
	beat_chroma = []
	# 节拍点的八音12度最强度的索引
	beat_chroma_max_index = []

	y, sr = librosa.load(filepath, sr=None)
	S = np.abs(librosa.stft(y))

	# 起点强度（音符按键起始点）
	onset_env = librosa.onset.onset_strength(y=y, sr=sr)
	# 节拍点（帧索引）
	tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
	# 节拍点 （时间点，单位秒）
	beat_times = librosa.frames_to_time(beats, sr=sr)
	
	# 频率、振幅强度，横坐标是采样点，纵坐标是帧
	pitches, magnitudes = librosa.piptrack(S=S, sr=sr)
	# 八音12度的强度
	chroma_stft = librosa.feature.chroma_stft(S=S, sr=sr)

	for beat in beats:
		index = magnitudes[:, beat].argmax()
		pitch = pitches[index, beat]
		beat_pitches.append(float(pitch))

		chromas = []
		max_chroma = 0
		max_chroma_index = 0
		chr_st_index = 0
		for chr_st in chroma_stft:
			chromas.append(chr_st[beat])

			if chr_st[beat] > max_chroma:
				max_chroma = chr_st[beat]
				max_chroma_index = chr_st_index
			chr_st_index += 1

		beat_chroma.append(chromas)
		beat_chroma_max_index.append(max_chroma_index)


	return {"beat_times": beat_times.tolist(), "beat_pitches": beat_pitches, "beat_chroma_max_index": beat_chroma_max_index}


def setup_music_data(musicfile, jsonfile):
	if os.path.exists(jsonfile):
		os.remove(jsonfile)

	data = load_music(musicfile)
	with open(jsonfile, 'w+') as f:
		json.dump(data, f)



if not os.path.exists(MUSIC_DIR_PATH) or not os.path.isdir(MUSIC_DIR_PATH):
	os.makedirs(MUSIC_DIR_PATH)

	
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
		setup_music_data(MUSIC_DIR_PATH + '/' + file, MUSIC_DIR_PATH + '/' + jsonfile)

