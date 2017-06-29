#!/usr/bin/env python

import tweepy, sys, random, subprocess
from random import randint

import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw, ImageOps

import pexpect
from pexpect import spawnu as spawn, EOF

##arpabet
arpabet = {
	'AO': 'o', 		#off, fall
	'AA': 'a', 		#father
	'IY': 'i', 		#bee		#changed from ee -> i
	'UW': 'oo', 	#food
	'EH': 'e', 		#red
	'IH': 'i', 		#big
	'UH': 'ou', 	#should
	'AH': 'a', 		#but        #changed from u -> a
	'AX': 'u', 		#discus
	'AE': 'a', 		#at
	'EY': 'a', 		#say
	'AY': 'i', 		#my
	'OW': 'o', 		#show
	'AW': 'ow', 	#how
	'OY': 'oy', 	#boy
	'ER': 'er', 	#her
	'AXR':'er', 	#father
	'EH R': 'air',  #air, where
	'UH R': 'ur', 	#cure, bureau
	'AO R': 'or', 	#more, bored
	'AA R': 'ar', 	#large
	'IH R': 'ear', 	#ear, near
	'IY R': 'ear', 	#" " " "
	'AW R': 'our', 	#flower
	'P': 'p',
	'B': 'b',
	'T': 't',
	'D': 'd',
	'K': 'k',
	'G': 'g',
	'CH': 'ch',
	'JH': 'j',
	'F': 'f',
	'V': 'v',
	'TH': 'th',
	'DH': 'th', 	#that, the
	'S': 's',
	'Z': 'z',
	'SH': 'sh',
	'ZH': 'j', 		#measure
	'HH': 'h',
	'M': 'm',
	'EM': 'm',
	'N': 'n',
	'EN': 'en', 	#button
	'NG': 'ng',
	'ENG': 'ing', 	#washington
	'L': 'l',
	'EL': 'l', 		#bottle
	'R': 'r',  		#run
	'DX': 'r', 		#wetter
	'NX': 'r', 		#wintergreen
	'Y': 'y',
	'W': 'w',
	'Q': '?',
}

photo_info = {

	'image1' : {
		'font' : "fonts/PermanentMarker.ttf",
		'font-size' : 70,
		'url' : "photo_templates/coffee_photo.jpeg",
		'cup-x-offset': 295,
		'cup-width' : 370,
		'y' : 370,

	},

	'image2' : {
		'font' : "fonts/brownbaglunch.medium.ttf",
		'font-size' : 150,
		'url' : "photo_templates/coffee_photo2.jpg",
		'cup-x-offset': 345,
		'cup-width' : 468,
		'y' : 350,

	},

	'image4' : {
		'font' : "fonts/brownbaglunch.medium.ttf",
		'font-size' : 100,
		'url' : "photo_templates/coffee_photo4.jpg",
		'cup-x-offset': 500,
		'cup-width' : 355,
		'y' : 300,

	},

}
ERROR_TYPE_NONE = 0
ERROR_TYPE_TOO_MANY_WORDS = 1
ERROR_TYPE_NONALPHA_CHARACTERS = 2
ERROR_TYPE_WORD_TOO_LONG = 3


def setupCredentials():
	CONSUMER_KEY = 'bFwgpbZrOAEt89DF5HWuKqaAU'
	CONSUMER_SECRET = 'jE1cOeNZDj3BEBd9i4tR8HGvwWhjeAILwRwNFx4Xef724vkR1M'
	ACCESS_KEY = '877102971724611584-gaavJtmnrA8sU3j40NduZZ3cUNjvPxZ'
	ACCESS_SECRET = 'UC22YRmqXnbzKPsM5x18MD1k6VKHQxE0R04qhu3iYpkm4'

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
	api = tweepy.API(auth)
	return api

api = setupCredentials()

class MyStreamListener(tweepy.StreamListener):
	
	def on_status(self, tweet):
		respondToTweet(tweet)


def main(args=None):

	runTestCases()
	respondToUnreadMentions()

	streamListener = MyStreamListener()
	stream = tweepy.Stream(auth = api.auth, listener=streamListener)
	stream.filter(track=['@thebaristabot'])


def respondToUnreadMentions():
	target = open('records.txt', 'r')
	last_responded_mention = target.readline()
	unresponded_mentions = api.mentions_timeline(since_id=last_responded_mention)
	for tweet in unresponded_mentions:
		if tweet.user.screen_name != 'thebaristabot':
			respondToTweet(tweet)

