#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import time
import threading
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np
import wave
import pyaudio


def waveplot():
	#y为长度等于采样率sr*时间的音频向量
	y, sr = librosa.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/1/mp3/0001.mp3", sr=None, mono=True)

	onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512, aggregate=np.median)

	peaks = librosa.util.peak_pick(onset_env, 3, 3, 3, 5, 0.6, 10)

	tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=512)
		
	times = librosa.frames_to_time(beats, sr=sr)

	# print(peaks)
	print(tempo)
	print(beats)
	print(times)

	plt.figure()
	#创建波形图
	# librosa.display.waveplot(y, sr)
	librosa.display.waveplot(y, sr)
	#显示波形图
	plt.show()


def remix():
	#y为长度等于采样率sr*时间的音频向量
	y1, sr1 = librosa.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/1/mp3/0001.mp3", sr=None) 
	y2, sr2 = librosa.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/2/mp3/0002.mp3", sr=None)
	y3, sr3 = librosa.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/4/mp3/0003.mp3", sr=None)

	print(y1.size)
	print(y1.dtype)
	print(y2.size)
	print(y2.dtype)

	size = 0
	if y2.size < y1.size:
		size = y2.size
	else:
		size = y1.size
	if y3.size < size:
		size = y3.size

	y1 = y1[0: size: 1]
	y2 = y2[0: size: 1]
	y3 = y3[0: size: 1]
	y4 = y1 * 1 + y2 * 1 + y3 * 1

	# librosa.output.write_wav("/Users/mash5/Documents/python3-workspace/python-rosa/music/temp.wav", y3, sr3)

	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sr1, output=True)

	audata = y4.astype(np.float32).tostring()
	stream.write(audata)

	stream.stop_stream()
	stream.close()

	p.terminate()


def beats_slice():
	#y为长度等于采样率sr*时间的音频向量
	y1, sr = librosa.load("/home/pi/Desktop/python-rosa/music/1/mp3/0002.mp3", sr=None)
	print(y1.size)
	tempo, beats = librosa.beat.beat_track(y=y1, sr=sr, hop_length=512)
	print(beats)
	beat_samples = librosa.frames_to_samples(beats, hop_length=512)
	print(beat_samples)

	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sr, output=True)


	pre_s = 0
	cur_beat_index = 0
	beat_count = len(beat_samples)
	while True:
		if cur_beat_index < beat_count:
			s = beat_samples[cur_beat_index]
			cur_beat_index += 1
			if (s - pre_s) < sr:
				continue
			else:
				y = y1[pre_s:s]
				pre_s = s
		else:
			y = y1[pre_s:]
			pre_s = 0
			cur_beat_index = 0

		audata = y.astype(np.float32).tostring()
		stream.write(audata)


	stream.stop_stream()
	stream.close()

	p.terminate()


sensor_value_list = [1, 1, 0, 1, 0]
# 设置超声波数值
def set_sensor_value(values):
	global sensor_value_list

	sensor_count = len(sensor_value_list)
	index = 0
	for value in values:
		if index < sensor_count:
			sensor_value_list[index] = value
		index += 1
		

