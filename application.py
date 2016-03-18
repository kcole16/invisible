import uuid
import time
import urllib
import requests

from flask import Flask, jsonify, render_template, redirect, request
from utils import connect_db, getenv, get_account, update_account
from message import initial_response

application = Flask(__name__) #establishing flask application

convo_ids = []
conversations = {}

@application.route('/home/', methods=['GET'])
def home():
    # if request.method == 'POST':
    return jsonify(data="Hello World")

def respond_to_message(message, convo_id):
    response = message+" +1"
    access_token = getenv('ACCESS_TOKEN')
    data = {'access_token': access_token, 'message': response}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % convo_id
    r = requests.post(url, data=data) 

def get_message(message_id, convo_id):
    print message_id
    access_token = getenv('ACCESS_TOKEN')
    params = {'access_token': access_token, 'fields':'message'}
    url = 'https://graph.facebook.com/v2.5/%s' % message_id
    r = requests.get(url, params=params)
    message = r.json()['message']
    print message
    respond_to_message(message, convo_id)

def get_messages(convo_id):
    print convo_id
    access_token = getenv('ACCESS_TOKEN')
    params = {'access_token': access_token, 'fields':'from'}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % convo_id
    r = requests.get(url, params=params)
    data = r.json()['data']
    newest_message = data[0]
    id = newest_message['id']
    if newest_message['from']['name'] != 'Invisible':
        get_message(id, convo_id)

def get_conversations():
    global conversations
    global convo_ids
    access_token = getenv('ACCESS_TOKEN')
    params = {'access_token': access_token}
    page_id = '102940933437533'
    url = 'https://graph.facebook.com/v2.5/%s/conversations' % page_id
    r = requests.get(url, params=params)
    data = r.json()['data']
    for convo in data:
        id = convo['id']
        if id not in convo_ids:
            conversation = {
                'id':convo['id'],
                'updated_time':convo['updated_time']
            }
            conversations[id] = {'updated_time': convo['updated_time']}
            convo_ids.append(id)
            initial_response(id)
        else:
            if convo['updated_time'] != conversations[id]['updated_time']:
                get_messages(id)
                conversations[id]['updated_time'] = convo['updated_time']

if __name__ == "__main__":
    application.debug = True
    while application.debug:
        get_conversations()
        time.sleep(2)
    application.run()
