# Twitch Relay Monitor
All code credit should go to https://github.com/plusmnt/twitch-train-led as the original code source that was modified to make this work.

So I know some people who host a weekly live show on Twitch and it was discussed about having something explode when a Hype Train happens. As this seems a bit.... firey deathy, I decided to make a device that will give more options, through setting electrical relays that can be connected to lights/motors/inflateable wackyman air pumps/etc to be triggered when the corresponding Twitch event occurs. Limited to the events that are available through teh Twitch API that will work with this type of device without substantial more technical knowledge and setup.

## How to use
The device itself uses the Twitch API so you need a Client ID and Secret from the Twitch Developer Portal. As we are not retrieving any information that Twitch deems personal through these functions you do not necessarily have to have a API key created under the channel you are using this on but it does help to keep things together. Put the Client ID + Secret + Channel ID into the configuration file and you are 90% good to go if you have all the hardware configured and connected correctly (refer to the Hackaday.io for more on the hardware build + files).

When the run.py script is run the logic will run in a loop polling for events from Twtich then setting relays appropriately. The device theorectically could make up to 60 API reuqests per minute with the Twitch Rate limit being 120. There is some room for adjustment in the config file but do also allow for time for the electrical device to power on/off without being shorted out.

Depending on how/where you use this you may need to adjust the /logs/ destination in the helper.py and run.py files to avoid errors or to actually get logs.

### Stream Online
If a Stream is online all other conditions are valid for checks but the first relay is also set to give an "on air" notification via relay that can be connected to a 'live stream' or 'on air' type light/sign. While the stream is online the cycle for checks is increased for all other events while if the stream is offline the user_offline_wait_time is used to determine the speed of while loop cycles. The Stream Online functions may require revision as while the Hype Train and Follow functions use the newer Helix based Twitch APIs the Stream Online (and token retrieval) based APIs are not, this is due to there not being a Helix based option at this time.

### Hype train Levels
Hype Levels for Twtich are currently set from 1 through to 5 with each level being valid for upto about 4mins and 30 seconds. If the Hype Train succeeds in reaching the next level before the timer runs out it will reset the timer. If not the hype train will end and there is a cooldown value that is set in the channel options (not here) that says how long before the next hype train can happen (see the cool down functions in the original unforked code). When a Hype Train is at each level the level function is called to check each relays current state and then turn them on or off appropriately (this allows for hype trains to skip levels which can occur). When the Hype train is not in effect it will be set as level 0 which triggers all Hype relays to be turned off.

### Follow
The follow function will pickup if a follow event has occured within event_notification_delay seconds from the current time. If the time is less the relay is enabled and if the time is more than it is disabled. The intent here is a follow gives a short notification with the relay turning on and off for a short amount of time. The amount of time the relay stays on is a combination of the event delay time set as well as the online user wait time which manages the entire while cycle

## Config
| Vailable                | Description                                                                  | Default value           |
|-------------------------|------------------------------------------------------------------------------|-------------------------|
| client_id               | client_id from [Twitch API](https://dev.twitch.tv/console/apps/create)       | not empty               |
| client_secret           | client_secret from [Twitch API](https://dev.twitch.tv/console/apps/create)   | not empty               |
| grant_type              | grant type Must be `client_credentials`                                      | client_credentials      |
| scope                   | permissions the program requires                                             | channel:read:hype_train |
| username                | streamer username                                                            | not empty               |
| user_offline_wait_time  | time in seconds to wait between request if the user not streaming            | 30                      |
| online_user_wait_time   | time in seconds to wait between request if the user streaming                | 10                      |
| token_validate_interval | time in seconds  to check if the token is valid                              | 3600                    |
| max_skip_count          | maximum number of skipping when there is a problem before the program stop   | 5                       |
| event_notification_delay| cooldown time in seconds before sending a new request when an error happens. | 15                      |
| enable_stream           | enable relay 1 use                                                           | 1                       |
| enable_hype             | enable relay 2-6 use                                                         | 1                       |
| enable_follow           | enable relay 7 use                                                           | 1                       |
| enable_spare            | enable relay 8 use                                                           | 0                       |
| verbose_mode            | Simple flag to change from printing to console or printing to log file       | 0                       |

### Config note 
- If you want to test or modify this without having a relay board connected, you can disable the setting of the relays by changing the configuration file flags

## Hardware
* [Raspberry Pi Zero WH](https://www.adafruit.com/product/3708)
* Momentary pushbutton
* 8 channel 3.3v Relay

### Setup 
* Setup a Raspberry Pi - [Raspberry Pi Zero Headless Quick Start](https://learn.adafruit.com/raspberry-pi-zero-creation)
* Add Power Button - [Wiring and some code that can be installed as a service to work with a momentary push button](https://howchoo.com/g/mwnlytk3zmm/how-to-add-a-power-button-to-your-raspberry-pi)
* Clone repo to your Pi using SSH and 'git clone https://github.com/evilspyboy/twitch-relay-monitor.git'
* Create a .sh file and have it run automatically - [There are a bunch of ways to do this, I went the bash.rc because I wanted it to run last thing, but there are other ways to do this](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)

## Code
the code consists of 3 main files 
- `config.sample.py` : this contains all the configuration options and should be renamed to `config.py` before running.
- `helper.py`: this contains Twitch API functions and relay state functions.
- `run.py`: this is the main file that use above two files to run, this file contains the logic of running the program.
- /logs/ directory for the app.log and helper.log files to be dumped into. Log files will rotate between up to 3 copies of the logfile to cap the log size


## Expansion
- There is a Spare relay due to the Subscribe option on the current Twitch API using a Pub/Sub interface which doesnt really work with this being more of an appliance to turn on and off than a full on integration. The spare function could be used with another sort of notification or be used if/when the Twitch API is added to
