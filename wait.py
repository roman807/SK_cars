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
    def __init__(self, headers, pipelineId, timeout):
        self.headers = headers
        self.pipelineId = pipelineId
        self.timeout = timeout
        self.status = None
        self.wait_until_resolved()

    def get_pipeline_status(self):
        get_status = 'tasking/get-status'
        payload = {'pipelineId': self.pipelineId}
        r_status = requests.post(url + get_status, data=json.dumps(payload), 
            headers=self.headers)
        r_status_json = r_status.json()
        self.status = r_status_json['status']
                                                                                                                                                                                                                                                                       
    def wait_until_resolved(self, period=5):
        must_end = time.time() + self.timeout
        while time.time() < must_end:
            self.get_pipeline_status()
            if self.status == 'RESOLVED':
                return True
            print('processing ...')
            time.sleep(period)
        print('skip scene (could not resolve pipeline within ' + str(self.timeout) 
            + ' seconds)')
        return False