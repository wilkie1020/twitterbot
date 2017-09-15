from TwitterAPI import TwitterAPI
import textwrap
import time
import json
import os.path
import os
import sys
import datetime

#authentication data
consumer_key = "5s1rr9Dg0eKFD97T7w2G6kpe9"
consumer_secret = "DvoVKE1wn2vsWLj8qaZyUnNo5K77KUf2dlO9g6Vzjc1sF7pjE9"
access_token_key = "890686903506173952-912Z2iCvNXo7QEuNjf6aZMW07Ne47bj"
access_token_secret = "2aDT2mjtFO92I59vvD2WBjFWMSnX11q9eyC2l3vTT9k6D"

#Authenticate
api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

#keywords data
follow_key = ["follow", "follower", "must be following", "following"]
fav_key = ["favorite", "fav", "like"]
search_queries = ["RT to win", "retweet to win", "retweet to enter", "rt to enter", "#retweet to #win", "#retweet to win"]
#search_queries = ["RT to win"]
bot_check = ["bot", "b0t"]#May append more like 6 for Bs or 7 for Ts?


#tracking lists
ignorelist = list()# already processed tweets
followlist = list()# who am I following and when
donotfollow = list()# bots and such - never follow or retweet

count_per_Search = 25

tweet_queue = list()#the list of items to re-tweet/favorite/follow


# read in the previous data of tracking lists if they exist
if os.path.isfile('C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\ignorelist'):
	print("Loading ignore list \n")
	with open('C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\ignorelist') as f:
		ignorelist = f.read().splitlines()
	f.close()
	
if os.path.isfile('C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\followlist'):
	print("Loading follow list \n")
	with open('C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\followlist') as g:
		followlist = g.read().splitlines()
	g.close()
	os.remove('C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\followlist')
	
if os.path.isfile('C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\donotfollow'):
	print("Loading do not follow list \n")
	with open('C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\donotfollow') as h:
		donotfollow = h.read().splitlines()
	h.close()

def unFollowBot():
    #This function will see how long a user has been followed
    #for and unfollow if greater than 3 weeks
	today = datetime.datetime.now().date()
    #iterate each item in the follow list
    #O(n), not great, whatever
	for i in range(len(followlist)):
		item = followlist[i]
		
		id, f_date_str = item.split('_')#Splits it based on delimeter _
        #need to see what format datetime is in
		#print(f_date_str)
		f_date_init = datetime.datetime.strptime(f_date_str, "%Y-%m-%d")#need to convert follow date to storing only year month day as well
		#YYYY-MM-DD is the standard form of a datetime.date()
		f_date = f_date_init.date()
		#print(str(f_date))
        
		d_diff = today - f_date
		d_diff_int = int(d_diff.days)
        
		if d_diff_int > 21:
			r = api.request('friendships/destroy', {'user_id': id})
			followlist.pop(i)
			print("Unfollowed after 3 months: " + id)
			#remove from followlist file
		

def checkFollow(item):

	print("Am following?: " + item['user']['screen_name'] + " - " + str(item['user']['following']))
	if str(item['user']['following']) == "False":
		text = item['text']
		user = item['user']
		screen_name = user['screen_name']
		id = user['id']

		if any(string in text.lower() for string in follow_key):
			r = api.request('friendships/create', {'id': id})
			print ("Following: " + screen_name + "\n")
			
			today = datetime.datetime.now()
			now = today.date()
			
			followlist.append(str(id) + "_" + str(now))

			f_fol = open("C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\followlist", 'a')
			f_fol.write(str(id) + "_" + str(now) + "\n")
			f_fol.close()
	else:
		print("Already following user: " + item['user']['screen_name'])

def checkLike(item):

	text = item['text']
	id = item['id']	
	shortened = textwrap.shorten(text, width = 50)

	if any(string in text.lower() for string in fav_key):
		r = api.request('favorites/create', {'id': id})
		print ("Liked: " + shortened + "\n")


def processQueue():

	while len(tweet_queue) > 0:
		#retweet
		tweet = tweet_queue.pop()
		print("******************" + "Queue Length: " + str(len(tweet_queue)) + "*************************")
		
		print("Retweeting: " + tweet['text'] + "\n")
		r = api.request('statuses/retweet/:' + str(tweet['id']))
		#check for follow request
		checkFollow(tweet)
		#check for like/favorite request
		checkLike(tweet)
		print("*******************************************")
		
		time.sleep(5)
	
