import requests

from utils import getenv, connect_db
from validators import *

class Conversation():

    def __init__(self, con_id, response):
        self.con_id = con_id
        self.response = response
        self.access_token = getenv('ACCESS_TOKEN')

    def update_conversation(self):
        db = connect_db()
        params = {'access_token': self.access_token}
        url = 'https://graph.facebook.com/v2.5/%s' % con_id
        r = requests.get(url, params=params) 
        data = r.json()
        db.conversations.update({'con_id':con_id}, {'con_id':con_id, 
            'updated_time':data['updated_time'], 'response': response+1})

    def complete_response(self):
        

def initial_response(con_id):
    response = """Hello! Thanks for trying out the Invisible API demo! This is a basic version of our full product, but hopefully it give you a good idea of what we do! First off, what is your name?"""
    data = {'access_token': self.access_token, 'message': response}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % con_id
    r = requests.post(url, data=data) 
    if r.ok:
        update_conversation(con_id, 0)

def weather_response(location):
    api_key = getenv('WEATHER_API_KEY')
    params = {'APPID': api_key, 'q':location, 'units':'metric'}
    url = 'http://api.openweathermap.org/data/2.5/weather'
    r = requests.get(url, params=params)
    data = r.json()
    weather = data['weather'][0]['description']
    high = data['main']['temp_max']
    low = data['main']['temp_min']
    response = "Today in %s: %s. The high is %s C and the low is %s C. Have a great day!" % (
            location,
            weather,
            high, 
            low
        )
    return response

def create_response(info, response):
    if response == 1:
        response = "Hi %s! Here's a quick example, today's weather forecast. Where are you located?" % info
    elif response == 2:
        response = weather_response(info)
    elif response == 3:
        response = "That's all for now! This is just a very small sneak peak of our potential. Check out our website for more details: http://www.invisibleapi.com. If you have any questions, send them to kendall@invisibleapi.com."
    elif response == 4:
        response = "Thanks again for your interest! I'm going to start repeating myself now..."
    elif response == 5:
        response = "Repeating"
    elif response == 6:
        response = "Still repeating"
    else:
        base = "still "
        root = base * (response - 6)
        response = "Still "+root+"repeating"

    return response
