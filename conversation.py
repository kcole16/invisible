import json

import requests

from utils import getenv, connect_db
from facebook import get_message, respond_to_message
from validate import *

class Conversation():

    def __init__(self, con_id, response, last_message, access_token):
        self.con_id = con_id
        self.last_message = last_message
        self.response = response
        self.access_token = access_token
        self.responses = json.load(open('messages.json'))['messages']

    def update_conversation(self):
        db = connect_db()
        params = {'access_token': self.access_token}
        url = 'https://graph.facebook.com/v2.5/%s' % self.con_id
        r = requests.get(url, params=params) 
        data = r.json()
        response = self.response+1
        self.response = response
        print response
        db.conversations.update({'con_id':self.con_id}, {'con_id':self.con_id, 
            'updated_time':data['updated_time'], 'response': response})

    def respond(self):
        # Get response from response tree based on response number

        try:
            response_branch = self.responses[str(self.response)]
        except KeyError:
            response = "That's all for now! I'll probably just repeat myself :)"
            issue_response(self.con_id, response, self.access_token)
        else:
            validator = response_branch['validator']
            last_message = get_message(self.con_id, self.access_token)
            if last_message and eval("%s('%s')" % (validator, last_message)):
                response = response_branch['content']
                self.update_conversation()
                respond_to_message(response, self.con_id, self.access_token)
            elif last_message:
                response = response_branch['error_message']
                respond_to_message(response, self.con_id, self.access_token)
            else:
                pass


# def update_conversation(con_id, response, access_token):
#     db = connect_db()
#     params = {'access_token': access_token}
#     url = 'https://graph.facebook.com/v2.5/%s' % con_id
#     r = requests.get(url, params=params) 
#     data = r.json()
#     db.conversations.update({'con_id':con_id}, {'con_id':con_id, 
#         'updated_time':data['updated_time'], 'response': response+1})

# def initial_response(con_id, access_token):
#     response = """Hello! Thanks for trying out the Invisible API demo! This is a basic version of our full product, but hopefully it give you a good idea of what we do! First off, what is your name?"""
#     data = {'access_token': access_token, 'message': response}
#     url = 'https://graph.facebook.com/v2.5/%s/messages' % con_id
#     r = requests.post(url, data=data) 
#     if r.ok:
#         update_conversation(con_id, 0, access_token)

# def weather_response(location):
#     api_key = getenv('WEATHER_API_KEY')
#     params = {'APPID': api_key, 'q':location, 'units':'metric'}
#     url = 'http://api.openweathermap.org/data/2.5/weather'
#     r = requests.get(url, params=params)
#     data = r.json()
#     weather = data['weather'][0]['description']
#     high = data['main']['temp_max']
#     low = data['main']['temp_min']
#     response = "Today in %s: %s. The high is %s C and the low is %s C. Have a great day!" % (
#             location,
#             weather,
#             high, 
#             low
#         )
#     return response

# def create_response(info, response):
#     if response == 1:
#         response = "Hi %s! Here's a quick example, today's weather forecast. Where are you located?" % info
#     elif response == 2:
#         response = weather_response(info)
#     elif response == 3:
#         response = "That's all for now! This is just a very small sneak peak of our potential. Check out our website for more details: http://www.invisibleapi.com. If you have any questions, send them to kendall@invisibleapi.com."
#     elif response == 4:
#         response = "Thanks again for your interest! I'm going to start repeating myself now..."
#     elif response == 5:
#         response = "Repeating"
#     elif response == 6:
#         response = "Still repeating"
#     else:
#         base = "still "
#         root = base * (response - 6)
#         response = "Still "+root+"repeating"

#     return response
