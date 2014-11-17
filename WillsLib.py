import sqlite3
import re
from collections import defaultdict
import math
def sanitize(string):
	WORD_LIST = ['ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC', 'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN', 'BY', 'CASCADE', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT', 'CONFLICT', 'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'DATABASE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DROP', 'EACH', 'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUSIVE', 'EXISTS', 'EXPLAIN', 'FAIL', 'FOR', 'FOREIGN', 'FROM', 'FULL', 'GLOB', 'GROUP', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE', 'IN', 'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTERSECT', 'INTO', 'IS', 'ISNULL', 'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'MATCH', 'NATURAL', 'NO', 'NOT', 'NOTNULL', 'NULL', 'OF', 'OFFSET', 'ON', 'OR', 'ORDER', 'OUTER', 'PLAN', 'PRAGMA', 'PRIMARY', 'QUERY', 'RAISE', 'RECURSIVE', 'REFERENCES', 'REGEXP', 'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT', 'RIGHT', 'ROLLBACK', 'ROW', 'SAVEPOINT', 'SELECT', 'SET', 'TABLE', 'TEMP', 'TEMPORARY', 'THEN', 'TO', 'TRANSACTION', 'TRIGGER', 'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL', 'WHEN', 'WHERE', 'WITH', 'WITHOUT']
	for i in WORD_LIST:
		if ' '+i.lower()+' ' in string.lower() or ', '+i.lower() in string.lower() or string.lower() == i.lower():
			if i == 'DROP':
				raise Exception("You should not have used \"Drop\" in your input. Please use a different word")
			else:
				string = string.lower().replace(i.lower(),"'"+i.lower()+"'")
	return string
def DBinsert(connection, table_name, vals):
	if type(vals) == type([]):
		s = 'insert into '+sanitize(table_name)+' VALUES (?'
		for i in range(len(vals)-1):
			s += ",?"
		s+=');'
		connection.cursor().execute(s, tuple(vals))
	elif type(vals) == type({}):
		s = 'insert into %s(' % sanitize(table_name)
		s += ','.join([sanitize(i) for i in vals.keys()])
		s+=') VALUES (?'
		for i in range(len(vals.values())-1):
			s +=',?'
		s += ');'
		connection.cursor().execute(s, tuple(vals.values()))
	connection.commit()
def DBselect(connection, table_name, columns, which):
	out = []
	if columns == 'all':
		columns = ['*']
	elif type(columns) == str:
		columns = [columns]
	else:
		for i, j in enumerate(columns):
			columns[i] = sanitize(str(j))
	if which == 'all':
		for i in connection.cursor().execute('select %s from %s;' % (','.join(columns),sanitize(table_name))):
			out.append(i)
	else:
		strings = [sanitize(i) + " = ?" for i in which.keys()]
		for i in connection.cursor().execute("select %s from %s WHERE %s" % (','.join(columns), sanitize(table_name), ' and '.join(strings)), tuple([i for i in which.values()])):
			out.append(i)
	return out
def DBcreate(connection, table_name, columns):
	s = 'create table '+sanitize(table_name)+'('
	s+= ', '.join([sanitize(i) for i in columns])
	s+=');'
	print(s)
	connection.cursor().execute(s)
	connection.commit()
def DBupdate(connection, table_name, set, which):
	# Set and which will be dictionaries that have the syntax {column: value}
	# "Which" could also be the string "all"
	if not set:
		raise Exception("""You didn't give the right parameters!\nYou need 
						 to give 2 dictionaries, \"set\" and \"which\", that\n
						 are in the format {attribute:value}. See the \n
						 documentation for more details.""")
	elif not which:
		raise Exception("""You didn't give the right parameters!\nYou need 
						 to give 2 dictionaries, \"set\" and \"which\", that\n
						 are in the format {attribute:value}. See the \n
						 documentation for more details.\n
						 If you want to select all and change, use\n
						 which='all'""")
	strings = []
	for i in set.keys():
		strings.append(sanitize(str(i))+' = ?')
	if which == 'all':
		connection.cursor().execute("update "+sanitize(table_name)+" SET "+', '.join(strings),tuple([j for j in set.values()]))
		connection.commit()
	else:
		params = []
		for i in which.keys():
			params.append(sanitize(str(i))+' = ?')
		connection.cursor().execute("update "+table_name+" SET "+', '.join(strings)+" WHERE "+' and '.join(params),tuple([j for j in set.values()]+[i for i in which.values()]))
	connection.commit()
