#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 18:20:45 2018

@author: roman
"""

import time
import requests
import json

url = 'https://spaceknow-tasking.appspot.com/'

class Wait():
    def __init__(self, headers, pipelineId):
        self.headers = headers
        self.pipelineId = pipelineId
        self.status = None

    def get_pipeline_status(self):
        get_status = 'tasking/get-status'
        payload = {'pipelineId': self.pipelineId}
        r_status = requests.post(url + get_status, data=json.dumps(payload), headers=self.headers)
        r_status_json = r_status.json()
        self.status = r_status_json['status']
        print(self.status)
                                                                                                                                                                                                                                                                       
    def wait_until_resolved(self, timeout=100, period=5):
        must_end = time.time() + timeout
        while time.time() < must_end:
            self.get_pipeline_status()
            if self.status == 'RESOLVED':
                return True
            print('still waiting')
            time.sleep(period)
        return False



   # def get_pipeline_status(self):
#get_status = 'tasking/get-status'
#payload = {'pipelineId': 'PJNe4ntnqp389gW9zWNg'}
#r_status = requests.post(url + get_status, data=json.dumps(payload), headers=headers)
#r_status_json = r_status.json()
#r_status_json['status']