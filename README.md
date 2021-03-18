# Twitch Relay Monitor
All code credit should go to https://github.com/plusmnt/twitch-train-led as the original code source that was modified to make this work.



## How to use 

## How it work

### Stream Online

### Hype train Levels

### Follow

## Config
| Vailable                | Description                                                                  | Default value           |
|-------------------------|------------------------------------------------------------------------------|-------------------------|
| client_id               | client_id from [Twitch API](https://dev.twitch.tv/console/apps/create)       | not empty               |
| client_secret           | client_secret from [Twitch API](https://dev.twitch.tv/console/apps/create)   | not empty               |
| grant_type              | grant type Must be `client_credentials`                                      | client_credentials      |
| scope                   | permissions the program requires                                             | channel:read:hype_train |
| username                | streamer username                                                            | not empty               |
| user_offline_wait_time  | time in seconds to wait between request if the user not streaming            | 60                      |
| online_user_wait_time   | time in seconds to wait between request if the user streaming                | 30                      |
| token_validate_interval | time in seconds  to check if the token is valid                              | 3600                    |
| max_skip_count          | maximum number of skipping when there is a problem before the program stop   | 5                       |
| skip_wait_time          | cooldown time in seconds before sending a new request when an error happens. | 5                       |

### Config note 
- If you want to test or modify this without having a relay board connected, you can disable the setting of the relays by changing the configuration file flags

## Hardware
* [Raspberry Pi Zero WH](https://www.adafruit.com/product/3708)

### Setup 
* Setup a Raspberry Pi - [Raspberry Pi Zero Headless Quick Start](https://learn.adafruit.com/raspberry-pi-zero-creation)
* Add Power Button
* Add Code
* Add to bash.rc

## Code
the code consists of 3 main files 
- `config.sample.py` : this contains all the configuration options and should be renamed to `config.py` before running.
- `helper.py`: this contains Twitch API functions and ScrollpHatHD display functions.
- `run.py`: this is the main file that use above two files to run, this file contains the logic of running the program.
- /logs/ directory for the app.log and helper.log files to be dumped into. Log files will rotate between up to 3 copies of the logfile to cap the log size


## Expansion
- There is a Spare relay due to the Subscribe option on the current Twitch API using a Pub/Sub interface which doesnt really work with this being more of an appliance to turn on and off than a full on integration. The spare function could be used with another sort of notification or be used if/when the Twitch API is added to
