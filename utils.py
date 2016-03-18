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

def connect_db(url, app_name):
   client = pymongo.MongoClient(getenv(url))
   db = client[getenv(app_name)]
   return db

def get_total(accounts):  
  balance = 0
  for account in accounts:
    balance += account['balance']
  return balance

def get_account(data):
  access_token = data['access_token']
  raw_accounts = data['accounts']
  sub_accounts = []
  for a in raw_accounts:
    try:
      name = a['meta']['official_name']
    except KeyError:
      name = a['meta']['name']
    type = a['type']
    if type == 'depository':
      balance = a['balance']['available']
    elif type == 'credit':
      balance = a['balance']['current'] * -1 #count credit owed as a liability
    else:
      balance = 0
    act = {
      'name': name,
      'type': type,
      'balance': balance
    }
    sub_accounts.append(act)
  total_balance = get_total(sub_accounts)
  account = {
    'access_token': access_token,
    'sub_accounts': sub_accounts,
    'total_balance': total_balance
  }
  return account

def update_account(account, auth_only):
  url = 'https://tartan.plaid.com/connect/get'
  if auth_only:
    url = 'https://tartan.plaid.com/auth/get'
  access_token = account['access_token']
  sub_accounts = []
  data = {'access_token': access_token,
  'client_id':getenv('PLAID_CLIENT_ID'), 'secret': getenv('PLAID_CLIENT_SECRET')}
  r = requests.post(url, data=data)
  if r.ok:
    transactions = []
    try:
      ts = r.json()['transactions']
    except KeyError:
      pass
    else:
      for t in ts:
        try:
          category = t['category'][0]
        except KeyError:
          category = None
        transaction = {
          'name': t['name'],
          'amount': int(t['amount'])*-1,
          'category': category,
          '_id': t['_account']
        } 
        transactions.append(transaction)
    accounts = r.json()['accounts']
    for a in accounts:
      try:
        name = a['meta']['official_name']
      except KeyError:
        name = a['meta']['name']
      type = a['type']
      if type == 'depository':
        balance = a['balance']['available']
      elif type == 'credit':
        balance = a['balance']['current'] * -1 #count credit owed as a liability
      else:
        balance = 0
      act = {
        'name': name,
        'type': type,
        'balance': balance,
        '_id': a['_id']
      }
      sub_accounts.append(act)
    total_balance = get_total(sub_accounts)
    account = {
      'access_token': access_token,
      'sub_accounts': sub_accounts,
      'total_balance': total_balance,
      'transactions': transactions
    }
  else: 
    account = None
  return account
