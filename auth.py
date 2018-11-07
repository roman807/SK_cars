#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 10:00:12 2018
@author: roman
"""
import requests
import time
import json
from os import path

url = 'https://spaceknow.auth0.com/oauth/ro'

class Authentication():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        if path.isfile('jwt_token.json'):
            with open('jwt_token.json') as f:
                jwt_token_old = json.load(f)
            if jwt_token_old['time'] + 3600 * 10 > time.time():
                self.id_token = jwt_token_old['id_token']
            else:
                self.get_jwt()
        else:
            self.get_jwt()
            
    def get_jwt(self):
        data = {"client_id": "hmWJcfhRouDOaJK2L8asREMlMrv3jFE1",
                "username": self.username,
                "password": self.password,
                "connection": "Username-Password-Authentication",
                "grant_type": "password",
                "scope": "openid"}
        r = requests.post(url, data=data)
        self.id_token = r.json()['id_token']
        time_ = time.time()
        jwt_token = {'id_token': self.id_token, 'time': time_}
        with open('jwt_token.json', 'a') as f:
            json.dump(jwt_token, f)
            
    def get_headers(self):
        headers = {'Content-Type': 'application/json',\
               'Authorization': 'Bearer ' + self.id_token}
        return headers