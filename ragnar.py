#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 10:13:58 2018
@author: roman
"""
import requests
import json

url = 'https://spaceknow-imagery.appspot.com'

class SearchImagery():
    def __init__(self, headers, extent, startDatetime, endDatetime):
        self.headers = headers
        self.startDatetime =  startDatetime
        self.endDatetime = endDatetime
        self.extent = extent
        self.pipelineId = None
        self.results = None
        self.sceneIds = None

    def init_image(self):
        initiate = '/imagery/search/initiate'
        payload = {'provider': 'gbdx', 
                   'dataset': 'idaho-pansharpened', 
                   'startDatetime': self.startDatetime,
                   'endDatetime': self.endDatetime,
                   'extent': self.extent}
        r_init = requests.post(url + initiate, data=json.dumps(payload), 
                               headers=self.headers)
        r_init_json = r_init.json()
        self.pipelineId = r_init_json['pipelineId']
        
    def ret_image(self):
        payload_ret = {'pipelineId': self.pipelineId}
        retrieve = '/imagery/search/retrieve'
        r_ret = requests.post(url + retrieve, data=json.dumps(payload_ret), 
                              headers=self.headers)
        r_ret_json = r_ret.json()
        self.results = r_ret_json['results']
        self.sceneIds = [self.results[i]['sceneId'] for i in 
                         range(len(self.results)) 
            if self.results[i]['bands'][0]['gsd'] < 0.55]
        return self.sceneIds

class GetImagery():
    def __init__(self, headers, extent, sceneId):
        self.headers = headers
        self.extent = extent
        self.sceneId = sceneId
        self.pipelineId = None
        self.url = None
        self.meta = None

    def init_image(self):
        initiate = '/imagery/get-image/initiate'
        payload = {'sceneId': self.sceneId, 
                   'extent': self.extent}
        r_init = requests.post(url + initiate, data=json.dumps(payload), 
                               headers=self.headers)
        r_init_json = r_init.json()
        self.pipelineId = r_init_json['pipelineId']

    def ret_image(self):
        payload_ret = {'pipelineId': self.pipelineId}
        retrieve = '/imagery/get-image/retrieve'
        r_ret = requests.post(url + retrieve, data=json.dumps(payload_ret), 
                              headers=self.headers)
        r_ret_json = r_ret.json()
        self.url = r_ret_json['url']
        self.meta = r_ret_json['meta']
        return self.url, self.meta    