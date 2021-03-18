import sys
import gpiozero
import requests
import datetime
import json
import random
import time
import math
from config import enable_stream
from config import enable_hype
from config import enable_follow
from config import enable_spare

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('Twitch Relay Monitor Helper')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/home/pi/twitch_relay_monitor/logs/helper.log', maxBytes=200000,backupCount=2)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

RELAY_PIN_1 = 4		#RELAY 1 / GPIO 4 / PIN 7
RELAY_PIN_2 = 17	#RELAY 2 / GPIO 17 / PIN 11
RELAY_PIN_3 = 27	#RELAY 3 / GPIO 27 / PIN 13
RELAY_PIN_4 = 22	#RELAY 4 / GPIO 22 / PIN 15
RELAY_PIN_5 = 24	#RELAY 5 / GPIO 24 / PIN 18
RELAY_PIN_6 = 25 	#RELAY 6 / GPIO 25 / PIN 22
RELAY_PIN_7 = 8 	#RELAY 7 / GPIO 8 / PIN 24
RELAY_PIN_8 = 7 	#RELAY 8 / GPIO 7 / PIN 26


relay1 = gpiozero.OutputDevice(RELAY_PIN_1, active_high=False, initial_value=False)
relay2 = gpiozero.OutputDevice(RELAY_PIN_2, active_high=False, initial_value=False)
relay3 = gpiozero.OutputDevice(RELAY_PIN_3, active_high=False, initial_value=False)
relay4 = gpiozero.OutputDevice(RELAY_PIN_4, active_high=False, initial_value=False)
relay5 = gpiozero.OutputDevice(RELAY_PIN_5, active_high=False, initial_value=False)
relay6 = gpiozero.OutputDevice(RELAY_PIN_6, active_high=False, initial_value=False)
relay7 = gpiozero.OutputDevice(RELAY_PIN_7, active_high=False, initial_value=False)
relay8 = gpiozero.OutputDevice(RELAY_PIN_8, active_high=False, initial_value=False)

# First, you need to register your application to get Client id and client secret
# https://dev.twitch.tv/docs/authentication#registration

# Get app token to access Twich API
# https://dev.twitch.tv/docs/authentication#introduction
# return auth. object or False if an error happen.

# App access token used here because I only need to access public data not specific user data.
# scope for channel:read:hype_train	only.
# https://dev.twitch.tv/docs/authentication#scopes
def get_token(client_id,client_secret,grant_type,scope):

	url = "https://id.twitch.tv/oauth2/token?client_id="+ \
		client_id+"&client_secret="+ \
		client_secret+"&grant_type="+ \
		grant_type+"&scope="+scope
	try:
		response = requests.request("POST",url)
		r=json.loads(response.text)
		return r
	except requests.Timeout as err:
		logger.error("get_token timeout")
		return False
	except Exception as e:
		logger.error("get_token network error")
		return False

# Check if the token is valid or not.
# return True if valid and False if invalid or network error
# https://dev.twitch.tv/docs/authentication#validating-requests
def is_valid_token(access_token):
	
	url = "https://id.twitch.tv/oauth2/validate"
	headers = {
	  'Authorization': 'OAuth '+access_token
	}
	try:
		response = requests.request("GET", url, headers=headers,)
		logger.info("valid token")
		if "expires_in" in r :
			if r['expires_in'] < 60*60*24: #1 day
				return False
		else:
			return False
	except requests.Timeout as err:
		logger.info("is_valid_token timeout")
		return False
	except Exception as e:
		logger.error("is_valid_token network error ")
		return False	
	return True


# Get last train information
# https://dev.twitch.tv/docs/api/webhooks-reference/#topic-hype-train-event
# user id is long value returned from get_broadcaster_id using username
# return last hype train action or false if there is a problem
def get_last_hype_train_action(client_id,access_token,user_id):
	url = "https://api.twitch.tv/helix/hypetrain/events?broadcaster_id="+ \
		user_id + \
		"&first=1"
	headers = {
	  'Client-ID': client_id,
	  'Authorization': 'Bearer '+access_token
	}
	try:
		response = requests.request("GET", url, headers=headers)
		return json.loads(response.text)
	except requests.Timeout as err:
		logger.info("get hype train action timeout")
		return False
	except Exception as e:
		logger.error("get hype train action network error ")
		return False

