#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 09:44:37 2018

@author: roman
"""
import os
os.chdir('/home/roman/Documents/Projects/SpaceKnow')
from save_geojson3 import *
from auth import *
from ragnar5 import SearchImagery, GetImagery
from kraken3 import Analyses
from wait_until_processed5 import Wait
import requests
import matplotlib.pyplot as plt
import cv2
import urllib.request
import numpy as np
from operator import itemgetter

#import importlib
#importlib.reload(kraken2)
#from kraken2 import Analyses

# ----- create single geometry ----- #
geometry = [[153.1045,-27.392],
            [153.1051,-27.3925],
            [153.1055,-27.3915],
            [153.1049,-27.391],
            [153.1045,-27.392]]
extent = create_geojson(geometry)

# ----- Authentication ----- #
username = 'roman.moser@gmx.net'
password = '#########'
headers = get_jwt(username, password)

# ----- search imagery with rangar ----- #
search_ragnar = SearchImagery(headers, extent)
search_ragnar.init_image()
resolve_pipeline = Wait(headers, search_ragnar.pipelineId) #################
resolve_pipeline.wait_until_resolved()
sceneIds = search_ragnar.ret_image()
sceneId = sceneIds[2]

# ----- get imagery with rangar ----- #
get_ragnar = GetImagery(headers, extent, sceneId)
get_ragnar.init_image()
resolve_pipeline = Wait(headers, get_ragnar.pipelineId) #################
resolve_pipeline.wait_until_resolved()
url, meta = get_ragnar.ret_image()

# ----- analyse scene for cars with kraken ----- #
map_type = 'cars'
kraken = Analyses(headers, sceneId, map_type, extent)
kraken.init_image()
resolve_pipeline = Wait(headers, kraken.pipelineId) #################
resolve_pipeline.wait_until_resolved()
map_id, max_zoom, tiles = kraken.ret_image()
tiles = sorted(sorted(tiles, key=itemgetter(1)), key=itemgetter(2))

url_d = 'https://spaceknow-kraken.appspot.com/kraken/grid/'
#<map_id>/<geometry_id>/<z>/<x>/<y>/<file_name>
geometry_id = '/-/'
z = [tile[0] for tile in tiles] 
x = [tile[1] for tile in tiles] 
y = [tile[2] for tile in tiles] 
# -----  count cars ----- #
file_name = 'detections.geojson'
n_cars = 0
for z_, x_, y_ in zip(z, x, y):
    url_pic = url_d + map_id + geometry_id + str(z_) + '/' + str(x_) + '/'\
        + str(y_) + '/' + file_name
    r = requests.get(url_pic)
    r_json = r.json()
    for feature in r_json['features']:
        if feature['properties']['class'] == 'cars':
            n_cars += feature['properties']['count']

# -----  masks for cars ----- #
file_name = 'cars.png'
img_cars = []
for z_, x_, y_ in zip(z, x, y):
    url = url_d + map_id + geometry_id + str(z_) + '/' + str(x_) + '/'\
        + str(y_) + '/' + file_name
    r = urllib.request.urlopen(url)
    image = np.asarray(bytearray(r.read()), dtype='uint8')
    img_cars.append(cv2.imdecode(image, cv2.IMREAD_COLOR))


#a=[[3,4],[2,1],[1,5],[7,8]]
#b=[1,2,3,4]
#
#[x for _,x in sorted(zip(a,b))]
#zip(a,b).sort(key=lambda x: (x[1],_))


# ----------- combine tiles ----------- #
row_images = []
for i in range(1, len(img_cars)):
    if y[i] == y[i-1]:
        img_cars[i] = np.concatenate([img_cars[i-1], img_cars[i]], axis=1)
    else:
        row_images.append(img_cars[i-1])
row_images.append(img_cars[-1])

image_car = np.concatenate(row_images)
plt.imshow(image_car)

bin_ = image_car !=0
blue = 150 * bin_
blue[:, :, 0] = 0
blue[:, :, 1] = 0
plt.imshow(blue)
plt.imshow(blue*0)

# ----- analyse scene for everything with kraken ----- #
map_type = 'imagery'
kraken = Analyses(headers, sceneId, map_type, extent)
kraken.init_image()
resolve_pipeline = Wait(headers, kraken.pipelineId)
resolve_pipeline.wait_until_resolved()
map_id, zoom, tiles = kraken.ret_image()

# -----  masks for truecolor ----- #
file_name = 'truecolor.png'
img_true = []
for z_, x_, y_ in zip(z, x, y):
    url = url_d + map_id + geometry_id + str(z_) + '/' + str(x_) + '/'\
        + str(y_) + '/' + file_name
    r = urllib.request.urlopen(url)
    image = np.asarray(bytearray(r.read()), dtype="uint8")
    img_true.append(cv2.imdecode(image, cv2.IMREAD_COLOR))

row_images = []
for i in range(1, len(img_true)):
    if y[i] == y[i-1]:
        img_true[i] = np.concatenate([img_true[i-1], img_true[i]], axis=1)
    else:
        row_images.append(img_true[i-1])
row_images.append(img_true[-1])
image_true = np.concatenate(row_images)

from pylab import rcParams
rcParams['figure.figsize'] = 6, 6
plt.imshow(image_true + blue)




# parking lot: 
geometry = [[153.1035,-27.392545],
            [153.10541,-27.3934],
            [153.10687,-27.3908],
            [153.10517,-27.389906],
            [153.1035,-27.392545]]
# 3 tiles:
geometry = [[153.1045,-27.392],
            [153.1051,-27.3925],
            [153.1055,-27.3915],
            [153.1049,-27.391],
            [153.1045,-27.392]]


geometry = [[153.11, -27.38],
            [153.12, -27.38],
            [153.12, -27.37],
            [153.11, -27.37],
            [153.11, -27.38]]

geometry = [[153.118, -27.383],
            [153.12, -27.383],
            [153.12, -27.38],
            [153.118, -27.38],
            [153.118, -27.383]]

