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
user_offline_wait_time=60 #60 seconds.

# time to wait between request if the user streaming
online_user_wait_time=30 #30 seconds.

# time to check if the token is valid
token_validate_interval=60*60*1 #1 hour

# maximum number of skipping when there is a problem before the program stop
max_skip_count=5

# cooldown time before sending a new request when an error happens.
skip_wait_time=5 #5 seconds