# Get broadcaster id from its username
# https://dev.twitch.tv/docs/v5/reference/users/#get-users
# return user object 

def get_broadcaster_id(client_id,username):
	url = "https://api.twitch.tv/kraken/users?login="+username
	headers = {
	  'Accept': 'application/vnd.twitchtv.v5+json',
	  'Client-ID': client_id
	}
	try:
		response = requests.request("GET", url, headers=headers)
		r=json.loads(response.text)
		return r['users'][0]
	except requests.Timeout as err:
		logger.error("get_broadcaster_id timeout")
		return False
	except Exception as e:
		logger.error("get_broadcaster_id network error ")
		return False

# Get last follow information
# https://dev.twitch.tv/docs/api/webhooks-reference#topic-user-follows

def get_last_follow_action(client_id,access_token,user_id):
	url = "https://api.twitch.tv/helix/users/follows?first=1&to_id="+ \
		user_id
	headers = {
	  'Client-ID': client_id,
	  'Authorization': 'Bearer '+access_token
	}
	try:
		response = requests.request("GET", url, headers=headers)
		return json.loads(response.text)
	except requests.Timeout as err:
		logger.error("get hype train action timeout")
		return False
	except Exception as e:
		logger.error("get hype train action network error ")
		return False

# Get last subscription information
# https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscribe

def get_last_subscribe_action(client_id,access_token,user_id):
	url = "https://api.twitch.tv/helix/subscriptions/events?broadcaster_id="+ \
		user_id + \
		"&first=1"
	headers = {
	  'Client-ID': client_id,
	  'Authorization': 'Bearer '+access_token
	}
	try:
		response = requests.request("GET", url, headers=headers)
		return json.loads(response.text)
	except requests.Timeout as err:
		logger.error("get subscriber action timeout")
		return False
	except Exception as e:
		logger.error("get subscriber action network error ")
		return False

# Get last Extension Transaction
def get_last_transaction_action(client_id,access_token,user_id):
	url = "https://api.twitch.tv/helix/extensions/transactions?extension_id="+ \
		client_id + \
		"&first=1"
	headers = {
	  'Client-ID': client_id,
	  'Authorization': 'Bearer '+access_token
	}
	try:
		response = requests.request("GET", url, headers=headers)
		return json.loads(response.text)
	except requests.Timeout as err:
		logger.error("get transaction action timeout")
		return False
	except Exception as e:
		logger.error("get transaction action network error ")
		return False

# Check if the train is active by comparing current UTC time with hype train `expires_at`
# return True if the train active, return False if the train inactive.

def is_train_active(train_data):
	# pprint.pprint(train_data)
	# exit()
	if len(train_data)==0:
		return False
	event_end=train_data[0]["event_data"]["expires_at"]
	event_end_date_time=datetime.datetime.strptime(event_end,'%Y-%m-%dT%H:%M:%SZ')
	if datetime.datetime.utcnow() > event_end_date_time:
		return False
	return True

# Check if the user streaming
# https://dev.twitch.tv/docs/api/reference#get-streams
# return True if the user streaming, return False if the user offline

def is_user_live(client_id,access_token,username):
	import requests
	url = "https://api.twitch.tv/helix/streams?user_login="+username
	
	headers = {
	  'Client-ID': client_id,
	  'Authorization': 'Bearer '+access_token
	}
	try:
		response = requests.request("GET", url, headers=headers, timeout=30)
		r=json.loads(response.text)
		if len(r["data"])==0:
			return False
		return True
	except requests.Timeout as err:
		logger.error("is_user_live timeout")
		return False
	except Exception as e:
		logger.error("can not check if user live ")
		return False

# Cooldown
# Show 12 base watch countdown after the train end.
# based on this project: https://github.com/plusmnt/rectangle-scrollphathd-watch
# take future as datetime object and subtract it from utc now

