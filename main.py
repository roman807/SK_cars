#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 09:44:37 2018

@author: roman
"""
import os
os.chdir('/home/roman/Documents/Projects/SpaceKnow')
import matplotlib.pyplot as plt
import geojson
import json
from PIL import Image
from auth import Authentication
from ragnar import SearchImagery, GetImagery
from kraken import Analyses
from wait_until_processed import Wait
from grid_files import Cars, TrueImage, combine_pictures

import importlib
import wait_until_processed
importlib.reload(wait_until_processed)

# ----- load inputs ----- #
with open('inputs.json') as f:
    inputs = json.load(f)

# ----- load single geometry ----- #
geometry_geojson = inputs['geometry_geojson']
with open(geometry_geojson) as f:
    extent = geojson.load(f)

# ----- Authentication ----- #
print('authentication - get JWT')
username = inputs['username']
password = inputs['password']
authorize = Authentication(username, password)
headers = authorize.get_headers()

# ----- search imagery with rangar ----- #
print('search imagery (ragnar)')
startDatetime = inputs['startDatetime']
endDatetime = inputs['endDatetime']
search_ragnar = SearchImagery(headers, extent, startDatetime, endDatetime)
search_ragnar.init_image()
resolve_pipeline = Wait(headers, search_ragnar.pipelineId, timeout=100)
sceneIds = search_ragnar.ret_image()
sceneIds = sceneIds[:min(len(sceneIds), inputs['max_pictures'])]

n_cars_all = []
images_all = []
date_times = []
i = 1
for sceneId in sceneIds:
# ----- get imagery with rangar ----- #
    print('-----------------------------------')
    print('Process scene no. ' + str(i))
    print('-----------------------------------')
    print('get imagery (ragnar)')
    get_ragnar = GetImagery(headers, extent, sceneId)
    get_ragnar.init_image()
    resolve_pipeline = Wait(headers, get_ragnar.pipelineId, inputs['timeout'])
    if resolve_pipeline.status == 'PROCESSING':
        continue
    url, meta = get_ragnar.ret_image()
    
    # ----- analyse scene for cars with kraken ----- #
    print('analyze scene for cars (kraken)')
    map_type = 'cars'
    kraken = Analyses(headers, sceneId, map_type, extent)
    kraken.init_image()
    resolve_pipeline = Wait(headers, kraken.pipelineId, inputs['timeout'])
    if resolve_pipeline.status == 'PROCESSING':
        continue
    map_id, max_zoom, tiles = kraken.ret_image()
    cars = Cars(map_id, tiles)
    n_cars = cars.count_cars()
    mask_cars = cars.combine_tiles()
    
    # ----- analyse scene for everything with kraken ----- #
    print('analyze imagery (kraken)')
    map_type = 'imagery'
    kraken = Analyses(headers, sceneId, map_type, extent)
    kraken.init_image()
    resolve_pipeline = Wait(headers, kraken.pipelineId, inputs['timeout'])
    if resolve_pipeline.status == 'PROCESSING':
        continue
    map_id, zoom, tiles = kraken.ret_image()
    background = TrueImage(map_id, tiles)
    true_image = background.combine_tiles()    
    combined_picture = combine_pictures(mask_cars, true_image)    
    n_cars_all.append(n_cars)
    images_all.append(combined_picture)
    date_times.append(meta['datetime'])
    i += 1

for image, date_time, n_cars in zip(images_all, date_times, n_cars_all):
    file_name = 'scene_' + date_time
    im = Image.fromarray(image)
    im.save("{}.png".format(file_name))
    plt.imshow(image)
    plt.show()
    print('Number of cars on ' + date_time + ': ' + str(n_cars))

