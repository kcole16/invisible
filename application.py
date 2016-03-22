import uuid
import time
import urllib
import requests

from flask import Flask, jsonify, render_template, redirect, request
from utils import connect_db, getenv, get_page_token
from conversation import Conversation

application = Flask(__name__) #establishing flask application

def get_conversations(access_token):
    db = connect_db()
    params = {'access_token': access_token}
    page_id = '102940933437533'
    url = 'https://graph.facebook.com/v2.5/%s/conversations' % page_id
    r = requests.get(url, params=params)
    data = r.json()['data']
    for convo in data:
        id = str(convo['id'])
        conversation = db.conversations.find_one({'con_id':id})
        if conversation is None:
            print access_token
            conversation = Conversation(id, 0, None, access_token, {})
            db.conversations.insert({'con_id':id, 'updated_time': convo['updated_time'], 'response':0, 'user': {}})
            conversation.respond()
        elif convo['updated_time'] != conversation['updated_time']:
            conversation = Conversation(id, conversation['response'], None, access_token, conversation['user'])
            conversation.respond()

@application.route('/fb', methods=['GET', 'POST'])
def fb():
    print "Hello"
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


