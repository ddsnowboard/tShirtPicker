import sqlite3
import datetime
import random
import sys
import WillsLib
from math import sqrt
try:
	import tkinter as tk
	from tkinter import messagebox
except ImportError:
	import Tkinter as tk
	import tkMessageBox
	tk.messagebox = tkMessageBox
	input = raw_input
import re
db = sqlite3.connect("shirts.db")
c = db.cursor()
# insert(), select(), update(), and delete() are functions that abstract the actual sql from me. 
def insert(id, description, lasttime, rating):
	c.execute("insert into shirts2 (id, description, lasttime, rating) VALUES (?, ?, ?, ?);", (id, description, lasttime, rating))
	db.commit()
def select(rows, params = ''):
	end = []
	if rows == "*":
		for i in c.execute("select * from shirts2 ORDER BY id;"):
			end.append(i)
	elif params == '': 
		for i in c.execute("select ? from shirts2 ORDER BY id;", (rows,)):
			end.append(i)
	else:
		for i in c.execute("select ? from shirts2 WHERE ? ORDER BY id;", (rows, params)):
			end.append(i)
	return end
def update(id, description, lasttime, rating):
	c.execute("update shirts2 SET lasttime = ?, description = ?, rating = ? WHERE id = ?;", (lasttime, description, rating, id))
	db.commit()
def delete(id):
	c.execute("delete from shirts2 WHERE id=?;", (id,))
	db.commit()
class Column(tk.Frame):
	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.master = master
		self.label = tk.Label(self)
		self.column = tk.Listbox(self, bd=1, height=30, width=13, selectmode='single', exportselection=0, yscrollcommand=self.scroll)
		self.column.bind("<ButtonRelease-1>", self.master.clickColumn)
		self.curselection = self.column.curselection
		self.config = self.column.config
		self.label.pack()
		self.column.pack()
		self.insert = self.column.insert
		self.selection_clear = self.column.selection_clear
		self.selection_set = self.column.selection_set
		self.size = self.column.size
		self.delete = self.column.delete
	def scroll(self, *args):
		for i in self.master.columns:
			if not i == self:
				i.column.yview_moveto(args[0])
		self.master.scrollbar.set(*args)
class IDColumn(Column):
	def __init__(self, master):
		Column.__init__(self, master)
		self.label.config(text="ID")
class DescriptionColumn(Column):
	def __init__(self, master):
		Column.__init__(self, master)
		self.label.config(text="Description")
		self.column.config(width=40)
class DateColumn(Column):
	def __init__(self, master):
		Column.__init__(self, master)
		self.label.config(text="Last Worn")
class RatingColumn(Column):
	def __init__(self, master):
		Column.__init__(self, master)
		self.label.config(text = "Rating")
	def ratingAdd(self, position, value):
		self.column.insert(position, "{}/5".format(str(value)))
class DateBox(tk.Frame):
	def __init__(self, master, text=""):
		tk.Frame.__init__(self, master)
		self.master = master
		self.frame = tk.Frame(self)
		self.label = tk.Label(self.frame, text=text)
		self.label.pack(side="left")
		self.textbox = tk.Entry(self.frame, validate='key', vcmd=(self.master.register(self.validateDate), '%P'))
		self.textbox.pack(side="left")
		self.today = tk.Button(self.frame, text="Today", command=self.insertToday, padx=3)
		self.today.pack(side='left', padx=5)
		self.frame.pack()
		self.insert = self.textbox.insert
		self.get = self.textbox.get
		self.delete = self.textbox.delete
		self.complaining = False
		self.complaint = tk.Label(self, fg="red", text='')
		self.complaint.pack()
	def insertToday(self): 
		self.delete(0, len(self.get()))
		self.insert(0, datetime.datetime.today().strftime("%Y-%m-%d"))
	def validateDate(self, text):
		date = re.compile(r"\d\d\d\d-\d\d-\d\d")
		if text == "":
			self.complaining = False
			self.complaint.config(text="")
		elif date.match(text):
			try:
				if datetime.datetime.today() >= datetime.datetime.strptime(text, "%Y-%m-%d"):
					self.complaint.config(text="")
					self.complaining = False
				else:
					self.complaint.config(text="That date is in the future!")
					self.complaining = True
			except ValueError:
				self.complaint.config(text="That date isn't properly formatted")
				self.complaining = True
		else:
			self.complaint.config(text="That date isn't properly formatted")
			self.complaining = True
		return True
