"""
    Base code for Slackbot sourced from   

    SCRIPT REQUIREMENTS
        Python
        slackclient API wrapper
        pytz module
        bot id (found from expot #create variable for this later)
        bot API (found from expot #create variable for this later)
"""
import os
import time
import requests
from datetime import datetime,tzinfo,timedelta
from slackclient import SlackClient


##################################################################
#Current Time
##################################################################
#Class handles time conversion from UTC to CST
class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

#Update the first parameter during Daylight Savings
CST = Zone(-5,False,'CST')

current_date_time = datetime.now(CST).strftime('%m/%d/%Y %H:%M')

##################################################################
#Current Weather
##################################################################

#Selma TX city ID = 4727785
#For different city IDs, visit http://bulk.openweathermap.org/sample/
weather_r = requests.get('http://api.openweathermap.org/data/2.5/weather?id=4727785&units=imperial&APPID=0cd3eb7242f017f9529514bde44103a5')
#for full list, print r.json()

weather_main = weather_r.json()['main']
weather_current = "*Temp:* " + str(weather_main['temp'])[0:2]
weather_max = "*Max:* " + str(weather_main['temp_max'])[0:2]
weather_min = "*Min:* " + str(weather_main['temp_min'])[0:2]


##################################################################
# Giphy Search
##################################################################
giphy = ""
def giphy_random(giphy_search_query):
    # Request
    # GET http://api.giphy.com/v1/gifs/search
    #http://api.giphy.com/v1/stickers/random?api_key=dc6zaTOxFJmzC&tag=oops
    #http://api.giphy.com/v1/gifs/search?q=funny+cat&api_key=dc6zaTOxFJmzC

    try:
        response = requests.get(
            url="http://api.giphy.com/v1/gifs/random",
            params={
                "api_key": "dc6zaTOxFJmzC",
                "limit": "1",
                "fmt": "json",
                "tag": str(giphy_search_query),
            },
        )
        #print('Response HTTP Status Code: {status_code}'.format(
        #    status_code=response.status_code))
        #print('Response HTTP Response Body: {content}'.format(
        #    content=response.content))
        giphy_response_json = response.json()['data']
        global giphy
        giphy = giphy_response_json['fixed_height_downsampled_url']
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

##########################################################################################
# Slackbot stuff I don't understand
# Base code from https://www.fullstackpython.com/blog/build-first-slack-bot-python.htmlBOT
# Eventually --- Use message buttons for coffee confirmation https://api.slack.com/docs/message-buttons 
##########################################################################################

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "do"
MORNING_COMMAND = "good morning"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    giphy_random("error 404")
    response = "Uh oh, an error occurred!" + "\n" + giphy
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    if command.startswith(MORNING_COMMAND):
        response = "Good morning & thank klevin, it is " + current_date_time + "\n" + "Oh, and here's the current weather: " + "\n" + weather_current + "\n" + weather_max + "\n" + weather_min +"\n"+"\n"+":rat:"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
