import sqlite3
import datetime
import random
import tkinter as tk
from tkinter import messagebox
import re
db = sqlite3.connect("shirts.db")
root = tk.Tk()
c = db.cursor()
all = '*'
date_format = "%Y-%m-%d"
shirts = []
root.title("T-Shirt Picker")
buttons = tk.Frame(root, height=15)
pickButton = tk.Button(buttons, text="Pick today's shirt")
addButton = tk.Button(buttons, text="Add a shirt")
updateButton = tk.Button(buttons, text="Update a shirt")
deleteButton = tk.Button(buttons, text='Delete a shirt', state='disabled')
idFrame = tk.Frame(root, width=10, height=30)
idLabel = tk.Label(idFrame, text="ID")
idColumn = tk.Listbox(idFrame, bd=1, height=30, width=10, selectmode='single', exportselection=0)
descriptionFrame = tk.Frame(root, width=40, height=30)
descriptionLabel = tk.Label(descriptionFrame, text="Description")
descriptionColumn = tk.Listbox(descriptionFrame, bg="#ffffff", bd=1, height=30, width=40, selectmode='single', exportselection=0)
dateFrame = tk.Frame(root, height=30, width=15)
dateLabel = tk.Label(dateFrame, text="Last Worn")
dateColumn = tk.Listbox(dateFrame, height=30, width=15, selectmode='single', exportselection=0)
def insert(id, description, lasttime):
	c.execute("insert into shirts (id, description, lasttime) VALUES (" + str(id) + ", '" + description + "', '" + lasttime + "');")
	db.commit()
def select(rows, params = ''):
	end = []
	if params == '': 
		for i in c.execute("select " + rows + " from shirts ORDER BY id;"):
			end.append(i)
	else:
		for i in c.execute("select " + rows + " from shirts WHERE " + params+' ORDER BY id;'):
			end.append(i)
	return end
def update(id, lasttime):
	c.execute("update shirts SET lasttime = '" + lasttime + "' WHERE id = "+ str(id) +";")
	db.commit()
def delete(id):
	c.execute("delete from shirts WHERE id="+str(id)+';')
	db.commit()
def pick():
	weighted = []
	for i in shirts:
		for j in range((datetime.datetime.today()-datetime.datetime.strptime(i.lastTime, date_format)).days*3+1):
			weighted.append(i)
	return random.choice(weighted)
class Shirt:
	def __init__(self, id, description, lastTime):
		global db
		self.description = description
		if lastTime == '':
			self.lastTime = (datetime.datetime.today()-datetime.timedelta(days=7)).strftime(date_format)
		else: 
			self.lastTime = lastTime
		if id == 0:
			if len(select(all)) == 0:
				self.id = 1
			else:
				self.id = select(all)[-1][0]+1
			insert(self.id, self.description, self.lastTime)
			db.commit()
		else: 
			self.id = id
			
	def wearToday(self):
		update(self.id, datetime.date.today().strftime(date_format))
		self.lastTime = datetime.date.today().strftime(date_format)
		db.commit()
	def addToList(self):
		global idColumn, descriptionColumn, dateColumn
		idColumn.insert('end', self.id)
		descriptionColumn.insert('end', self.description)
		dateColumn.insert('end', self.lastTime)
	def update(self, description, lastTime):
		self.description = description
		self.lastTime = lastTime
		c.execute('update shirts set description=?, lasttime=? where id=?', (self.description, self.lastTime, self.id))
		db.commit()
		populate()
def populate():
	idColumn.delete(0, 'end')
	dateColumn.delete(0, 'end')
	descriptionColumn.delete(0,'end')
	for i in shirts:
		i.addToList()
def onOpen():
	try:
		for i in select(all):
			shirts.append(Shirt(i[0], i[1], i[2]))
		populate()
	except:
		c.execute("create table shirts (id, description, lasttime);")
		onOpen()
def clickColumn(event):
	selection = event.widget.curselection()
	if selection:
		deleteButton.config(state='normal')
		if event.widget is not descriptionColumn:
			descriptionColumn.selection_clear(0, descriptionColumn.size()-1)
			descriptionColumn.selection_set(selection[0])
		if event.widget is not dateColumn:
			dateColumn.selection_clear(0, dateColumn.size()-1)
			dateColumn.selection_set(selection[0])
		if event.widget is not idColumn:
			idColumn.selection_clear(0, idColumn.size()-1)
			idColumn.selection_set(selection[0])
def finishShirt(event):
	description = enterDescription.get()
	date = enterDate.get()
	if description is not '' and (re.match("\d\d\d\d-\d\d-\d\d",date) or date == ''):
		shirts.append(Shirt(0, description, date))
		shirts[-1].addToList()
		dialog.destroy()
def addShirt():
	global dialog, enterDescription, enterDate
	dialog = tk.Tk()
	tk.Label(dialog, text='Give a short description of the shirt').pack()
	enterDescription = tk.Entry(dialog)
	enterDescription.pack(pady=5)
	tk.Label(dialog, text='When was the last day you wore the shirt, \napproxamately, in YYYY-MM-DD format? \nOr leave it blank if you don\'t know.').pack()
	dateDialogFrame = tk.Frame(dialog)
	enterDate = tk.Entry(dateDialogFrame)
	enterDate.pack(pady=5, side='left')
	today = tk.Button(dateDialogFrame, text="Today")
	today.bind("<Button-1>", insertTodaysDate)
	today.pack(side='left')
	dateDialogFrame.pack()
	okButton = tk.Button(dialog, text="OK")
	okButton.pack(pady=5)
	okButton.bind("<Button-1>", finishShirt)