class Star(tk.Label):
	def __init__(self, master, status, index):
		tk.Label.__init__(self, master)
		self.master = master
		self.status = status
		self.index = index
		self.onImage = tk.PhotoImage(file="res/filled_star.gif", )
		self.offImage = tk.PhotoImage(file="res/empty_star.gif")
		if self.status == 1:
			self.config(image=self.onImage)
		elif self.status == 0:
			self.config(image=self.offImage)
		self.bind("<Button-1>", lambda x: self.master.click(self.index))
	def set(self, status):
		self.status = status
		if status == 1:
			self.config(image=self.onImage)
		elif status == 0:
			self.config(image=self.offImage)
	def getStatus(self):
		return self.status
class RatingField(tk.Frame):
	def __init__(self, master, default = 3):
		tk.Frame.__init__(self, master)
		self.master = master
		self.NUM_OF_STARS = 5
		self.rating = 3
		self.stars = []
		for i in range(self.NUM_OF_STARS):
			self.stars.append(Star(self, 0, i))
			self.stars[-1].pack(side='left')
		self.click(default-1)
	def click(self, index):
		for i in self.stars:
			i.set(0)
		for i in range(index+1):
			self.stars[i].set(1)
		self.set(index+1)
	def get(self):
		return self.rating
	def set(self, rating):
		self.rating = rating
class DeleteShirtWindow:
	def __init__(self, master, shirt, index):
		if tk.messagebox.askyesno("Delete", "Do you really want to delete \"{}\"?".format(shirt.description)):
			delete(shirt.id)
			master.shirts.pop(index)
			master.populate()
class TShirtPicker(tk.Tk):
	def __init__(self, GUI):
		self.all = '*'
		self.date_format = "%Y-%m-%d"
		tk.Tk.__init__(self)
		self.title("T-Shirt Picker")
		self.shirts = []
		self.resizable(0, 0)
		self.buttonFrame = tk.Frame(self, height=15)
		self.pickButton = tk.Button(self.buttonFrame, text="Pick a Shirt", command = lambda: PickShirtWindow(self))
		self.pickButton.pack(side='left')
		self.addButton = tk.Button(self.buttonFrame, text="Add a Shirt", command = lambda: NewShirtWindow(self))
		self.addButton.pack(side='left')
		self.updateButton = tk.Button(self.buttonFrame, text="Update a Shirt", state="disabled", command=(lambda: UpdateWindow(self, self.shirts[self.idColumn.curselection()[0]]) if self.idColumn.curselection() else lambda: None))
		self.updateButton.pack(side='left')
		self.deleteButton = tk.Button(self.buttonFrame, command=lambda: DeleteShirtWindow(self, self.shirts[self.idColumn.curselection()[0]], self.idColumn.curselection()[0]) if self.idColumn.curselection() else lambda: None, text="Delete a Shirt", state="disabled")
		self.deleteButton.pack(side='left')
		self.buttonFrame.pack(expand=1, pady=4)
		self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.scroll)
		self.idColumn = IDColumn(self)
		self.dateColumn = DateColumn(self)
		self.descriptionColumn = DescriptionColumn(self)
		self.ratingColumn = RatingColumn(self)
		self.columns = [self.idColumn, self.descriptionColumn, self.dateColumn, self.ratingColumn]
		for i in self.columns:
			i.pack(side="left")
		self.scrollbar.pack(side="left", fill="y")
		self.onOpen(GUI)
	def onOpen(self, GUI):
		# When you open the program, make the list of shirts and populate the GUI, or make a table and then do that. 
		try:
			for i in select('*'):
				self.shirts.append(Shirt(i[0], i[1], i[2], i[3]))
			if GUI:
				self.populate()
		except sqlite3.Error:
			try:
				self.convert()
			except sqlite3.Error:
				raise
				conn = sqlite3.connect("shirts.db")
				c = conn.cursor()
				c.execute("create table shirts2 (id, description, lasttime, rating)")
				conn.commit()
				self.onOpen(True)
	def convert(self):
		conn = sqlite3.connect("shirts.db")
		c = conn.cursor()
		temp = []
		for i in c.execute("select * from shirts"):
			temp.append(Shirt(i[0], i[1], i[2]))
		c.execute("create table shirts2 (id, description, lasttime, rating)")
		for i in temp:
			c.execute("insert into shirts2 values(?, ?, ?, ?)", (i.id, i.description, i.lastTime, i.rating))
		conn.commit()
		self.onOpen(True)
	def populate(self):
		for i in self.columns:
			i.delete(0, tk.END)
		for i in self.shirts:
			i.addToList(*self.columns)
	def clickColumn(self, event):
		selection = event.widget.curselection()
		if selection:
			self.deleteButton.config(state='normal')
			self.updateButton.config(state='normal')
			for i in self.columns:
				if i != event.widget:
					i.selection_clear(0, self.descriptionColumn.size()-1)
					i.selection_set(selection[0])
	def scroll(self, *args):
		for i in self.columns:
			i.column.yview(*args)
