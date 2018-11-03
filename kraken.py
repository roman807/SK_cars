#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 10:31:11 2018

@author: roman
"""

import requests
import json
import geojson

url = 'https://spaceknow-kraken.appspot.com'
map_type = 'cars'

class Analyses():
    def __init__(self, headers, sceneId, map_type, extent):
        self.headers = headers
        self.sceneId = sceneId
        self.map_type = map_type
        self.extent = extent
        self.pipelineId = None
        self.mapId = None
        self.tiles = None

    def init_image(self):
        initiate = '/kraken/release/' + self.map_type + '/geojson/initiate'
        payload = {'sceneId': self.sceneId, 'extent': self.extent}
        r_kraken = requests.post(url + initiate, data=json.dumps(payload), headers=self.headers)
        r_kraken_json = r_kraken.json()
        self.pipelineId = r_kraken_json['pipelineId']
        
    def ret_image(self):
        retrieve = '/kraken/release/' + map_type + '/geojson/retrieve'
        payload_ret = {'pipelineId': self.pipelineId}
        r_kraken_ret = requests.post(url + retrieve, data=json.dumps(payload_ret), headers=self.headers)
        r_kraken_ret_json = r_kraken_ret.json()
        self.mapId = r_kraken_ret_json['mapId']
        self.maxZoom = r_kraken_ret_json['maxZoom']
        self.tiles = r_kraken_ret_json['tiles']
        return self.mapId, self.maxZoom, self.tiles