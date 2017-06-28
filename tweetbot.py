import tweepy

CONSUMER_KEY = 'bFwgpbZrOAEt89DF5HWuKqaAU'
CONSUMER_SECRET = 'jE1cOeNZDj3BEBd9i4tR8HGvwWhjeAILwRwNFx4Xef724vkR1M'
ACCESS_KEY = '877102971724611584-gaavJtmnrA8sU3j40NduZZ3cUNjvPxZ'
ACCESS_SECRET = 'UC22YRmqXnbzKPsM5x18MD1k6VKHQxE0R04qhu3iYpkm4'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

#for number in ["3rd", "4th", "5th"]:
#	api.update_status("Sending my " + number + " tweet via Tweepy!")

mention = api.mentions_timeline()[0]
print(mention.id_str)
print(mention.user.screen_name)
status_text = "@" + mention.user.screen_name + " Replying to test"
api.update_status(status=status_text, in_reply_to_status_id=mention.id_str)
	
