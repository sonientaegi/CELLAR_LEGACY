#! /usr/bin/python
import sys
import sqlite3

connOld = sqlite3.connect(sys.argv[1])
connNew = sqlite3.connect(sys.argv[2])
cursorOld = connOld.cursor()
cursorNew = connNew.cursor()

tables = []
for table in cursorOld.execute("select name from sqlite_master where type = 'table'") :
	tables.append(table[0])

for table in tables :
	print("\n\n" + table)
	
	cursorNew.execute("delete from '%s'" % table)
	for record in cursorOld.execute("select * from '%s'" % table) :
		fields = len(record)
		sql = "insert into '" + table + "' values("
		
		values = ""
		
		for column in record :
			if column is None :
				values = values + "null"
			elif type(column) is int :
				values = values + column.__str__()
			else :
				values = values + "'" + column + "'"
			values = values + ","
	
		sql = sql + values[0:len(values)-1] +  ")"
		print(sql)
		cursorNew.execute(sql)
connNew.commit()
connNew.close()
connOld.close()
print("Job completed")