def deleteShirt():
	global idColumn, descriptionColumn, dateColumn
	selection = idColumn.curselection()
	if selection:
		if tk.messagebox.askyesno("Delete", "Do you really want to delete the shirt \""+str(shirts[selection[0]].description)+"\"?"):
			delete(shirts.pop(selection[0]).id)
			idColumn.delete(selection[0])
			descriptionColumn.delete(selection[0])
			dateColumn.delete(selection[0])
def insertTodaysDate(event):
	enterDate.insert('end', datetime.datetime.today().strftime(date_format))
def pickAShirt():
	one = pick()
	if tk.messagebox.askyesno("Pick", "Do you want to wear \""+one.description+"\" ?"):
		one.wearToday()
		populate()
		tk.messagebox.showinfo("Yes", "Ok. You're wearing \""+one.description+"\" today.")
	else:
		tk.messagebox.showinfo("No", "Ok. Press \"Pick today's shirt\" again to try again.")
def finishUpdate():
	shirts[updateSelection[0]].update(descriptionEntry.get(), dateEntry.get())
	updateDialog.destroy()
def updateShirt():
	global idColumn, updateSelection, descriptionEntry, dateEntry, updateDialog
	updateSelection = idColumn.curselection()
	if updateSelection:
		updateDialog = tk.Tk()
		tk.Label(updateDialog, text="Change the attributes of \""+ str(shirts[updateSelection[0]].description) + "\" to how \nyou want them, then press OK, or cancel to cancel.").pack()
		descriptionFrame = tk.Frame(updateDialog)
		tk.Label(descriptionFrame, text="Description: ").pack(side='left')
		descriptionEntry = tk.Entry(descriptionFrame)
		descriptionEntry.insert(0, shirts[updateSelection[0]].description)
		descriptionEntry.pack(side='left')
		descriptionFrame.pack()
		dateFrame = tk.Frame(updateDialog)
		tk.Label(dateFrame, text="Last worn (YYYY-MM-DD): ").pack(side='left')
		dateEntry = tk.Entry(dateFrame)
		dateEntry.insert(0, shirts[updateSelection[0]].lastTime)
		dateEntry.pack(side='left')
		dateFrame.pack()
		buttonFrame = tk.Frame(updateDialog)
		tk.Button(buttonFrame, text="OK", command=finishUpdate).pack(side='left')
		tk.Button(buttonFrame, text="Cancel", command=updateDialog.destroy).pack(side='left')
		buttonFrame.pack()		
onOpen()
pickButton.config(command=pickAShirt)
pickButton.pack(side='left')
addButton.config(command=addShirt)
addButton.pack(side='left')
deleteButton.config(command=deleteShirt)
deleteButton.pack(side='left')
updateButton.config(command=updateShirt)
updateButton.pack(side='left')
buttons.pack(expand=1, pady=4)
idLabel.pack()
idColumn.bind('<ButtonRelease-1>', clickColumn)
idColumn.pack()
idFrame.pack(side='left')
descriptionLabel.pack()
descriptionColumn.bind('<ButtonRelease-1>', clickColumn)
descriptionColumn.pack()
descriptionFrame.pack(side='left')
dateLabel.pack()
dateColumn.bind('<ButtonRelease-1>', clickColumn)
dateColumn.pack()
dateFrame.pack(side='left')
root.mainloop()








# These are all for the text-based implementation, but I'm working on a GUI.
# def list():
	# print("Here are your shirts \nID   Description   Last worn")
	# for i in shirts: 
		# print(', '.join([str(i.id), i.description, i.lastTime]))
# while True:
	# i = input("Type PICK to pick a new shirt for today, NEW to add a shirt, UPDATE to update a shirt, LIST to list all shirts, DELETE to delete a shirt, or EXIT to exit. \n")
	# if i.lower() == "new":
		# descrip = input("Give a short description of the shirt \n")
		# last = input("When was the last time you wore the shirt, in YYYY-MM-DD format? Or leave it blank if it was never worn \n")
		# if last == '':
			# last = (datetime.datetime.today()-datetime.timedelta(days=14)).strftime(date_format)
		# shirts.append(Shirt(0, descrip, last))
	# elif i.lower() == "pick":
		# done = False
		# while not done:
			# choice = pick()
			# print("Today's shirt is " + choice.description +". Do you want to wear it? y/n")
			# n = input()
			# if n.lower() == 'y':
				# print("Ok!")
				# choice.wearToday()
				# done = True
			# elif n.lower() == 'n':
				# print("Ok then.")
	# elif i.lower() == 'update':
		# list()
		# choice = input("Type the ID of the shirt you want to change\n")
		# inp = input("Do you want to change the last worn DATE or the DESCRIPTION?\n")
		# if inp.lower()== 'description':
			# newDescrip = input("Type the new description you want\n")
			# c.execute("update shirts SET description='"+newDescrip+"' WHERE id = "+str(choice)+";")
			# db.commit()
		# elif inp.lower() == 'date':
			# newDate = input("Type the new date you want to set in YYYY-MM-DD format\n")
			# update(choice, newDate)
	# elif i.lower() == 'list':
		# list()
	# elif i.lower() == 'delete':
		# list()
		# delId = input("What is the ID of the shirt you want to delete?\n")
		# yn = input("Do you really want to delete? YES or NO\n")
		# if yn.lower() == 'yes':
			# c.execute("delete from shirts where id = "+str(delId) +";")
			# print("Successfully deleted")
	# elif i.lower() == 'exit':
		# break
	# else: 
		# print("That's not an available command. Sorry!")
		
	# print("\n\n")