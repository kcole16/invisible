import requests

def respond_to_message(response, con_id, access_token):
    data = {'access_token': access_token, 'message': response}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % con_id
    r = requests.post(url, data=data) 
    print r.text

def get_message(con_id, access_token):
    params = {'access_token': access_token, 'fields':'from'}
    url = 'https://graph.facebook.com/v2.5/%s/messages' % con_id
    r = requests.get(url, params=params)
    data = r.json()['data']
    newest_message = data[0]
    id = newest_message['id']
    if newest_message['from']['name'] != 'Invisible':
	    params = {'access_token': access_token, 'fields':'message'}
	    url = 'https://graph.facebook.com/v2.5/%s' % id
	    r = requests.get(url, params=params)
	    message = r.json()['message']
	    return message
    else:
    	return None
