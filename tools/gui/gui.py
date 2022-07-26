import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
from os import listdir
from os.path import isfile, join

color_bg = "#171717"

def choice_dialog(prompt, options):
	root = tkinter.Tk()

	root.geometry("400x300")
	root.resizable(False, False)
	root["background"] = color_bg

	if prompt:
		Label(root, text=prompt).pack()

	v = IntVar()

	for i, option in enumerate(options):
		Radiobutton(root, text=option, variable=v, value=i).pack(anchor="w")

	Button(text="Submit", command=root.destroy).pack()

	root.mainloop()

	if v.get() == 0:
		return None
	else:
		return options[v.get()]

def populate_listbox_with_files(messagetext, list):
	dir = filedialog.askdirectory(title=messagetext)

	for f in listdir(dir):
		if isfile(join(dir, f)):
			list.insert(tkinter.END, f)

	return dir

def label(parent, text, font, justify, row, column, padx, pady, sticky, fgcolor, bgcolor):
	label = tkinter.Label(parent=parent, text=text, font=font, justify=justify, fg=fgcolor, bg=bgcolor)
	label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)

class main_display:

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

		self.file_listbox = tkinter.Listbox(self.window, selectmode="single", width=35)
		self.file_listbox.grid(row=0, column=0, padx=16, pady=16, sticky="W, E, N, S")

		gamedir = populate_listbox_with_files("Select Game Directory", self.file_listbox)

		#
		# window init
		#
		
		self.window.mainloop()

main_display(window=tkinter.Tk(), window_title="Lobotomy Software Suite", window_resolution="800x600")