def respondToTweet(tweet):

	status_id = tweet.id_str #what we reply to 
	username = tweet.user.screen_name #twitter handle name

	#array of words in message
	#convert to all lowercase for g2p
	#remove special characters
	customer_name_array = [x.lower() for x in tweet.text.split() if x.lower() != '@thebaristabot'] 

	error_type = verifyRequestFormat(customer_name_array)
	if error_type == ERROR_TYPE_TOO_MANY_WORDS:
		api.update_status(status= "@" + username + " Sorry, I can only remember up to 3 words!", in_reply_to_status_id=status_id)	
	elif error_type == ERROR_TYPE_NONALPHA_CHARACTERS:
		api.update_status(status= "@" + username + " Sorry, I don't know how to handle numbers or special characters like puncuation!", in_reply_to_status_id=status_id)
	elif error_type == ERROR_TYPE_WORD_TOO_LONG:
		api.update_status(status= "@" + username + " Sorry, one or more of the words is too long for me!", in_reply_to_status_id=status_id)
	else:
		coffee_name = generateName(customer_name_array)	
		imagePath = createImage(coffee_name)
		customer_full_name = ' '.join(customer_name_array).title()
		status_message = ". @" + username + " Order for " + customer_full_name + "!"
		api.update_with_media(imagePath, status=status_message, in_reply_to_status_id=status_id)	

	#store the status id to keep track of responses
	target = open('records.txt', 'w')
	target.truncate()
	target.write(status_id)
	target.close()

def generateName(customer_name_array):
	cmd = ['g2p-seq2seq', '--interactive', '--model', 'g2p/g2p-seq2seq-cmudict']
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	for i in range(0,3):
		process.stdout.readline() #read line 3 times to dump the excess output

	#generate name
	customer_name_g2p_input = '\n'.join(customer_name_array)
	g2p_output,error = process.communicate(customer_name_g2p_input.encode())

	customer_name_phonetic_array = g2p_output.decode("utf-8").strip('> ').split('> ')
	full_name_array = []
	for index, name in enumerate(customer_name_phonetic_array):
		new_name = ''
		for phoneme in name.split():
			new_name = new_name + arpabet[str(phoneme)]

		if new_name == customer_name_array[index]:
			new_name = applyAdditionalTransform(new_name, name.split())
		full_name_array.append(new_name)

	full_name_string = ' '.join(full_name_array)
	return full_name_string

def applyAdditionalTransform(name, phonetic_list):
	
	#find all vowels
	vowel_indices = []
	for index, letter in enumerate(name):
		if letter in ['a', 'e', 'i', 'o', 'u']:
			vowel_indices.append(index)

	#select random vowel and replace with another vowel
	random_vowel_index = random.choice(vowel_indices)

	new_vowel = random.choice(['a', 'e', 'i', 'o', 'u'])
	while new_vowel == name[random_vowel_index]:
		new_vowel = random.choice(['a', 'e', 'i', 'o', 'u'])

	return name[0:random_vowel_index] + new_vowel + name[random_vowel_index+1:]


def verifyRequestFormat(customer_name_array):
	#only evaluate names that are 3 words or less
	if len(customer_name_array) > 3:
		return ERROR_TYPE_TOO_MANY_WORDS

	elif any(not name.isalpha() for name in customer_name_array):
		return ERROR_TYPE_NONALPHA_CHARACTERS

	elif any(len(name) > 20 for name in customer_name_array):
		return ERROR_TYPE_WORD_TOO_LONG
	else:
		return ERROR_TYPE_NONE


def createImage(name): 

	#choose random photo
	curPhotoData = photo_info[random.choice(['image1', 'image2', 'image4'])]
	#curPhotoData = photo_info['image1'] #for testing
	img = Image.open(curPhotoData['url'])
	img_width, img_height = img.size
	draw = ImageDraw.Draw(img)
	font_size = curPhotoData['font-size']
	font = ImageFont.truetype(curPhotoData['font'], font_size)
	text_width, text_height = draw.textsize(name, font=font)
	
	#shrink font until the text fits within the cup
	while text_width >= curPhotoData['cup-width']:
		font_size = int(font_size*0.8)
		font = ImageFont.truetype(curPhotoData['font'], font_size)
		text_width, text_height = draw.textsize(name, font=font)


	draw.text((curPhotoData['cup-x-offset'] + (curPhotoData['cup-width'] - text_width)/2, curPhotoData['y']), name, (0, 0, 0), font=font)
	file_path = "final-photos/" + name + '.jpg'
	img.save(file_path)
	return file_path


def runTestCases():

	assert verifyRequestFormat(['$arah', 'dollar']) == ERROR_TYPE_NONALPHA_CHARACTERS
	assert verifyRequestFormat(['one', 'two', 'three', 'four']) == ERROR_TYPE_TOO_MANY_WORDS
	assert verifyRequestFormat(['a', 'b', 'c']) == ERROR_TYPE_NONE
	assert verifyRequestFormat([x.lower() for x in ['ke$ha']]) == ERROR_TYPE_NONALPHA_CHARACTERS



if __name__ == "__main__":
	main()