from TwitterAPI import TwitterAPI
import time

# Authetnication keys
consumer_key = "<Your token here>"
consumer_secret = "<Your token here>"
access_token_key = "<Your token here>"
access_token_secret = "<Your token here>"

# Authenticate
api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

for id in api.request('friends/ids'):
	r = api.request('friendships/destroy', {'user_id': id})
	time.sleep(5)