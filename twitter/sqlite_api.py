#!/usr/bin/env python
# -*- coding: utf-8 -*-

# text processing in python
# Bijit Halder
# Merakee LLC.
# Aug 2014
import sqlite3 

class SqliteApi:

	def __init__(self,filename):
		self.db = sqlite3.connect(filename)
		self.cursor = self.db.cursor() 

	def close_db(self):
		if self.db:
			self.db.close()

	def create_table(self,table_name,col_def,new=False):
		"""
		Example: 
		col_def: (word TEXT NOT NULL UNIQUE,
	        	  count INT NOT NULL)
		"""
		if new:
			sql = "DROP TABLE IF EXISTS %s" % table_name
			self.cursor.execute(sql)
			sql = """CREATE TABLE %s %s""" % (table_name, col_def)
			self.cursor.execute(sql)
		else:
			sql = "CREATE TABLE IF NOT EXISTS %s %s" %(table_name, col_def)
			self.cursor.execute(sql)

		self.db.commit()

	def execute_sql(self, sql):
		self.cursor.execute(sql)
		return self.db.commit()

	def get_one(self, sql):
		self.cursor.execute(sql)
		return self.cursor.fetchone()

	def get_all(self, sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def set_cursor(self, sql):
		self.cursor.execute(sql)

	def get_next_row(self):
		return self.cursor.fetchone()




# commend line option
if __name__ == '__main__':
	# run test code
	db = SqliteApi("test.sqlite")
	table_name = "test_table"
	col_def = """
			(user_id INTEGER NOT NULL,
			 tagline TEXT NOT NULL,
			 score REAL NOT NULL)				
			"""
	db.create_table(table_name,col_def=col_def,new=True)
	user_id=13
	tagline = u"This is the tag line for user"
	score= 23.4
	sql = "INSERT INTO %s (user_id,tagline,score) VALUES (%d,'%s',%f)" %(table_name,user_id,tagline,score)
	db.execute_sql(sql)
	sql = "SELECT * FROM %s WHERE user_id=%d" %(table_name,user_id)
	res = db.get_one(sql)
	if (res[0] != user_id) or (res[1] != tagline) or (abs(res[2]- score)>0.0001):
		print "Error: the results do not match"
	db.close_db

