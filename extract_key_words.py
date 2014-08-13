#!/usr/bin/env python
# -*- coding: utf-8 -*-

# text processing in python
# Bijit Halder
# Merakee LLC.
# Aug 2014
import nltk
import sqlite3 
import string

# gobal variables 
np_list = ['NN','NNP','NNPS','NNS']
#stemmer= nltk.stem.porter.PorterStemmer()
lmtzr = nltk.WordNetLemmatizer()
db_in= None
cursor_in = None 
#db_in_filename = "QuoteDatabase_All.sqlite"
db_in_filename = "./twitter/Twitter_feed.sqlite"
db_out=None
cursor_out = None 
db_out_filename = "./twitter/Twitter_feed_keys.sqlite"
out_table_name = "quote_keys"
in_table_name = "tweets"
in_col_name = "tweet"
punc_list = set(string.punctuation)

# db related functions
def open_db(dbname = "in"):
	global db_in, cursor_in, db_out, cursor_out 
	if dbname == "in":
		if db_in == None:
			print "opening in db"
			db_in = sqlite3.connect(db_in_filename)
		if cursor_in == None: 
			print "init cursor for in db"
			cursor_in = db_in.cursor() 
	
	if dbname == "out":
		if db_out == None:
			print "opening out db"
			db_out = sqlite3.connect(db_out_filename)
		if cursor_out == None: 
			print "init cursor for out db"
			cursor_out = db_out.cursor() 

def close_db(dbname = "in"):
	if dbname == "in":
		if db_in:
			print "closing in db"
			db_in.close()

	if dbname == "out":
		if db_out:
			print "closing out db"
			db_out.close()


def create_db():
	if cursor_out:
		cursor_out.execute("DROP TABLE IF EXISTS quote_keys")
    	cursor_out.execute("""CREATE TABLE quote_keys (
    							word TEXT NOT NULL UNIQUE,
        						count INT NOT NULL)
							""")
    	db_out.commit()

def insert_data(word):
	if not word:
		return

	# try to update 
	res = cursor_out.execute("UPDATE quote_keys SET count = (count+1) WHERE word = ?",(word,)) 
	if res.rowcount==0: # insert 
		#print "inserting word: %s" % word  
		cursor_out.execute("INSERT INTO quote_keys (word,count) VALUES(?,?)", (word,1))

	db_out.commit()

def save_keys(keys):
	if not keys:
		return 

	for key in keys:
		key = strip_punc(key).capitalize()
		insert_data(key) 


def strip_punc(text):
	return ''.join(ch for ch in text if ch not in punc_list) 

def get_keys(text):
	tags = nltk.pos_tag(nltk.word_tokenize(text))
	return list({lmtzr.lemmatize(tag[0]) for tag in tags if tag[1] in np_list})

def set_quote_cursor():
	if cursor_in:
		cursor_in.execute("SELECT rowid, %s FROM %s" % (in_col_name,in_table_name))

def get_next_quote():
	if cursor_in:
		return cursor_in.fetchone()

def get_key_count():
	if cursor_out:
		cursor_out.execute("SELECT COUNT(*) FROM quote_keys")
		return cursor_out.fetchone()[0]

def create_key_db():
	"""
	this is the main function for creating the db for key words
	"""
	print "Start................."
	# db set up
	open_db("in")
	open_db("out")
	create_db()

	set_quote_cursor()
	res = get_next_quote()
	while res:
		if (res[0]-1)%1000 ==0:
			print "processing quote %d ....keys count: %d" % (res[0], get_key_count())
		keys =  get_keys(res[1])
		save_keys(keys)
		res = get_next_quote()


	# close db
	close_db("out")
	close_db("in")
	print "End................."



# commend line option
if __name__ == '__main__':
	# run code
	create_key_db()
