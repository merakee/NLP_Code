#!/usr/bin/env python
# -*- coding: utf-8 -*-

# text processing in python
# Bijit Halder
# Merakee LLC.
# Aug 2014
import sys
sys.path.append('./util')
sys.path.append('./twitter')

import nltk
import sqlite_api
import string

# gobal variables 
np_list = ['NN','NNP','NNPS','NNS']
#stemmer= nltk.stem.porter.PorterStemmer()
lmtzr = nltk.WordNetLemmatizer()
out_table_name = "key_words_table" 
punc_list = set(string.punctuation)

class ExtractKeyWords:
	def __init__(self,db_in_filename,in_table_name,in_col_name,db_out_filename,new=False):
		self.db_in = sqlite_api.SqliteApi(db_in_filename)
		self.cursor_in = self.db_in.cursor 
		self.db_out = sqlite_api.SqliteApi(db_out_filename)
		self.cursor_out = self.db_out.cursor
		self.in_table_name = in_table_name
		self.in_col_name = in_col_name
		# create table
		col_def = """
				(key_word TEXT NOT NULL UNIQUE,
	        	count INT NOT NULL)
				"""
		self.db_out.create_table(table_name=out_table_name,col_def=col_def,new=new)

	def close_db(self):
		if self.db_in:
			self.db_in.close()
		if self.db_out:
			self.db_out.close()

	def insert_data(self,key_word):
		if not key_word:
			return

		# try to update 
		sql = "UPDATE %s SET count = (count+1) WHERE key_word = '%s'" % (out_table_name,key_word)
		res = self.db_out.execute_sql(sql) 
		if res.rowcount==0: # insert 
			sql =  "INSERT INTO %s (key_word,count) VALUES('%s',%d)" % (out_table_name,key_word,1)
			self.db_out.execute_sql(sql) 

	def save_key_words(self,key_words):
		if not key_words:
			return 

		for key_word in key_words:
			key_word = self.strip_punc(key_word).capitalize()
			self.insert_data(key_word) 


	def strip_punc(self,text):
		return ''.join(ch for ch in text if ch not in punc_list) 

	def get_key_words(self,text):
		tags = nltk.pos_tag(nltk.word_tokenize(text))
		return list({lmtzr.lemmatize(tag[0]) for tag in tags if tag[1] in np_list})

	def set_text_cursor(self):
		sql = "SELECT rowid, %s FROM %s" % (self.in_col_name,self.in_table_name)
		self.db_in.execute_sql(sql)

	def get_next_text(self):
		return self.cursor_in.fetchone()

	def get_key_word_count(self):
		sql = "SELECT COUNT(*) FROM %s" % out_table_name
		return self.db_out.get_one(sql)[0]

	def create_key_word_db(self):
		"""
		this is the main function for creating the db for key_word words
		"""
		print "Start................."
		self.set_text_cursor()
		res = self.get_next_text()
		while res:
			if (res[0]-1)%1000 ==0:
				print "processing quote %d ....key_words count: %d" % (res[0], self.get_key_word_count())
			key_words =  self.get_key_words(res[1])
			self.save_key_words(key_words)
			res = self.get_next_text()


		# close db
		self.close_db()
		print "End................."


# commend line option
if __name__ == '__main__':
	# run code
	ekw = ExtractKeyWords(db_in_filename="./twitter/Twitter_feed.sqlite",
		in_table_name="tweets",in_col_name="tweet",
		db_out_filename="./twitter/Twitter_feed_key_word.sqlite",
		new=True)
	ekw.create_key_word_db()
