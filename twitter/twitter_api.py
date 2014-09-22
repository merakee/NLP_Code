#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Access twitter Api
# Bijit Halder
# Merakee LLC.
# Aug 2014
import sys
sys.path.append('../util')
import twitter
import sqlite_api
import string
import re

# global var
db_file_name = "Twitter_feed.sqlite"
table_name = "tweets"
valid_ch_list = list(string.lowercase) +  list(string.uppercase) + list(string.punctuation) + range(0,10) + [' ']
WORLD_WOE_ID = 1
US_WOE_ID = 23424977

class TwitterApi:
	def __init__(self):
	# XXX: Go to http://twitter.com/apps/new to create an app and get values # for these credentials that you'll need to provide in place of these
	# empty string values that are defined as placeholders.
	# See https://dev.twitter.com/docs/auth/oauth for more information
	# on Twitter's OAuth implementation.
		CONSUMER_KEY = 'l25tveWcFxl0hnlRQCYhLX9pL'
		CONSUMER_SECRET = 'uYrAMvKKVWE7UVArhiJhHE8zEx7x6ToI6H0Kq9X1di94VYJzse'
		OAUTH_TOKEN = '2725103371-sIPczPhz9Y6TcxTKhyxkqtau6YhJx8e68hds6dj'
		OAUTH_TOKEN_SECRET = 'LQXIjf1mz2FCwPO5nWtyRWIqYFFZ1Xzp1wbmvU0Cl6Nv4'
		"""
		self.api_manager = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=OAUTH_TOKEN,
                  access_token_secret=OAUTH_TOKEN_SECRET)
		"""
		auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
		self.api_manager = twitter.Twitter(auth=auth)
		self.db = sqlite_api.SqliteApi(db_file_name)
		# create table
		col_def = """
				(tweet TEXT NOT NULL UNIQUE)
				"""
		self.db.create_table(table_name=table_name,col_def=col_def)



	def save_stream(self,key="fun",count=1000):
		# Reference the self.auth parameter
		twitter_stream = twitter.TwitterStream(auth=self.api_manager.auth) # See https://dev.twitter.com/docs/streaming-apis
		stream = twitter_stream.statuses.filter(track=key,language='en')
		# For illustrative purposes, when all else fails, search for Justin Bieber
		# and something is sure to turn up (at least, on Twitter)
		c_count=0
		print "Saving tweets to database...and text file....%d" % c_count
		file_h = open(self.get_text_file_name(keyword,count),'w')
		for tweet in stream:
			# Save to a database in a particular collection
			text = self.extract_text(tweet['text'])
			c_count += self.save_text(text,file_h)
			if c_count%1000 == 0:
				print "Saving tweets to database...%d" % c_count
			if c_count >= count:
				file_h.close()
				self.db.close_db()
				break


	def get_stream(self,key="fun"):
		# Reference the self.auth parameter
		twitter_stream = twitter.TwitterStream(auth=self.api_manager.auth) # See https://dev.twitter.com/docs/streaming-apis
		stream = twitter_stream.statuses.filter(track=key,language='en')
		# For illustrative purposes, when all else fails, search for Justin Bieber
		# and something is sure to turn up (at least, on Twitter)
		for tweet in stream:
			if 'text' in tweet:
				print tweet['text']


	def get_tweets(self,key="fun",count=10):
		# Reference the self.auth parameter
		twitter_stream = twitter.TwitterStream(auth=self.api_manager.auth) # See https://dev.twitter.com/docs/streaming-apis
		stream = twitter_stream.statuses.filter(track=key,language='en')

		# For illustrative purposes, when all else fails, search for Justin Bieber
		# and something is sure to turn up (at least, on Twitter)
		#print stream.
		tweets=[]
		for tweet in stream:
			tweets.append(tweet['text'])
			if len(tweets) >= count:
				break

		return tweets 

	def clean_string(self, text):
		text = text.replace("'", '"') # replace single quote with double quote 
		return self.remove_tags(''.join(ch for ch in text if ch in valid_ch_list))
	
	def remove_tags(self, text):
		text = re.sub("(RT([^:]*)\:)","",text) # remove retweet
		text = re.sub("(@([^\s]*))","",text) # remove @ mention
		text = re.sub("(#([^:]*)\:)","",text) # remove #  at the start
		text = re.sub("(#([^\s]*))","",text) # remove # in the middle 
		return text.strip()

	def extract_text(self,tweet):
		return self.clean_string(tweet)

	def save_text(self,text,file_h):
		if text:
			sql  = "SELECT * FROM %s WHERE tweet = '%s'" % (table_name, text)
			res = self.db.get_one(sql)
			if not res: # if does not exist
				# save to text file
				file_h.write(text + "\n") 
				sql = "INSERT INTO %s (tweet) VALUES ('%s')" % (table_name, text) 
				self.db.execute_sql(sql)
				return 1
		return 0

	def get_trends(self,place_id):
		results = self.api_manager.trends.place(_id=place_id)
		#print results 
		for location in results:
			for trend in location["trends"]:
				print " - %s" % trend["name"]


	def get_text_file_name(self,keyword=None,count=0):
		if not keyword:
			return "tweets_trends.text"
		else:
			if count==0:
				return "tweets_" + keyword + ".text"
			else:
				return "tweets_" + keyword + "_" + str(count) + ".text"

# commend line option
if __name__ == '__main__':
	# set api_manager
	tapi = TwitterApi()
	
	# for tweet in tapi.get_tweets(count=20,key="rivers"):
	# 	print "Tweet::: %s"  % tweet 
	# 	print "Tweet<<< %s"  % tapi.extract_text(tweet) 

	keyword, count = None, 0
	if len(sys.argv)>1:
		keyword = sys.argv[1]

	if len(sys.argv)>2:
		count = int(sys.argv[2])


	if not keyword:
		print "WORLD -----------------"
		tapi.get_trends(WORLD_WOE_ID)
		print "US  -----------------"
		tapi.get_trends(US_WOE_ID)
	else:
		if count==0:
			tapi.get_stream(keyword)
		else:
			tapi.save_stream(keyword, count)



	# tapi.get_stream("#BORvAFC")
	#tapi.get_stream("funny")
	#tapi.save_stream("funny",10000)
	