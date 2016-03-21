import os 
import sys
import datetime
from datetime import timedelta

#dependencies
import pymongo
import requests
# from bson import json_util

def getenv(key):
   val = os.environ.get(key)
   if val:
       return val
   elif os.path.isfile('.env'):
       f = open('.env')
       s = f.read()
       f.close()
       for line in s.strip().split('\n'):
           k, v = line.split('=')
           if k == key:
               return v
   return None

def connect_db():
   url = getenv('MONGO_URL')
   app_name = getenv('MONGO_APP_NAME')
   client = pymongo.MongoClient(url)
   db = client[app_name]
   return db


def get_page_token():
  access_token = getenv('ACCESS_TOKEN')
  url = "https://graph.facebook.com/me/accounts"
  params = {'access_token':access_token}
  r = requests.get(url, params=params)
  page = r.json()['data'][0]
  if page['name'] == 'Invisible':
      page_token = page['access_token']
  else: 
      page_token = None

  return page_token
