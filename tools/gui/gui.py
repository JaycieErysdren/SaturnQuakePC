# python modules
import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import os
import os.path
from os import listdir
from os.path import isfile, join, splitext, exists
import numpy
import wave

# custom modules
import kaitaistruct
from lev_quake import LevQuake

# defs
color_bg = "#171717"
color_bg_dark = "black"
color_text = "white"

class main_display:

	#
	# funcs
	#

	def send_message(self, message):
		message += "\n"
		self.console.insert(INSERT, message)
		self.console.see("end")
		print(message)

	def add_file_info(self, message):
		message += "\n"
		self.file_info.insert(INSERT, message)
		self.file_info.see("end")

	def choose_gamedir(self):
		self.gamedir = self.populate_listbox_with_files("Select Game Directory", self.file_listbox)
		self.send_message(message=f"Game directory: {self.gamedir}")

	def populate_listbox_with_files(self, message, list):
		dir = filedialog.askdirectory(title=message)

		if not dir or dir == "":
			self.file_info.delete('1.0', END)
			self.clear_frame(self.actions_frame)
			self.file_listbox.delete(0, END)
			self.add_action_message(text="No file loaded.")
			self.send_message(message="Error: User did not select directory, exiting.")
			return

		for f in listdir(dir):
			if isfile(join(dir, f)):
				list.insert(tkinter.END, f)

		return dir

	def parse_pic(self, filepath):
		self.send_message(message="TODO: add support for this")
		self.add_action_message(text="TODO: add support for this")

	def parse_lev(self, filepath):
		self.lev = LevQuake.from_file(filepath)
		if self.lev:
			# tell user it's loaded
			self.send_message(message="Found: SlaveDriver Engine Level (Quake)")
			# fill out information
			self.add_file_info(message="Type: SlaveDriver Engine Level (Quake)")
			self.add_file_info(message="")
			self.add_file_info(message=f"Level Name: {self.lev.level_name}")
			self.add_file_info(message="\n")
			self.add_file_info(message="Geometry Data:")
			self.add_file_info(message=f"Vertices: {self.lev.header.num_vertices}")
			self.add_file_info(message=f"Nodes: {self.lev.header.num_nodes}")
			self.add_file_info(message=f"Planes: {self.lev.header.num_planes}")
			self.add_file_info(message=f"Quads: {self.lev.header.num_quads}")
			self.add_file_info(message=f"Tiles: {self.lev.header.num_tile_entries}")
			self.add_file_info(message="")
			self.add_file_info(message="Entity Data:")
			self.add_file_info(message=f"Entities: {self.lev.header.num_entities}")
			self.add_file_info(message=f"Entity Polylinks: {self.lev.header.num_entity_polylinks}")
			self.add_file_info(message="")
			self.add_file_info(message="Resource Data:")
			self.add_file_info(message=f"Sounds: {self.lev.resources.num_sounds}")
			self.add_file_info(message=f"Resources: {self.lev.resources.num_resources}")
			# add action buttons
			self.add_action_button(text="Extract Sounds", command=self.lev_extract_sounds)
		else:
			self.unknown_file()

	def lev_extract_sounds(self):
		output_dir = filedialog.askdirectory(title="Select Output Directory")

		for i, sound in enumerate(self.lev.resources.sounds):
			num_channels = 1
			samples_per_second = 11025
			bytes_per_sample = sound.bits / 8
			bytes_per_frame = num_channels * bytes_per_sample
			num_frames = sound.len_samples / bytes_per_frame

			wav_path = f"{output_dir}{self.lev.level_name}_sound{i:03d}.wav"

			if sound.bits == 8:
				s8_samples = numpy.frombuffer(sound.samples, dtype='i1')
				u8_samples = (s8_samples+128).astype('u1')
				samples = u8_samples.tobytes()
			elif sound.bits == 16:
				s16be_samples = numpy.frombuffer(sound.samples, dtype='>i2')
				s16le_samples = s16be_samples.astype('<i2')
				samples = s16le_samples.tobytes()
			else:
				raise ValueError("Expected 8 or 16 bit samples, but found something else!")

			w = wave.open(wav_path, "wb")
			w.setnchannels(num_channels)
			w.setsampwidth(bytes_per_sample)
			w.setframerate(samples_per_second)
			w.setnframes(num_frames)
			w.writeframes(samples)
			w.close()

	def unknown_file(self):
		self.file_info.delete('1.0', END)
		self.clear_frame(self.actions_frame)
		self.send_message(message="Error: Unknown file extension or type.")
		self.add_action_message(text="No actions for this format.")

	def parse_file(self, event):
		self.file_info.delete('1.0', END)
		self.clear_frame(self.actions_frame)
		filename = self.file_listbox.get(self.file_listbox.curselection())
		self.send_message(message=f"Parsing file: {filename}")
		filepath = join(self.gamedir, filename)
		name = splitext(filename)[0].lower()
		ext = splitext(filename)[1].lower()

		if not exists(filepath):
			self.file_info.delete('1.0', END)
			self.clear_frame(self.actions_frame)
			self.send_message(message="Error: Could not find the file.")
			self.add_action_message(text="No file loaded.")
			return

		match ext:
			case ".lev": self.parse_lev(filepath)
			case ".pic": self.parse_pic(filepath)
			case _: self.unknown_file()

	def clear_frame(self, frame):
		for widget in frame.winfo_children():
			widget.destroy()

	def add_action_button(self, text, command):
		button = tkinter.Button(self.actions_frame, text=text, command=command, width=224)
		button.pack(side=TOP, pady=(0, 8))

	def add_action_message(self, text):
		message = tkinter.Label(self.actions_frame, text=text, font=self.font_body, justify=LEFT, fg=color_text, bg=color_bg)
		message.pack(side=TOP, anchor="nw")

	#
	# main loop
	#

	def __init__(self, window, window_title, window_resolution):

		#
		# window setup
		#
		
		self.window = window
		self.window.title(window_title)
		self.window.geometry(window_resolution)
		self.window.resizable(False, False)
		self.window["background"] = color_bg
		
		#
		# defs
		#
		
		# text styling
		self.font_header = "Arial 20 bold"
		self.font_subheader = "Arial 16 bold"
		self.font_body = "Arial 12"
		self.font_body_bold = "Arial 12 bold"
		self.font_small = "Arial 9"
		self.font_small_bold = "Arial 9 bold"

		#
		# main window
		#

		# file listbox

		self.file_listbox_header = tkinter.Label(self.window, text="Files", font=self.font_subheader, justify=LEFT, fg=color_text, bg=color_bg)
		self.file_listbox_header.place(x=16, y=16)

		self.file_listbox = tkinter.Listbox(self.window, selectmode="single", fg=color_text, bg=color_bg_dark)
		self.file_listbox.bind('<Double-Button-1>', self.parse_file)
		self.file_listbox.place(x=16, y=48, width=192, height=320)

		self.file_listbox_loadbutton = tkinter.Button(self.window, text="Choose Directory", command=self.choose_gamedir)
		self.file_listbox_loadbutton.place(x=16, y=384)

		# file info

		self.file_info_header = tkinter.Label(self.window, text="File Info", font=self.font_subheader, justify=LEFT, fg=color_text, bg=color_bg)
		self.file_info_header.place(x=224, y=16)

		self.file_info = tkinter.Text(self.window, fg=color_text, bg=color_bg_dark, height=20)
		self.file_info.place(x=224, y=48, width=320, height=320)

		# actions

		self.actions_header = tkinter.Label(self.window, text="Actions", font=self.font_subheader, justify=LEFT, fg=color_text, bg=color_bg)
		self.actions_header.place(x=560, y=16)

		self.actions_frame = tkinter.Frame(self.window, bg=color_bg)
		self.actions_frame.place(x=560, y=48, width=224, height=320)

		self.add_action_message(text="No file loaded.")

		# console

		self.console_header = tkinter.Label(self.window, text="Console", font=self.font_subheader, justify=LEFT, fg=color_text, bg=color_bg)
		self.console_header.place(x=16, y=424)

		self.console = tkinter.Text(self.window, fg=color_text, bg=color_bg_dark)
		self.console.place(x=16, y=456, width=768, height=128)

		#
		# window init
		#
		
		self.window.mainloop()

main_display(window=tkinter.Tk(), window_title="SlaveDriver Engine Suite", window_resolution="800x600")