def botCheck(item):
	user_data = item['user']
	user_id = user_data['id']
	user_screen_name = user_data['screen_name']
	screen_name_lowercase = user_screen_name.lower()
	
	#for each case of bot keywords
	for string in bot_check:
		#if any seem like bots
		if string in screen_name_lowercase:
			#add the user ID for that twitter account to the do not follow list
			donotfollow.append(user_id)
			print("Bot Found! Added to do not follow list \n")
			f_dnf = open("C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\donotfollow", 'a')
			f_dnf.write(str(user_id) + "\n")
			f_dnf.close()

	
def getTweets():

	
	for search_query in search_queries:
		r = api.request('search/tweets', {'q':search_query, 'result_type':"mixed", 'count':count_per_Search})
		
		print("Getting results for " + search_query + "\n")
		
		for item in r:
			

			#collect the tweet data we need based on it if is a retweet or not
			#tweet data
			#if there is a retweet_status it is a retweeted tweet
			if 'retweeted_status' in item:
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("Retweeted item \n")
				original_item = item['retweeted_status']#pulls data from original tweet, not the retweet
				#original user of the tweet data
				original_user_data = original_item['user']
				original_screen_name = original_user_data['screen_name']
				original_user_id = str(original_user_data['id'])
				
				#original tweet data
				original_tweet_id = str(original_item['id'])
				original_tweet_text = original_item['text']
				original_have_rted = original_item['retweeted']
				original_have_fvted = original_item['favorited']
				
				botCheck(original_item)
				
				if not original_user_id in donotfollow:
					if not original_tweet_id in ignorelist:
						print("Okay to process retweet \n")
						tweet_queue.append(original_item)
						
						f_ign = open("C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\ignorelist", 'a')
						f_ign.write(str(original_tweet_id) + "\n")
						f_ign.close()
					else:
						print("Ignored: " + str(original_tweet_id) + "\n")
				else:
					print(str(original_user_id) + " On do not follow list \n")
						
				time.sleep(3)
					
				
			else:
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("New item \n")
				#user of the tweet data
				user_data = item['user']# user data in json forma
				screen_name = user_data['screen_name']#screen name of the specific user who tweeted
				user_id = str(user_data['id'])# user ID pulled from user data
				
				#tweet data
				text = item['text'] # text of the tweet
				tweet_id = str(item['id'])#id for the specific tweet
				have_rted = item['retweeted']#this object holds a true or false value
				have_fvted = item['favorited']#this object holds true or false value

				botCheck(item)
				
				if not user_id in donotfollow:
					if not tweet_id in ignorelist:
						print("Okay to process \n")
						tweet_queue.append(item)
						ignorelist.append(tweet_id)
						
						f_ign = open("C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\ignorelist", 'a')
						f_ign.write(str(tweet_id) + "\n")
						f_ign.close()
					else:
						print("Ignored: " + str(tweet_id) + "\n")
				else:
					print(str(original_user_id) + " On do not follow list \n")
						
				time.sleep(3)

	
#Start of the main loop
while (True):
	print("########################Scanning for Tweets \n")
	getTweets()
	
	time.sleep(5) #Sleep to avoid rate limit
	print("########################Processing Tweet Queue \n")
	
	processQueue()
	
	print("########################Running Unfollow Bot \n")
	unFollowBot()
	
	time.sleep(5) #sleep to avoid rate limiting
	print("Printing ignore list for testing \n")
	
	for x in ignorelist:
		print(str(x))
	
	print("Printing do not follow list for testing \n")
	for x in donotfollow:
		print(str(x))
		
	print("Printing follow list for testing \n")
	for x in followlist:
		print(str(x))

		f_fol = open("C:\\Users\\Mat\\AppData\\Local\\Programs\\Python\\Python36-32\\Working Folder\\ContestBot\\followlist", 'a')
		f_fol.write(x + "\n")
		f_fol.close()
		
	time.sleep(15) #sleep to let me close now if I want