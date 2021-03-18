import datetime
from datetime import timedelta
import pprint
from config import *
from helper import *
import time
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('Twitch Relay Monitor')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/home/pi/twitch_relay_monitor/logs/app.log', maxBytes=200000, backupCount=2)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def print_verbose(comment):
	if verbose_mode==1:
		#print to screen
		print(comment)
	else:
		logger.info(comment)

#First, start by getting token to access Twitch api
r=get_token(client_id,client_secret,grant_type,scope)
if r == False:
	# if there is a problem, end the program
	logger.error("Can't Auth user")
	exit(1)

# since streamer username is given we need to get its broadcaster id for other requests
broadcaster=get_broadcaster_id(client_id,username)
if broadcaster==False:
	# if there is a problem, end the program
	logger.error("Can not get broadcster id")
	exit(1)

if "access_token" not in r:
	# if there is a problem, end the program
	logger.error("Access token is missing " + str(r))
	exit(1)
	
access_token=r['access_token'];
expires_in=r['expires_in']

# Fresh token interval will keep track of the time we need to validate the token
fresh_token_interval=token_validate_interval
skip_count=0


while True:
	wait_time=online_user_wait_time
	
	# refresh token if expired 
	if fresh_token_interval <30:
		#confirm the token is valid
		if is_valid_token(access_token) ==False:
			r=get_token(client_id,client_secret,grant_type,scope)
			if r ==False:
				skip_count=skip_count+1
				logger.info("Fresh Token Skip get token , skip:" + str(skip_count))
				time.sleep(skip_wait_time)
				continue
			access_token=r['access_token'];
			expires_in=r['expires_in']
		fresh_token_interval=token_validate_interval


	if is_user_live(client_id,access_token,username):
		print_verbose("User ["+username+"] online")
		set_stream(1)
		user_streaming_flag=1
	else:
		print_verbose("User ["+username+"] offline")
		set_hypetrain(0)
		set_follow(0)
		set_stream(0)
		user_streaming_flag=0
		wait_time=user_offline_wait_time

	last_hype_train_action=get_last_hype_train_action(client_id,access_token,broadcaster["_id"])
	if last_hype_train_action ==False:
		skip_count=skip_count+1
		logger.info("Hype Train Skip get token , skip:" + str(skip_count))
		time.sleep(skip_wait_time)
		continue


	#retrieve most recent follow event
	last_follow_action=get_last_follow_action(client_id,access_token,broadcaster["_id"])
	if last_follow_action ==False:
		skip_count=skip_count+1
		logger.info("Follow Skip get token , skip:" + str(skip_count))
		time.sleep(skip_wait_time)
		continue

	#mark follow if last follow event is < event notification time from current time
	if user_streaming_flag==1:
		subscribe_time=last_follow_action["data"][0]["followed_at"]
		subscribe_time=datetime.datetime.strptime(subscribe_time,'%Y-%m-%dT%H:%M:%SZ')
		if datetime.datetime.utcnow() < subscribe_time + timedelta(seconds=event_notification_delay):
			print_verbose("Relay Function - Follow Event Active")
			set_follow(1)
		else:
			set_follow(0)

	#set hype train state
	if(is_train_active(last_hype_train_action["data"])):
		print_verbose("Train Active at level " + str(last_hype_train_action["data"][0]["event_data"]['level']))
		level=last_hype_train_action["data"][0]["event_data"]['level']
		if 1 <= level <= 5:
			if user_streaming_flag==1:
				logger.info("Relay Function - Hype Train Event")
				set_hypetrain(level)
		wait_time=5 # active hype train wait time in seconds
	else:
		print_verbose("Train not active")
		set_hypetrain(0)
		wait_time=online_user_wait_time

	fresh_token_interval=fresh_token_interval-wait_time

	if skip_count == max_skip_count:
		logger.error("Skip count limit reached")
		exit(1)
	    
	time.sleep(wait_time)
	#reset skip_count if one request execute without issue within max_skip_count
	skip_count=0 