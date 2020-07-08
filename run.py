import datetime
import pprint
from config import *
from helper import *
import time

r=get_token(client_id,client_secret,grant_type,scope)
if r == False:
	print("Can't Auth user")
	exit(1)

broadcaster=get_broadcaster_id(client_id,username)
if broadcaster==False:
	print("Can not get broadcster id")
	exit(1)
access_token=r['access_token'];
expires_in=r['expires_in']
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
				print("Skipp get token , skip:", skip)
				time.sleep(skip_wait_time)
				continue
			access_token=r['access_token'];
			expires_in=r['expires_in']
		fresh_token_interval=token_validate_interval


	if is_user_live(client_id,access_token,username):
		print("User ["+username+"] online")
	else:
		print("User ["+username+"] offline")
		wait_time=60

	last_hype_train_action=get_last_hype_train_action(client_id,access_token,broadcaster["_id"])
	if last_hype_train_action ==False:
		skip_count=skip_count+1
		print("Skipp get token , skip:", skip)
		time.sleep(skip_wait_time)
		continue
	if(is_train_active(last_hype_train_action["data"])):
		#pprint.pprint(last_hype_train_action["data"])
		precent=int(round(last_hype_train_action["data"][0]["event_data"]['total']*100/last_hype_train_action["data"][0]["event_data"]['goal']))
		print("Train Active at level ",last_hype_train_action["data"][0]["event_data"]['level'])
		print("Level complete %: ",precent)
		wait_time=5
	else:
		print("Train not active")
		wait_time=online_user_wait_time
	#check hype train cooldown_end_time
	if "data" in last_hype_train_action:
		if len(last_hype_train_action["data"]) >0:
			cooldown_end_time=last_hype_train_action["data"][0]["event_data"]["cooldown_end_time"]
			cooldown_end_time=datetime.datetime.strptime(cooldown_end_time,'%Y-%m-%dT%H:%M:%SZ')
			if cooldown_end_time > datetime.datetime.utcnow() and is_train_active(last_hype_train_action["data"])==False:
				if int((cooldown_end_time - datetime.datetime.utcnow()).total_seconds()-60*5) >0:
					wait_time=int((cooldown_end_time - datetime.datetime.utcnow()).total_seconds()-60*5) #5min padding
					print("Cool down end:",int((cooldown_end_time - datetime.datetime.utcnow()).total_seconds()-60*5) )
	fresh_token_interval=fresh_token_interval-wait_time

	if skip_count == max_skip_count:
		print("Skip count limit reached")
		exit(1)

	time.sleep(wait_time)


