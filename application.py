import uuid
import time
import urllib
import requests

from flask import Flask, jsonify, render_template, redirect, request
from utils import connect_db, getenv
from message import initial_response, update_conversation, create_response

application = Flask(__name__) #establishing flask application

@application.route('/home/', methods=['GET'])
def home():
    # if request.method == 'POST':
    return jsonify(data="Hello World")

def respond_to_message(message, convo_id, response_num):
    response = create_response(message, response_num)
    access_token = getenv('ACCESS_TOKEN')
    data = {'access_token': access_token, 'message': response}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % convo_id
    r = requests.post(url, data=data) 
    print r.text

def get_message(message_id, convo_id, response_num):
    access_token = getenv('ACCESS_TOKEN')
    params = {'access_token': access_token, 'fields':'message'}
    url = 'https://graph.facebook.com/v2.5/%s' % message_id
    r = requests.get(url, params=params)
    message = r.json()['message']
    respond_to_message(message, convo_id, response_num)
    update_conversation(convo_id, response_num)

def get_messages(convo_id, response_num):
    access_token = getenv('ACCESS_TOKEN')
    params = {'access_token': access_token, 'fields':'from'}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % convo_id
    r = requests.get(url, params=params)
    data = r.json()['data']
    newest_message = data[0]
    id = newest_message['id']
    if newest_message['from']['name'] != 'Invisible':
        get_message(id, convo_id, response_num)

def get_conversations():
    db = connect_db()
    access_token = getenv('ACCESS_TOKEN')
    params = {'access_token': access_token}
    page_id = '102940933437533'
    url = 'https://graph.facebook.com/v2.5/%s/conversations' % page_id
    r = requests.get(url, params=params)
    data = r.json()['data']
    for convo in data:
        id = str(convo['id'])
        conversation = db.conversations.find_one({'convo_id':id})
        if conversation is None:
            db.conversations.insert({'convo_id':id, 'updated_time': convo['updated_time'], 'response':0})
            initial_response(id)
        elif convo['updated_time'] != conversation['updated_time']:
            get_messages(id, conversation['response'])

if __name__ == "__main__":
    application.debug = True
    while application.debug:
        get_conversations()
        time.sleep(2)
    application.run()
