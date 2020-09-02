# #!/usr/bin/python
# # -*- coding: UTF-8 -*-

# from pygame import mixer 
# from time import sleep

# def playmusic():
# 	mixer.init()
# 	mixer.music.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/1.wav")
# 	mixer.music.play()

# playmusic()

# while True:
# 	sleep(10)



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
	y,sr = librosa.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/1/mp3/0001.mp3", sr=None) 
	plt.figure()
	#创建波形图
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
	y1, sr = librosa.load("/Users/mash5/Documents/python3-workspace/python-rosa/music/1/mp3/0002.mp3", sr=None)
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


sensor_value_list = [0, 0, 0, 0, 0]
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

	PATH = "/Users/mash5/Documents/python3-workspace/python-rosa/music/"
	def get_audio_series(p_index, m_index, sr):
		y_temp, sr_temp = librosa.load(PATH + str(p_index) + "/mp3/000" + str(m_index) +  ".mp3" , sr=sr)
		return y_temp, sr_temp


	def get_beats_samples(y, sr):
		_, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
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

	sr = None
	ys = []
	beats_list = []
	beat_samples_list = []
	starts = []
	s_ys = []

	for x in range(0, sensor_count):
		y, sr = get_audio_series(x + 1, 1, sr) 
		ys.append(y)
		beats, beat_samples = get_beats_samples(y, sr)
		beats_list.append(beats)
		beat_samples_list.append(beat_samples)
		starts.append(0)
		s_ys.append(0)

	s_count = sr
	while True:
		for x in range(0, sensor_count):
			if sensor_value_list[x] > 0:
				s_ys[x], starts[x] = get_fragment(ys[x], starts[x], s_count)
			else:
				s_ys[x] = 0
				starts[x] = 0

		y = s_ys[0] + s_ys[1] + s_ys[2] + s_ys[3] + s_ys[4]
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
			print(msg)
			# values = msg.split(',');
			# for x in range(0, len(values)):
			# 	values[x] = int(values[x])

			set_sensor_value(msg)
