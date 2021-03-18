#setting
# client id from https://dev.twitch.tv/console/apps/create
client_id=""

# client secret from https://dev.twitch.tv/console/apps/create
client_secret=""

# grant type Must be client_credentials
# https://dev.twitch.tv/docs/authentication/getting-tokens-oauth#oauth-client-credentials-flow
grant_type="client_credentials"

# scope for hype train only 
# https://dev.twitch.tv/docs/authentication#scopes
scope="channel:read:hype_train"

# channel username 
username=""

# time to wait between request if the user not streaming
user_offline_wait_time=30 #60 seconds.

# time to wait between request if the user streaming
online_user_wait_time=10 #10 seconds.

# time to check if the token is valid
token_validate_interval=60*60*1 #1 hour

# maximum number of skipping when there is a problem before the program stop
max_skip_count=5

# cooldown time before sending a new request when an error happens.
skip_wait_time=5 #5 seconds

# max time in seconds for a subscription or follow event to be active after the event relative to UTC
# NB: time set should include allowances for other configuration intervals ie online_user_wait_time
event_notification_delay=15 #15 seconds

# enable specific relay functions - 1 = on and 0 = off
# this will not disable the API calls associated that will trigger the relay only turn the relay setting function on and off
enable_stream=1 #enable relay 1 use
enable_hype=1   #enable relay 2-6 use
enable_follow=1 #enable relay 7 use
enable_spare=0    #enable relay 8 use

# enable verbose mode for printing messages direct to console (1) or log files (0)
verbose_mode=0
