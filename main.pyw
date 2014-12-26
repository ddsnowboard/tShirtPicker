import sqlite3
import datetime
import random
import sys
import WillsLib
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
def insert(id, description, lasttime):
	c.execute("insert into shirts (id, description, lasttime) VALUES (?, ?, ?);", (id, description, lasttime))
	db.commit()
def select(rows, params = ''):
	end = []
	if rows == "*":
		for i in c.execute("select * from shirts ORDER BY id;"):
			end.append(i)
	elif params == '': 
		for i in c.execute("select ? from shirts ORDER BY id;", (rows,)):
			end.append(i)
	else:
		for i in c.execute("select ? from shirts WHERE ? ORDER BY id;", (rows, params)):
			end.append(i)
	return end
def update(id, lasttime):
	c.execute("update shirts SET lasttime = ? WHERE id = ?;", (lasttime, id))
	db.commit()
def delete(id):
	c.execute("delete from shirts WHERE id=?;", (id,))
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
	def scroll(self, *args):
		raise NotImplementedError("You need to implement this for each column individually")
class IDColumn(Column):
	def __init__(self, master):
		Column.__init__(self, master)
		self.label.config(text="ID")
	def scroll(self, *args):
		for i in [self.master.dateColumn, self.master.descriptionColumn]:
			i.column.yview_moveto(args[0])
		self.master.scrollbar.set(*args)
class DescriptionColumn(Column):
	def __init__(self, master):
		Column.__init__(self, master)
		self.label.config(text="Description")
		self.column.config(width=40)
	def scroll(self, *args):
		for i in [self.master.dateColumn, self.master.idColumn]:
			i.column.yview_moveto(args[0])
		self.master.scrollbar.set(*args)
class DateColumn(Column):
	def __init__(self, master):
		Column.__init__(self, master)
		self.label.config(text="Last Worn")
	def scroll(self, *args):
		for i in [self.master.idColumn, self.master.descriptionColumn]:
			i.column.yview_moveto(args[0])
		self.master.scrollbar.set(*args)
class TShirtPicker(tk.Tk):
	def __init__(self, GUI):
		self.all = '*'
		self.date_format = "%Y-%m-%d"
		tk.Tk.__init__(self)
		self.title("T-Shirt Picker")
		self.shirts = []
		self.resizable(0, 0)
		self.buttonFrame = tk.Frame(self, height=15)
		self.pickButton = tk.Button(self.buttonFrame, text="Pick a Shirt", command = pickAShirt)
		self.pickButton.pack(side='left')
		self.addButton = tk.Button(self.buttonFrame, text="Add a Shirt", command = lambda: NewShirtWindow())
		self.addButton.pack(side='left')
		self.updateButton = tk.Button(self.buttonFrame, command=updateShirt, text="Update a Shirt", state="disabled")
		self.updateButton.pack(side='left')
		self.deleteButton = tk.Button(self.buttonFrame, command=deleteShirt, text="Delete a Shirt", state="disabled")
		self.deleteButton.pack(side='left')
		self.buttonFrame.pack(expand=1, pady=4)
		self.scrollbar = tk.Scrollbar(self, orient='vertical')
		self.idColumn = IDColumn(self)
		self.dateColumn = DateColumn(self)
		self.descriptionColumn = DescriptionColumn(self)
		for i in [self.idColumn, self.descriptionColumn, self.dateColumn]:
			i.pack(side="left")
		self.scrollbar.pack(side="left", fill="y")
		self.onOpen(GUI)
	def onOpen(self, GUI):
		# When you open the program, make the list of shirts and populate the GUI, or make a table and then do that. 
		try:
			for i in select('*'):
				self.shirts.append(Shirt(i[0], i[1], i[2]))
			if GUI:
				self.populate()
		except sqlite3.Error:
			conn = sqlite3.connect("shirts.db")
			c = conn.cursor()
			c.execute("create table shirts (id INTEGER, description, lasttime")
			conn.commit()
			self.onOpen()
	def populate(self):
		for i in self.shirts:
			i.addToList(self.idColumn, self.descriptionColumn, self.dateColumn)
	def clickColumn(self, event):
		selection = event.widget.curselection()
		if selection:
			self.deleteButton.config(state='normal')
			self.updateButton.config(state='normal')
			if event.widget is not self.descriptionColumn:
				self.descriptionColumn.selection_clear(0, self.descriptionColumn.size()-1)
				self.descriptionColumn.selection_set(selection[0])
			if event.widget is not self.dateColumn:
				self.dateColumn.selection_clear(0, self.dateColumn.size()-1)
				self.dateColumn.selection_set(selection[0])
			if event.widget is not self.idColumn:
				self.idColumn.selection_clear(0, self.idColumn.size()-1)
				self.idColumn.selection_set(selection[0])
