import requests

from utils import getenv

def initial_response(convo_id):
    response = """Hello! Thanks for trying out the Invisible API demo! This is a basic version of our full product, but hopefully it give you a good idea of what we do! First off, what is your name?"""
    access_token = getenv('ACCESS_TOKEN')
    data = {'access_token': access_token, 'message': response}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % convo_id
    r = requests.post(url, data=data) 