class PickShirtWindow:
	def __init__(self, master):
		self.master = master
		one = self.pick()
		if tk.messagebox.askyesno("Pick", "Do you want to wear \""+one.description+"\" ?"):
			one.wearToday()
			master.populate()
			tk.messagebox.showinfo("Yes", "Ok. You're wearing \""+one.description+"\" today.")
		else:
			tk.messagebox.showinfo("No", "Ok. Press \"Pick today's shirt\" again to try again.")
	def pick(self):
		weighted = []
		for i in self.master.shirts:
			for j in range((int(10*sqrt(i.rating)))*(datetime.datetime.today()-datetime.datetime.strptime(i.lastTime, "%Y-%m-%d")).days*3+1):
				weighted.append(i)
		return random.choice(weighted)
class UpdateWindow(tk.Toplevel):
	def __init__(self, master, shirt):
		tk.Toplevel.__init__(self)
		self.focus_set()
		self.shirt = shirt
		self.bind("<Escape>", lambda x: self.destroy())
		self.bind("<Return>", lambda x: self.finish())
		tk.Label(self, text="Description").pack()
		self.descriptionBox = tk.Entry(self)
		self.descriptionBox.insert(0, self.shirt.description)
		self.descriptionBox.pack()
		tk.Label(self, text="Last worn (YYYY-MM-DD)").pack()
		self.dateEntry = DateBox(self)
		self.dateEntry.insert(0, self.shirt.lastTime)
		self.dateEntry.pack()
		self.ratingField = RatingField(self)
		self.ratingField.pack()
		self.buttons = tk.Frame(self)
		self.ok = tk.Button(self.buttons, text="OK", command=self.finish)
		self.ok.pack(side="left")
		self.cancel = tk.Button(self.buttons, text="Cancel", command = self.destroy)
		self.cancel.pack(side="left")
		self.buttons.pack()
	def finish(self):
		if self.dateEntry.complaining:
			return
		else:
			self.shirt.update(self.descriptionBox.get(), self.dateEntry.get(), self.ratingField.get())
			self.master.populate()
			self.destroy()
# This is the shirt class. 
class Shirt:
	def __init__(self, id, description, lastTime, rating = 3):
		self.description = description
		self.rating = rating
		# If you don't know when you wore it, say you wore it a week ago. 
		if lastTime == '':
			self.lastTime = (datetime.datetime.today()-datetime.timedelta(days=7)).strftime("%Y-%m-%d")
		else: 
			self.lastTime = lastTime
		# If the id is zero (it doesn't have one), tack it on to the end of the list. 
		if id == 0:
			# If the list is empty, it's number 1. 
			if len(select('*')) == 0:
				self.id = 1
			else:
				self.id = select('*')[-1][0]+1
			insert(self.id, self.description, self.lastTime, self.rating)
		else: 
			self.id = id
	# This updates both the database and the python list.
	def wearToday(self):
		update(self.id, datetime.date.today().strftime("%Y-%m-%d"), self.lastTime, self.rating)
		self.lastTime = datetime.date.today().strftime("%Y-%m-%d")
	# This is used by the tkinter list object to actually add the shirt to the GUI list. 
	def addToList(self, idColumn, descriptionColumn, dateColumn, ratingColumn):
		idColumn.insert('end', self.id)
		descriptionColumn.insert('end', self.description)
		dateColumn.insert('end', self.lastTime)
		ratingColumn.ratingAdd("end", self.rating)
	def update(self, description, lastTime, rating):
		self.description = description
		self.rating = rating
		self.lastTime = lastTime
		c.execute('update shirts2 set description=?, lasttime=?, rating=? where id=?', (self.description, self.lastTime, self.rating, self.id))
		db.commit()
