#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 10:00:12 2018

@author: roman
"""

import requests

def get_jwt(username, password):
    url = 'https://spaceknow.auth0.com/oauth/ro'
    data = {"client_id": "hmWJcfhRouDOaJK2L8asREMlMrv3jFE1",
            "username": username,
            "password": password,
            "connection": "Username-Password-Authentication",
            "grant_type": "password",
            "scope": "openid"}
    r = requests.post(url, data=data)
    id_token = r.json()['id_token']
    headers = {'Content-Type': 'application/json',\
           'Authorization': 'Bearer ' + id_token}
    return headers