def DBdelete(connection, table_name, which):
	if which == 'all':
		connection.cursor().execute("delete from %s" % sanitize(table_name))
		db.commit()
		return
	strings = [sanitize(i)+ " = ?" for i in which.keys()]
	connection.cursor().execute("delete from "+sanitize(table_name)+" WHERE "+' and '.join(strings),tuple([i for i in which.values()]))
	connection.commit()
# A generator that will generate perfect squares forever. 
def squares():
	out = 1
	odd = 3
	while True:
		yield out
		out+=odd
		odd+=2
# This generator should kick out primes forever, given enough memory and time. Also, it's broken.  
def primes():
	yield 2
	prime = True
	out = 3
	while True:
		prime = True
		for i in range(2, int(out/2)+1):
			if out%i==0:
				prime = False
		if prime:
			yield out
		out+=2
# This is a class for polynomial equations. Give it the equation as a string, and you can evaluate it and maybe find the intersection
# with another line. 
class Equation:
	def __init__(self, eq):	# y=2x^2-3x+5
		self.coefficients = defaultdict(float)
		self.eq = re.subn(r"^y=|=y$", '', eq)[0]   # 2x^2-3x+5
		self.eq = self.eq.replace('^', '**').replace("+", " +").replace("-", ' -')  # 2x**2 -3x +5
		self.terms = self.eq.split(" ")	 # "2x**2", "-3x", "+5"
		self.terms = [i for i in self.terms if i != '']
		for i in self.terms:
			if not re.compile(r"[A-Za-z]").search(i):
				self.coefficients[0] += float(i)  # "+5"
			elif re.compile(r"[\+-]?[\d\.]+[A-Za-z]$").search(i):
				self.coefficients[1]+=float(re.compile(r"[A-Za-z]").subn('',i)[0])  	#"-3" 
			elif re.compile(r"[\+-]?[\d\.]+[A-Za-z]\*\*\d+").match(i):
				self.coefficients[i[i.index("**")+2:]] += float(i[:re.compile("[A-Za-z]").search(i).span()[1]-1]) # '2'
		self.degree = len(self.coefficients)-1
	def evaluate(self, x):
		end = 0
		for i, j in self.coefficients.items():
			end+=j*x**i
		return end
	def intersect(self, other):
		if not type(other) == type(Equation("2x^2-4x+5")):
			raise Exception("You seem to have made a stupid; this is supposed to take another equation and find the intersection")
			return
		# Left will be variables; right will be constants. 
		# Left starts as self, right starts as other. 
		left = defaultdict(float)
		right = 0
		for i, j in self.coefficients.items():
			if i == 0:
				right-=j
			else:
				left[i]+=j
		for i, j in other.coefficients.items():
			if i == 0:
				right+=j
			else:
				left[i]-=j
		if self.degree == 0 and other.degree == 0:
			return right == 0
		elif self.degree<=1 and other.degree<=1:
			return (right/left[1], self.evaluate(right/left[1]))
		elif self.degree == 2 or other.degree == 2:
			return (((-1*left[1]+math.sqrt(left[1]**2-4*(left[2])*(-1*right)))/(2*left[2]), self.evaluate((-1*left[1]+math.sqrt(left[1]**2-4*(left[2])*(-1*right)))/(2*left[2]))), ((-1*left[1]-math.sqrt(left[1]**2-4*(left[2])*(-1*right)))/(2*left[2]), self.evaluate((-1*left[1]-math.sqrt(left[1]**2-4*(left[2])*(-1*right)))/(2*left[2]))))
		else:
			raise Error("I really can't get an accurate intersection with just this data.")
def myIndex(l, value, func = lambda x: x):
	for i, j in enumerate(l):
		if func(j) == value:
			return i