class PickShirtWindow(tk.Toplevel):
	def __init__(self, master):
		tk.Toplevel.__init__(self)
		self.master = master
		one = pick()
		if tk.messagebox.askyesno("Pick", "Do you want to wear \""+one.description+"\" ?"):
			one.wearToday()
			master.populate()
			tk.messagebox.showinfo("Yes", "Ok. You're wearing \""+one.description+"\" today.")
		else:
			tk.messagebox.showinfo("No", "Ok. Press \"Pick today's shirt\" again to try again.")
	def pick():
		weighted = []
		for i in master.shirts:
			for j in range((datetime.datetime.today()-datetime.datetime.strptime(i.lastTime, "%Y-%m-%d")).days*3+1):
				weighted.append(i)
		return random.choice(weighted)
# This is the shirt class. 
class Shirt:
	def __init__(self, id, description, lastTime):
		self.description = description
		# If you don't know when you wore it, say you wore it a week ago. 
		if lastTime == '':
			self.lastTime = (datetime.datetime.today()-datetime.timedelta(days=7)).strftime(date_format)
		else: 
			self.lastTime = lastTime
		# If the id is zero (it doesn't have one), tack it on to the end of the list. 
		if id == 0:
			# If the list is empty, it's number 1. 
			if len(select(all)) == 0:
				self.id = 1
			else:
				self.id = select(all)[-1][0]+1
			insert(self.id, self.description, self.lastTime)
		else: 
			self.id = id
	# This updates both the database and the python list.
	def wearToday(self):
		update(self.id, datetime.date.today().strftime(date_format))
		self.lastTime = datetime.date.today().strftime(date_format)
	# This is used by the tkinter list object to actually add the shirt to the GUI list. 
	def addToList(self, idColumn, descriptionColumn, dateColumn):
		idColumn.insert('end', self.id)
		descriptionColumn.insert('end', self.description)
		dateColumn.insert('end', self.lastTime)
	def update(self, description, lastTime, gui = True):
		self.description = description
		self.lastTime = lastTime
		c.execute('update shirts set description=?, lasttime=? where id=?', (self.description, self.lastTime, self.id))
		if gui:
			populate()
class NewShirtWindow(tk.Toplevel):
	def __init__(self, master):
		tk.Toplevel.__init__(self)
		self.complaining = False
		self.master = master
		self.bind("<Escape>", lambda x: self.destroy())
		# Can I set the title to something better?
		tk.Label(self, text="Give a short description of the shirt").pack()
		self.enterDescription=tk.Entry(self)
		self.enterDescription.pack()
		tk.Label(self, text='When was the last day you wore the shirt, \napproxamately, in YYYY-MM-DD format? \nOr leave it blank if you don\'t know.').pack()
		self.dateFrame = tk.Frame(self)
		self.enterDate = tk.Entry(self.dateFrame, validate='key', vcmd=(self.master.register(self.validateDate), '%P'))
		self.enterDate.pack(side="left")
		self.today_button = tk.Button(self.dateFrame, text="Today", command=self.insertTodaysDate)
		self.today_button.pack(side="left")
		self.dateFrame.pack(pady=5)
		self.complaint = tk.Label(self, text="", fg='red')
		self.complaint.pack()
		self.submit_button = tk.Button(self, text="Done", command= self.finishShirt)
		self.submit_button.pack(pady=5)
	def insertTodaysDate(self): 
		self.enterDate.delete(0, len(self.enterDate.get()))
		self.enterDate.insert(0, datetime.datetime.today().strftime(date_format))
	def validateDate(self, newText): 
		date = re.compile(r"\d\d\d\d-\d\d-\d\d")
		if newText == "":
			self.complaint.config(text="")
			self.complaining = False
		elif date.match(newText):
			try:
				if datetime.datetime.today() >= datetime.datetime.strptime(newText, date_format):
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
	def finishShirt(self):
		self.validateDate(self.enterDate.get())
		if self.complaining:
			return
		else:
			if self.enterDescription.get() != "" or tk.messagebox.askyesno("Empty Description", "Do you want to make a shirt with an empty description?"):
				shirts.append(Shirt(0, self.enterDescription.get(), self.enterDate.get()))
				shirts[-1].addToList()
				self.destroy()