def dy_remix():
	global sensor_value_list
	sensor_count = len(sensor_value_list)

	PATH = "/home/pi/Desktop/python-rosa/music/"
	def get_audio_series(p_index, m_index, sr):
		y_temp, sr_temp = librosa.load(PATH + str(p_index) + "/mp3/000" + str(m_index) +  ".mp3", sr=sr)
		return y_temp, sr_temp


	def get_beats_samples(y, sr):
		# 起点强度（音符按键起始点）
		onset_env = librosa.onset.onset_strength(y=y, sr=sr)
		# 节拍点（帧索引）
		_, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=512)
		# 节拍点（采样引）
		beat_samples = librosa.frames_to_samples(beats, hop_length=512)
		return beats, beat_samples

	def get_fragment(y, start, s_count):
		t_count = len(y)
		if start == t_count:
			start = 0

		s_y = None
		end = start + s_count
		if end <= t_count:
			s_y = y[start:end]
		else:
			end -= t_count
			s_y1 = y[start:]
			s_y2 = y[0:end]
			s_y = np.concatenate((s_y1, s_y2))

		return s_y, end

	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)	


	# 采样率
	sr = None
	# 每组音频数
	audios_count = 5
	# 加载所有音频数据及节奏点数据
	audios_pool = []
	beat_samples_pool = []
	for x in range(0, sensor_count):
		audios_list = []
		beat_samples_list = []
		for i in range(0, audios_count):
			y, sr = get_audio_series(x + 1, i + 1, sr) 
			beats, beat_samples = get_beats_samples(y, sr)

			audios_list.append(y)
			beat_samples_list.append(beat_samples)

		audios_pool.append(audios_list)
		beat_samples_pool.append(beat_samples_list)
		print("========%d=========",x)


	# 上一次互动参数
	pre_sensor_value_list = []
	# 互动参数对应的音频数据索引
	audio_indexs = []
	# 互动参数对应的音频数据 
	audios_list = []
	# 动参数对应的音频数据节奏点采样索引
	beat_samples_list = []
	# 当前音频播放的开始位置与播放的数据切片
	starts = []
	s_ys = []

	for x in range(0, sensor_count):
		pre_sensor_value_list.append(0)
		audio_indexs.append(0)

		audios_list.append(audios_pool[x][0])
		beat_samples_list.append(beat_samples_pool[x][0])

		starts.append(0)
		s_ys.append(0)


	def get_yield_size(sensor_value_index):
		for i in range(0, sensor_count):
			if sensor_value_index == i:
				continue
			if pre_sensor_value_list[i] > 0:
				start = starts[i]
				beat_samples = beat_samples_list[i]
				bs_count = len(beat_samples)
				for x in range(0, bs_count):
					if start < beat_samples[x]:
						t_x = x + 1
						if t_x < bs_count:
							return beat_samples[t_x] - start
						else:
							return len(audios_list[i]) - start + beat_samples[t_x - bs_count - 1]

				return len(audios_list[i]) - start + beat_samples[0]

		return 0

	s_count = sr
	while True:
		s_count = sr
		# 有互动项被启动，寻找播放该音频的开始位置
		for x in range(0, sensor_count):
			sensor_value = sensor_value_list[x]
			if pre_sensor_value_list[x] == 0 and sensor_value > 0:
				yield_size = get_yield_size(x)
				if yield_size > 0:
					s_count = yield_size
					break


		for x in range(0, sensor_count):
			sensor_value = sensor_value_list[x]
			if sensor_value > 0:
				if pre_sensor_value_list[x] > 0:
					s_ys[x], starts[x] = get_fragment(audios_list[x], starts[x], s_count)

			else:
				if pre_sensor_value_list[x] > 0:
					# 该项互动音频索引递增
					audio_indexs[x] += 1
					if audio_indexs[x] == 5:
						audio_indexs[x] = 0
					# 该项互动替换音频数据
					i = audio_indexs[x]
					audios_list[x] = audios_pool[x][i]
					beat_samples_list[x] = beat_samples_pool[x][i]
					# 该项互动播放参数清空
					s_ys[x] = 0
					starts[x] = 0

			pre_sensor_value_list[x] = sensor_value

		# 混音操作
		y = s_ys[0] + s_ys[1] + s_ys[2] + s_ys[3] + s_ys[4]
		# 播放
		if not isinstance(y, int):
			audata = y.astype(np.float32).tostring()
			stream.write(audata)


	stream.stop_stream()
	stream.close()

	p.terminate()


if __name__ == '__main__':
	audio_thread = threading.Thread(target=dy_remix, name="超声波接收线程")
	audio_thread.start()

	while True:
		msg = input("input:")
		if msg == 'c':
			sys.exit()
		else:
			values = msg.split(',');
			for x in range(0, len(values)):
				values[x] = int(values[x])

			set_sensor_value(values)
