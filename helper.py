import requests
import datetime
import json
#Get token
def get_token(client_id,client_secret,grant_type,scope):

	url = "https://id.twitch.tv/oauth2/token?client_id="+ \
		client_id+"&client_secret="+ \
		client_secret+"&grant_type="+ \
		grant_type+"&scope="+scope
	response = requests.request("POST",url)
	r=json.loads(response.text)
	return r

def get_last_hype_train_action(client_id,access_token,user_id):
	url = "https://api.twitch.tv/helix/hypetrain/events?broadcaster_id="+ \
		user_id + \
		"&first=1"
	headers = {
	  'Client-ID': client_id,
	  'Authorization': 'Bearer '+access_token
	}
	response = requests.request("GET", url, headers=headers)
	return json.loads(response.text)


def get_broadcaster_id(client_id,username):
	url = "https://api.twitch.tv/kraken/users?login="+username
	headers = {
	  'Accept': 'application/vnd.twitchtv.v5+json',
	  'Client-ID': client_id
	}
	response = requests.request("GET", url, headers=headers)
	r=json.loads(response.text)
	return r['users'][0]

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

	payload = {}
	headers = {
	  'Client-ID': client_id,
	  'Authorization': 'Bearer '+access_token
	}

	response = requests.request("GET", url, headers=headers, data = payload)
	r=json.loads(response.text)
	if len(r["data"])==0:
		return False
	return True

def is_valid_token(access_token):
	
	url = "https://id.twitch.tv/oauth2/validate"
	headers = {
	  'Authorization': 'OAuth '+access_token
	}

	response = requests.request("GET", url, headers=headers,)
	r=json.loads(response.text)
	if "expires_in" in r :
		if r['expires_in'] < 60*60*24: #1 day
			return False
	else:
		return False
	return True
	
