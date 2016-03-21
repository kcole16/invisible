import uuid
import time
import urllib
import requests

from flask import Flask, jsonify, render_template, redirect, request
from utils import connect_db, getenv, get_page_token
from conversation import initial_response, update_conversation, create_response

application = Flask(__name__) #establishing flask application

def respond_to_message(message, convo_id, response_num, access_token):
    response = create_response(message, response_num)
    data = {'access_token': access_token, 'message': response}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % convo_id
    r = requests.post(url, data=data) 
    print r.text

def get_message(message_id, convo_id, response_num, access_token):
    params = {'access_token': access_token, 'fields':'message'}
    url = 'https://graph.facebook.com/v2.5/%s' % message_id
    r = requests.get(url, params=params)
    message = r.json()['message']
    respond_to_message(message, convo_id, response_num, access_token)
    update_conversation(convo_id, response_num, access_token)

def get_messages(convo_id, response_num, access_token):
    params = {'access_token': access_token, 'fields':'from'}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % convo_id
    r = requests.get(url, params=params)
    data = r.json()['data']
    newest_message = data[0]
    id = newest_message['id']
    if newest_message['from']['name'] != 'Invisible':
        get_message(id, convo_id, response_num, access_token)

def get_conversations(access_token):
    db = connect_db()
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
            initial_response(id, access_token)
        elif convo['updated_time'] != conversation['updated_time']:
            get_messages(id, conversation['response'], access_token)

@application.route('/fb', methods=['GET', 'POST'])
def fb():
    client_id = getenv('CLIENT_ID')
    client_secret = getenv('CLIENT_SECRET')
    url = "https://www.facebook.com/dialog/oauth?client_id=%s&client_secret=%s&redirect_uri=http://localhost:5000/&scope=read_page_mailboxes,manage_pages, publish_pages,pages_show_list,pages_manage_cta,pages_manage_leads" % (client_id, client_secret)
    return redirect(url)

@application.route('/', methods=['GET', 'POST'])
def home():
    code = request.args['code']
    url = "https://graph.facebook.com/oauth/access_token"
    client_id = getenv('CLIENT_ID')
    client_secret = getenv('CLIENT_SECRET')
    params = {
        'client_id':client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://localhost:5000/',
        'code':code
    }
    r = requests.get(url, params)
    access_token = r.text.split('access_token=')[1]

    return jsonify(data=access_token)

if __name__ == "__main__":
    application.debug = True
    page_token = get_page_token()
    pagecheck = 1
    while application.debug:
        print "Hey"
        if pagecheck % 10 == 0:
            page_token = get_page_token()
            get_conversations(page_token)
            pagecheck = 1
            time.sleep(2)
        else:
            get_conversations(page_token)
            pagecheck += 1
            time.sleep(2)
    application.run()


