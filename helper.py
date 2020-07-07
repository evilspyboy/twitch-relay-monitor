import requests
import datetime
import json
#Get token
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
		print("get_token network error ",e.message)
		return False

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
		print("get hype train action network error ",e.message)
		return False


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
		print("get_broadcaster_id network error ",e.message)
		return False

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
		print("can not check if user live ",e.message)
		return False

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
		print("is_valid_token network error ",e.message)
		return False	
	return True
	
