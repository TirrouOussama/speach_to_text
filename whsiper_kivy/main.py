
import gi
gi.require_version('Gst', '1.0')
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget 
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.graphics.texture import Texture
from kivy.graphics import *
from kivy.graphics import Rectangle, Color, Line, Bezier, Ellipse, Triangle
from kivy.core.clipboard import Clipboard
import time
import os
import time
import whisper
from datetime import datetime
from kivy.uix.progressbar import ProgressBar
import pyaudio
import wave
import threading

kill = False                   
rec_cond = False
stop_cond = False
finsih = False
res = ''

def record():
	global rec_cond, stop_cond, finish, res, kill
	while kill == False:
		time.sleep(0.5)
		try:
			while rec_cond == True:
				
					chunk = 1024  # Record in chunks of 1024 samples
					sample_format = pyaudio.paInt16  # 16 bits per sample
					channels = 2
					fs = 44100  # Record at 44100 samples per second
					seconds = 10
					filename = "output.wav"
					p = pyaudio.PyAudio()  # Create an interface to PortAudio
					print('Recording')
					stream = p.open(format=sample_format,
					                channels=channels,
					                rate=fs,
					                frames_per_buffer=chunk,
					                input=True)
					frames = []  # Initialize array to store frames
					# Store data in chunks for 3 seconds
					for i in range(0, int(fs / chunk * seconds)):
					    data = stream.read(chunk)
					    frames.append(data)
					    if stop_cond == True:
					    	print('stopping')
					    	break

					# Stop and close the stream 
					stream.stop_stream()
					stream.close()
					# Terminate the PortAudio interface
					p.terminate()
					print('Finished recording')

					# Save the recorded data as a WAV file
					wf = wave.open(filename, 'wb')
					wf.setnchannels(channels)
					wf.setsampwidth(p.get_sample_size(sample_format))
					wf.setframerate(fs)
					wf.writeframes(b''.join(frames))
					wf.close()
					model = whisper.load_model("small")
					result = model.transcribe('output.wav')
					print(result['text'])
					res = result['text']


					rec_cond = False
					finish = True




		except:
			print('standby')
			

thread_1 = threading.Thread(target = record)
class welcomescreen(Widget):
	def __init__(self, **kwargs):
		global rec_cond, stop_cond, finish, res
		super().__init__(**kwargs)
		self.anime_rec = False
		self.anime_stop = False
		thread_1.start()


	def copy_it(self):
		Clipboard.copy(self.ids.result_id.text)

	def record_it(self):
		global rec_cond, stop_cond, finish, res
		self.anime_rec = True
		rec_cond = True
		rec_stop = False
		finish = False
		self.ids.result_id.text = ''
		self.ids.cp_id.pos[0] = self.width*2
		Clock.schedule_interval(self.animation_rec, 1/60)
		Clock.schedule_interval(self.prog_bar, 1/10)
		Clock.schedule_interval(self.awaits, 1/10)
		print('recording btn')

	def stop_it(self):
		global rec_cond, stop_cond
		stop_cond = True
		self.anime_stop = False
		Clock.schedule_interval(self.animation_stop, 1/60)
		self.ids.prog.value = 0
		self.ids.brief.text = 'Transcribing ...'
		Clock.unschedule(self.prog_bar)

	def animation_rec(self, *args):
		if self.anime_rec == True and self.ids.rec_id.pos[0] > self.width*0.4:
			self.ids.rec_id.pos[0] = self.ids.rec_id.pos[0] - self.width*0.003
			if self.ids.rec_id.pos[0] <= self.width*0.4:
				self.ids.stop_id.pos[0] = self.width*0.5
				Clock.unschedule(self.animation_rec)

	def animation_stop(self, *args):
		if self.anime_rec == True and self.ids.rec_id.pos[0] < self.width*0.45:
			self.ids.stop_id.pos[0] = self.width*2
			self.ids.rec_id.pos[0] = self.ids.rec_id.pos[0] + self.width*0.003
			if self.ids.rec_id.pos[0] >= self.width*0.45:
				Clock.unschedule(self.animation_stop)

	def prog_bar(self, *args):
		if self.ids.prog.value != self.ids.prog.max:
			self.ids.prog.value = self.ids.prog.value + 10

			if self.ids.prog.value >= 980:
				self.ids.stop_id.pos[0] = self.width*2
				self.ids.brief.text = 'Transcribing ...'

	def awaits(self, *args):
		global finish, res
		if finish == True:
			print(len(res))
			self.ids.brief.text = ''
			self.ids.result_id.text = res
			self.ids.cp_id.pos[0] = self.width*0.55
			Clock.unschedule(self.prog_bar)
			Clock.schedule_interval(self.animation_stop, 1/60)
			Clock.unschedule(self.awaits)
			self.ids.prog.value = 0

		
class mainscreen(Widget):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)



class theapp(App):
	def build(self):	
		self.screenm = ScreenManager(transition=FadeTransition()) 
		self.welcomescreen = welcomescreen()
		screen = Screen(name = "welcomescreen")
		screen.add_widget(self.welcomescreen)
		self.screenm.add_widget(screen)

		self.mainscreen = mainscreen()
		screen = Screen(name = "mainscreen")
		screen.add_widget(self.mainscreen)
		self.screenm.add_widget(screen)

		return self.screenm

if __name__ == "__main__":

	theapp = theapp()			
	
	
	threading.Thread(target = theapp.run())
	kill = True