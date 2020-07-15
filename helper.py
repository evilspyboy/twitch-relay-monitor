import requests
import datetime
import json
import random
import scrollphathd
import time
import math
from scrollphathd.fonts import font3x5
# First you need to register you application to get Client id and client secret
# https://dev.twitch.tv/docs/authentication#registration

# Get app token to access twich API
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
		print("get_token timeout")
		return False
	except Exception as e:
		print("get_token network error")
		return False

# Check if the token is valid no not.
# return True if valid and False if invalid or network error
# https://dev.twitch.tv/docs/authentication#validating-requests
def is_valid_token(access_token):
	
	url = "https://id.twitch.tv/oauth2/validate"
	headers = {
	  'Authorization': 'OAuth '+access_token
	}
	try:
		response = requests.request("GET", url, headers=headers,)
		r=json.loads(response.text)
		if "expires_in" in r :
			if r['expires_in'] < 60*60*24: #1 day
				return False
		else:
			return False
	except requests.Timeout as err:
		print("is_valid_token timeout")
		return False
	except Exception as e:
		print("is_valid_token network error ")
		return False	
	return True


# get last train information
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
		print("get hype train action timeout")
		return False
	except Exception as e:
		print("get hype train action network error ")
		return False

# get broadcaster id from its username
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
		print("get_broadcaster_id timeout")
		return False
	except Exception as e:
		print("get_broadcaster_id network error ")
		return False

# check if tain is active by comparing current UTC time with hype train `expires_at`
# return True if the train active, return False if the train end.

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

# check if the user streaming
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
		print("is_user_live timeout")
		return False
	except Exception as e:
		print("can not check if user live ")
		return False



# LED functions

# this function will run when the train is not active.
# show random led pixel in random x,y location with brighness range from 0.1 to 0.5
# the function show or hide one pixel first, then hide random pixel

def rand_pixel():
    x =random.randint(1,15)
    y =random.randint(1,5)
    b =random.randint(0,5)/10
    scrollphathd.set_pixel(x,y,b)
    x =random.randint(1,15)
    y =random.randint(1,5)
    scrollphathd.set_pixel(x,y,0)
    scrollphathd.show()
    

# get location of the number in the rectangle watch
# giving sx as start X point and n as a number
# return x and y location 
    
def get_loc(sx,n):
    if n ==12:
        n=0
    if n ==0 or n == 6:
        y=1
        if n ==6:
            y =5
        return sx+1,y
    if n <= 5:
        y =n
        x=sx+2
        return x,y
    if n >=7:
        y =12-n
        x =sx
        return x,y

# Cooldown
# show 12 base watch countdown after the train end.
# based on this project: https://github.com/plusmnt/rectangle-scrollphathd-watch
# take future as datetime object and subtract it from utc now
# the output will be shown in the scrollphathd LED

def show_time(future):
    now=datetime.datetime.utcnow()
    diff = future-now
    print("Cooldown timer:",diff)
    time_str=str(diff).split(":")

    #Draw 3 rectangles background
    #sq: will give 1, 7, 13 as x starting point
    for sq in range(1, 15, 6):
        for sx in range(sq,sq+3):
            for sy in range(1,6):
                if sx ==sq+1 :
                    if sy !=1 and sy !=5:
                        continue
                scrollphathd.set_pixel(sx,sy,0.13)

#Draw ':'
    scrollphathd.set_pixel(5,2,0.13)
    scrollphathd.set_pixel(5,4,0.13)
    scrollphathd.set_pixel(11,2,0.13)
    scrollphathd.set_pixel(11,4,0.13)

    #set time
    second_12_base=int(float(time_str[2])/5+0.5)
    sec_x,sec_y=get_loc(13,second_12_base)
    scrollphathd.set_pixel(sec_x,sec_y,0.5)
    
    minute_12_base=int(int(time_str[1])/5+0.5)
    if int(time_str[1]) != 0:
        min_x,min_y=get_loc(7,minute_12_base)
        scrollphathd.set_pixel(min_x,min_y,0.5)

    hour=int(time_str[0])
    if hour !=0:
        if hour >12:
            hour=hour-12
        hour_x,hour_y=get_loc(1,hour)
        scrollphathd.set_pixel(hour_x,hour_y,0.5)
    scrollphathd.show()


# Active train function
# show the prorgress and the level of hype train.
# the funcation hype train level, pre as percentage (goal/total),  previous x value and previous y value.
# from 1 to 11 x value it will show the progress of the train.
# if the train pass 100% the led will stop in the last level 5 dot.
# the output will be shown in the scrollphatHD led display.

def progress_show(level,per,prev_x,prev_y):

    #max value for x in the led display
    max_x=11
    fix_x=prev_x
    fix_y=prev_y
    # get the upper value of the percentage e.g. 4.1 = 5
    cal_x = math.ceil(per /10)
    #print("Cal_x:",cal_x)
    if cal_x >=max_x:
        cal_x=max_x
    for y in range(fix_y,level,1):
        x_limit=max_x
        if y == level-1:
            x_limit=cal_x+1
            if x_limit >= max_x:
                x_limit =max_x
        for x in range(fix_x,x_limit):
            if prev_x !=1 or prev_y !=5 :
                scrollphathd.set_pixel(prev_x,5-prev_y,0.1)
            scrollphathd.set_pixel(x,5-y,0.3)
            scrollphathd.clear_rect(x=13,y=1,width=3,height=5)
            scrollphathd.write_string(str(y+1),x=13, y=1, font=font3x5, brightness=0.3)
            scrollphathd.show()
            time.sleep(0.1)
            prev_x=x
            prev_y=y
        
        fix_x=1

    return prev_x,prev_y

# clear ScrollpHatHD led display
def clear_pixel():
    scrollphathd.clear()
    scrollphathd.show()