def deleteShirt():
	global idColumn, descriptionColumn, dateColumn
	selection = idColumn.curselection()
	if selection:
		if tk.messagebox.askyesno("Delete", "Do you really want to delete the shirt \""+str(shirts[int(selection[0])].description)+"\"?"):
			delete(shirts.pop(int(selection[0])).id)
			idColumn.delete(selection[0])
			descriptionColumn.delete(selection[0])
			dateColumn.delete(selection[0])
# This puts today's date into a specific box. 
def insertTodaysDate(event):
	enterDate.insert('end', datetime.datetime.today().strftime(date_format))

# This picks the shirt.
def pickAShirt():
	one = pick()
	if tk.messagebox.askyesno("Pick", "Do you want to wear \""+one.description+"\" ?"):
		one.wearToday()
		populate()
		tk.messagebox.showinfo("Yes", "Ok. You're wearing \""+one.description+"\" today.")
	else:
		tk.messagebox.showinfo("No", "Ok. Press \"Pick today's shirt\" again to try again.")
def finishUpdate():
	if not datetime.datetime.today() < datetime.datetime.strptime(dateEntry.get(), date_format):
		shirts[int(updateSelection[0])].update(descriptionEntry.get(), dateEntry.get())
		updateDialog.destroy()
	else:
		complaint.set("You have to put in a past date, you fool!")
def updateShirt():
	global idColumn, updateSelection, descriptionEntry, dateEntry, updateDialog, complaint
	updateSelection = idColumn.curselection()
	if updateSelection:
		updateDialog = tk.Tk()
		updateDialog.bind("<Escape>", lambda n: updateDialog.destroy())
		complaint = tk.StringVar(updateDialog)
		tk.Label(updateDialog, text="Change the attributes of \"%s\" to how \nyou want them, then press OK, or cancel to cancel." % (str(shirts[int(updateSelection[0])].description))).pack()
		descriptionFrame = tk.Frame(updateDialog)
		tk.Label(descriptionFrame, text="Description: ").pack(side='left')
		descriptionEntry = tk.Entry(descriptionFrame)
		descriptionEntry.bind("<Return>", lambda n: finishUpdate())
		descriptionEntry.insert(0, shirts[int(updateSelection[0])].description)
		descriptionEntry.pack(side='left')
		descriptionFrame.pack()
		dateFrame = tk.Frame(updateDialog)
		tk.Label(dateFrame, text="Last worn (YYYY-MM-DD): ").pack(side='left')
		dateEntry = tk.Entry(dateFrame)
		dateEntry.insert(0, shirts[int(updateSelection[0])].lastTime)
		dateEntry.pack(side='left')
		dateEntry.bind("<Return>", finishUpdate)
		dateFrame.pack()
		tk.Label(updateDialog, textvariable = complaint, fg='red').pack()
		buttonFrame = tk.Frame(updateDialog)
		tk.Button(buttonFrame, text="OK", command=finishUpdate).pack(side='left')
		tk.Button(buttonFrame, text="Cancel", command=updateDialog.destroy).pack(side='left')
		buttonFrame.pack()
if len(sys.argv) < 2:
	# This is the actual logic that happens when you run the program. 
	root = TShirtPicker(True)
	root.mainloop()
else:
	onOpen(False)
# These are all for the text-based implementation, but I'm working on a GUI.
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
				last = (datetime.datetime.today()-datetime.timedelta(days=14)).strftime(date_format)
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