class NewShirtWindow(tk.Toplevel):
	def __init__(self, master):
		tk.Toplevel.__init__(self)
		self.complaining = False
		self.master = master
		self.bind("<Escape>", lambda x: self.destroy())
		self.bind("<Return>", lambda x: self.finish())
		# Can I set the title to something better?
		tk.Label(self, text="Give a short description of the shirt").pack()
		self.enterDescription=tk.Entry(self)
		self.enterDescription.pack()
		self.enterDescription.focus_set()
		tk.Label(self, text='When was the last day you wore the shirt, \napproxamately, in YYYY-MM-DD format? \nOr leave it blank if you don\'t know.').pack()
		self.dateBox = DateBox(self)
		self.dateBox.pack()
		self.ratingField = RatingField(self)
		self.ratingField.pack()
		self.submit_button = tk.Button(self, text="Done", command= self.finish)
		self.submit_button.pack(pady=5)
	def finish(self):
		self.dateBox.validateDate(self.dateBox.get())
		if self.dateBox.complaining:
			return
		else:
			if self.enterDescription.get() != "" or tk.messagebox.askyesno("Empty Description", "Do you want to make a shirt with an empty description?"):
				self.master.shirts.append(Shirt(0, self.enterDescription.get(), self.dateBox.get(), self.ratingField.get()))
				self.master.shirts[-1].addToList(*self.master.columns)
				self.destroy()
if len(sys.argv) < 2:
	# This is the actual logic that happens when you run the program. 
	root = TShirtPicker(True)
	root.mainloop()
else:
	onOpen(False)
	def list():
		print("Here are your shirts \nID   Description   Last worn")
		for i in shirts: 
			print(', '.join([str(i.id), i.description, i.lastTime]))
	while True:
		command = input("Type PICK to pick a new shirt for today, NEW to add a shirt, UPDATE to update a shirt, LIST to list all shirts, DELETE to delete a shirt, or EXIT to exit. \n")
		if command.lower() == "new":
			descrip = input("Give a short description of the shirt \n")
			last = input("When was the last time you wore the shirt, in YYYY-MM-DD format? Or leave it blank if it was never worn \n")
			if last == '':
				last = (datetime.datetime.today()-datetime.timedelta(days=14)).strftime("%Y-%m-%d")
			shirts.append(Shirt(0, descrip, last))
		elif command.lower() == "pick":
			done = False
			while not done:
				choice = pick()
				print("Today's shirt is " + choice.description +". Do you want to wear it? y/n")
				n = input()
				if n.lower() == 'y':
					print("Ok!")
					choice.wearToday()
					done = True
				elif n.lower() == 'n':
					print("Ok then.")
		elif command.lower() == 'update':
			list()
			choice = shirts[WillsLib.myIndex(shirts, int(input("Type the ID of the shirt you want to change\n")), lambda x: x.id)]
			inp = input("Do you want to change the last worn DATE or the DESCRIPTION?\n")
			if inp.lower()== 'description':
				newDescrip = input("Type the new description you want\n")
				choice.update(newDescrip, choice.lastTime, False)
			elif inp.lower() == 'date':
				newDate = input("Type the new date you want to set in YYYY-MM-DD format\n")
				choice.update(choice.description, newDate, False)
		elif command.lower() == 'list':
			list()
		elif command.lower() == 'delete':
			list()
			delId = input("What is the ID of the shirt you want to delete?\n")
			yn = input("Do you really want to delete? YES or NO\n")
			if yn.lower() == 'yes':
				delete(int(delId))
				print("Successfully deleted")
		elif command.lower() == 'exit':
			break
		else: 
			print("That's not an available command. Sorry!")
		print("\n\n")
		shirts = [Shirt(i[0], i[1], i[2]) for i in select(all)]