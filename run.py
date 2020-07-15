import datetime
import pprint
from config import *
from helper import *
import time

#First, start by getting token to access Twitch api
r=get_token(client_id,client_secret,grant_type,scope)
if r == False:
	# if there is a problem, end the program
	print("Can't Auth user")
	exit(1)

# since streamer username is given we need to get its broadcaster id for other requests
broadcaster=get_broadcaster_id(client_id,username)
if broadcaster==False:
	# if there is a problem, end the program
	print("Can not get broadcster id")
	exit(1)

if "access_token" not in r:
	# if there is a problem, end the program
	print("Access token is missing ", r)
	exit(1)
	
access_token=r['access_token'];
expires_in=r['expires_in']

# Fresh token interval will keep track of the time we need to validate the token
fresh_token_interval=token_validate_interval
skip_count=0
wait_type="nt" #nt: no hype train, cd: cooldown, at: active hype train
# save old value of wait_type to clear the LED display when the new event happen.
prev_wait_type="nt"
#for active train 
prev_x=1
prev_y=0

while True:
	wait_time=online_user_wait_time
	
	# refresh token if expired 
	if fresh_token_interval <30:
		#confirm the token is valid
		if is_valid_token(access_token) ==False:
			r=get_token(client_id,client_secret,grant_type,scope)
			if r ==False:
				skip_count=skip_count+1
				print("Skip get token , skip:", skip_count)
				time.sleep(skip_wait_time)
				continue
			access_token=r['access_token'];
			expires_in=r['expires_in']
		fresh_token_interval=token_validate_interval


	if is_user_live(client_id,access_token,username):
		print("User ["+username+"] online")
	else:
		print("User ["+username+"] offline")
		wait_time=user_offline_wait_time

	last_hype_train_action=get_last_hype_train_action(client_id,access_token,broadcaster["_id"])
	if last_hype_train_action ==False:
		skip_count=skip_count+1
		print("Skip get token , skip:", skip_count)
		time.sleep(skip_wait_time)
		continue
		
	if(is_train_active(last_hype_train_action["data"])):
		#pprint.pprint(last_hype_train_action["data"])
		precent=int(round(last_hype_train_action["data"][0]["event_data"]['total']*100/last_hype_train_action["data"][0]["event_data"]['goal']))
		print("Train Active at level ",last_hype_train_action["data"][0]["event_data"]['level'])
		print("Level complete %: ",precent)
		wait_type="at"
		level=last_hype_train_action["data"][0]["event_data"]['level']
		# clear ScrollpHatHD display before showing the progress
		if prev_wait_type !="at":
			clear_pixel()
		prev_x,prev_y=progress_show(level,precent,prev_x,prev_y)
		wait_time=5 # active hype train wait time in seconds
	else:
		print("Train not active")
		wait_type="nt"
		wait_time=online_user_wait_time
	#check hype train cooldown_end_time
	if "data" in last_hype_train_action:
		if len(last_hype_train_action["data"]) >0:
			cooldown_end_time=last_hype_train_action["data"][0]["event_data"]["cooldown_end_time"]
			cooldown_end_time=datetime.datetime.strptime(cooldown_end_time,'%Y-%m-%dT%H:%M:%SZ')
			if cooldown_end_time > datetime.datetime.utcnow() and is_train_active(last_hype_train_action["data"])==False:
				if int((cooldown_end_time - datetime.datetime.utcnow()).total_seconds()-5*60) >0:
					wait_time=int((cooldown_end_time - datetime.datetime.utcnow()).total_seconds())-5*60 
					print("Cool down end:",int((cooldown_end_time - datetime.datetime.utcnow()).total_seconds())-5*60 )
					wait_type="cd"
	fresh_token_interval=fresh_token_interval-wait_time

	if skip_count == max_skip_count:
		print("Skip count limit reached")
		exit(1)

	#print("wait_type:",wait_type)
	if wait_type == "cd":
		if prev_wait_type !="cd":
			prev_x=1
			prev_y=0
			clear_pixel()
		while wait_time > 0:
			next_hype_train=datetime.datetime.strptime(last_hype_train_action["data"][0]["event_data"]["cooldown_end_time"]  ,'%Y-%m-%dT%H:%M:%SZ')
			if datetime.datetime.utcnow() >= next_hype_train:
				break 
			show_time(next_hype_train)
			time.sleep(1)
			wait_time =wait_time-1
	elif wait_type == "nt":
		if prev_wait_type !="nt":
			prev_x=1
			prev_y=0
			clear_pixel()
		while wait_time >0:
			rand_pixel()
			time.sleep(1)
			wait_time =wait_time-1
	
	prev_wait_type=wait_type	    
	time.sleep(wait_time)
	#reset skip_count if one request execute without issue within max_skip_count
	skip_count=0 