def show_time(future):
	now=datetime.datetime.utcnow()
	diff = future-now
	logger.info("Cooldown timer:" + str(diff))
	time_str=str(diff).split(":")


def set_stream(state):
	if enable_stream==1:
		try:
			if relay1.value==state:
				#do nothing
				return True
			if state==1:
				#turn on relay
				logger.info("set stream relay level " + str(state))
				relay1.on()
			if state==0:
				#turn off relay
				logger.info("set stream relay level " + str(state))
				relay1.off()
    			else:
				#do nothing
				return False
			return True
		except Exception as e:
			logger.error("set stream error")
			return False

def set_hypetrain(hype_level):
	if enable_hype==1:
		try:
			if hype_level==0:
				#turn off all relays
				if relay2.value==1:
					relay2.off()
				if relay3.value==1:
					relay3.off()
				if relay4.value==1:
					relay4.off()
				if relay5.value==1:
					relay5.off()
				if relay6.value==1:
					logger.info("set hype level relay level " + str(hype_level))
					relay6.off()
				return True
			if hype_level==1:
				#turn on relay 2 only
				if relay2.value==0:
					logger.info("set hype level relay level " + str(hype_level))
					relay2.on()
				if relay3.value==1:
					relay3.off()
				if relay4.value==1:
					relay4.off()
				if relay5.value==1:
					relay5.off()
				if relay6.value==1:
					relay6.off()
				return True
			if hype_level==2:
				#turn on relay 2 + relay 3
				if relay2.value==0:
					relay2.on()
				if relay3.value==0:
					logger.info("set hype level relay level " + str(hype_level))
					relay3.on()
				if relay4.value==1:
					relay4.off()
				if relay5.value==1:
					relay5.off()
				if relay6.value==1:
					relay6.off()
				return True
			if hype_level==3:
				#turn on relay 2 + relay 3 + relay 4
				if relay2.value==0:
					relay2.on()
				if relay3.value==0:
					relay3.on()
				if relay4.value==0:
					logger.info("set hype level relay level " + str(hype_level))
					relay4.on()
				if relay5.value==1:
					relay5.off()
				if relay6.value==1:
					relay6.off()
				return True
			if hype_level==4:
				#turn on relay 2 + relay 3 + relay 4 + relay 5
				if relay2.value==0:
					relay2.on()
				if relay3.value==0:
					relay3.on()
				if relay4.value==0:
					relay4.on()
				if relay5.value==0:
					logger.info("set hype level relay level " + str(hype_level))
					relay5.on()
				if relay6.value==1:
					relay6.off()
				return True
			if hype_level==5:
				#turn on relay 2 + relay 3 + relay 4 + relay 5 + relay 6
				if relay2.value==0:
					relay2.on()
				if relay3.value==0:
					relay3.on()
				if relay4.value==0:
					relay4.on()
				if relay5.value==0:
					relay5.on()
				if relay6.value==0:
					logger.info("set hype level relay level " + str(hype_level))
					relay6.on()
				return True
			else:
				#do nothing
				return False
		except Exception as e:
			logger.error("set hype train error")
			return False

def set_follow(state):
	if enable_follow==1:
		try:
			if relay7.value==state:
				#do nothing
				return True
			if state==1:
				#turn on relay
				logger.info("set follow state " + str(state))
				relay7.on()
			if state==0:
				#turn off relay
				logger.info("set follow state " + str(state))
				relay7.off()
  		  	else:
				#do nothing
				return False
			return True
		except Exception as e:
			logger.error("set follow error")
			return False

def set_spare(state):
	if enable_spare==1:
		try:
			if relay8.value==state:
				#do nothing
				return True
			if state==1:
				#turn on relay
				logger.info("set spare " + str(state))
				relay8.on()
			if state==0:
				#turn off relay
				logger.info("set spare " + str(state))
				relay8.off()
  		  	else:
				#do nothing
				return False
			return True
		except Exception as e:
			logger.error("set spare error")
			return False