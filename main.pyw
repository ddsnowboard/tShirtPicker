import sqlite3
import datetime
import random
import tkinter as tk
db = sqlite3.connect("shirts.db")
root = tk.Tk()
c = db.cursor()
all = '*'
date_format = "%Y-%m-%d"
shirts = []
def insert(id, description, lasttime):
	c.execute("insert into shirts (id, description, lasttime) VALUES (" + str(id) + ", '" + description + "', '" + lasttime + "');")
	db.commit()
def list():
	print("Here are your shirts \nID   Description   Last worn")
	for i in shirts: 
		print(', '.join([str(i.id), i.description, i.lastTime]))
def select(rows, params = ''):
	end = []
	if params == '': 
		for i in c.execute("select " + rows + " from shirts;"):
			end.append(i)
	else:
		for i in c.execute("select " + rows + " from shirts WHERE " + params+';'):
			end.append(i)
	return end
def update(id, lasttime):
	c.execute("update shirts SET lasttime = '" + lasttime + "' WHERE id = "+ str(id) +";")
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
		db.commit()
def onOpen():
	try:
		for i in select(all):
			shirts.append(Shirt(i[0], i[1], i[2]))
		
	except:
		c.execute("create table shirts (id, description, lasttime);")
		onOpen()
onOpen()
root.title("T-Shirt Picker")
buttons = tk.Frame(root, height=15)
pickButton = tk.Button(buttons, text="Pick today's shirt")
pickButton.pack(side='left')
addButton = tk.Button(buttons, text="Add a shirt")
addButton.pack(side='left')
updateButton = tk.Button(buttons, text="Update a shirt")
updateButton.pack(side='left')
deleteButton = tk.Button(buttons, text='Delete a shirt')
deleteButton.pack(side='left')
buttons.pack(expand=1, pady=4)
idFrame = tk.Frame(root, width=10, height=40)
idLabel = tk.Label(idFrame, text="ID")
idLabel.pack()
idColumn = tk.Listbox(idFrame, bg="#ffffff", bd=1, height=40, width=10)
idColumn.pack(fill='x', expand=1, side='top')
idFrame.pack(side='left')
descriptionFrame = tk.Frame(root, width=40, height=40)
descriptionLabel = tk.Label(descriptionFrame, text="Description")
descriptionLabel.pack()
descriptionColumn = tk.Listbox(descriptionFrame, bg="#ffffff", bd=1, height=40, width=40)
descriptionColumn.pack()
descriptionFrame.pack(side='left')
dateFrame = tk.Frame(root, height=40, width=15)
dateLabel = tk.Label(dateFrame, text="Last Worn")
dateLabel.pack()
dateColumn = tk.Listbox(dateFrame, height=40, width=15)
dateColumn.pack()
dateFrame.pack(side='left')
root.mainloop()








# These are all for the text-based implementation, but I'm working on a GUI.
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