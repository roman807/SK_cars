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
from ragnar import SearchImagery, GetImagery
from kraken import Analyses
from wait_until_processed import Wait
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
geometry = [[153.1035,-27.392545],
            [153.10541,-27.3934],
            [153.10687,-27.3908],
            [153.10517,-27.389906],
            [153.1035,-27.392545]]
extent = create_geojson(geometry)

# ----- Authentication ----- #
#username = 'roman.moser@gmx.net'
#password = '.q1851319'
#print('Authorization - get JWT')
headers = get_jwt(username, password)

# ----- search imagery with rangar ----- #
print('Search imagery (ragnar)')
search_ragnar = SearchImagery(headers, extent)
search_ragnar.init_image()
resolve_pipeline = Wait(headers, search_ragnar.pipelineId) #################
resolve_pipeline.wait_until_resolved()
sceneIds = search_ragnar.ret_image()
sceneId = sceneIds[2]

# ----- get imagery with rangar ----- #
print('Get imagery (ragnar)')
get_ragnar = GetImagery(headers, extent, sceneId)
get_ragnar.init_image()
resolve_pipeline = Wait(headers, get_ragnar.pipelineId) #################
resolve_pipeline.wait_until_resolved()
url, meta = get_ragnar.ret_image()

# ----- analyse scene for cars with kraken ----- #
print('Analyze scene for cars (kraken)')
map_type = 'cars'
kraken = Analyses(headers, sceneId, map_type, extent)
kraken.init_image()
resolve_pipeline = Wait(headers, kraken.pipelineId) #################
resolve_pipeline.wait_until_resolved()
map_id, max_zoom, tiles = kraken.ret_image()

url_d = 'https://spaceknow-kraken.appspot.com/kraken/grid/'
geometry_id = '/-/'
# -----  count cars ----- #
print('Count cars')
file_name = 'detections.geojson'
n_cars = 0
for tile in tiles:
    url_pic = url_d + map_id + geometry_id + str(tile[0]) + '/' + str(tile[1]) + '/'\
        + str(tile[2]) + '/' + file_name
    r = requests.get(url_pic)
    r_json = r.json()
    for feature in r_json['features']:
        if feature['properties']['class'] == 'cars':
            n_cars += feature['properties']['count']
            
# -------- zero image get one picture:
file_name = 'cars.png'
print('create zero image')
url = url_d + map_id + geometry_id + str(tiles[0][0]) + '/' + str(tiles[0][1]) + '/'\
    + str(tiles[0][2]) + '/' + file_name
r = urllib.request.urlopen(url)
image = np.asarray(bytearray(r.read()), dtype='uint8')
image_zero = cv2.imdecode(image, cv2.IMREAD_COLOR) * 0

all_x = list(set([tile[1] for tile in tiles]))
all_y = list(set([tile[2] for tile in tiles]))
all_tiles = [[tiles[0][0], all_x[i], all_y[j]] for i in range(len(all_x)) for j in range(len(all_y))]
all_tiles = sorted(sorted(all_tiles, key=itemgetter(1)), key=itemgetter(2))

# -----  masks for cars ----- #
print('create mask for cars')
file_name = 'cars.png'
img_cars = []
for tile in all_tiles:
    if tile not in tiles:
        img_cars.append(image_zero)
    else:
        url = url_d + map_id + geometry_id + str(tile[0]) + '/' + str(tile[1]) + '/'\
            + str(tile[2]) + '/' + file_name
        r = urllib.request.urlopen(url)
        image = np.asarray(bytearray(r.read()), dtype='uint8')
        img_cars.append(cv2.imdecode(image, cv2.IMREAD_COLOR))


# ----------- combine tiles ----------- #
row_images = []
print('combine tiles for car masks')
for i in range(1, len(img_cars)):
    if all_tiles[i][2] == all_tiles[i-1][2]:
        img_cars[i] = np.concatenate([img_cars[i-1], img_cars[i]], axis=1)
    else:
        row_images.append(img_cars[i-1])
row_images.append(img_cars[-1])
image_car = np.concatenate(row_images)

bin_ = image_car !=0
BLUE = 150
image_car_blue = BLUE * bin_
image_car_blue[:, :, 0] = 0
image_car_blue[:, :, 1] = 0
#plt.imshow(blue)
#plt.imshow(blue*0)

# ----- analyse scene for everything with kraken ----- #
print('analyze imagery with kraken')
map_type = 'imagery'
kraken = Analyses(headers, sceneId, map_type, extent)
kraken.init_image()
resolve_pipeline = Wait(headers, kraken.pipelineId)
resolve_pipeline.wait_until_resolved()
map_id, zoom, tiles = kraken.ret_image()

# -----  masks for truecolor ----- #
print('create background pictures')
file_name = 'truecolor.png'
img_true = []
for tile in all_tiles:
    if tile not in tiles:
        img_true.append(image_zero)
    else:
        url = url_d + map_id + geometry_id + str(tile[0]) + '/' + str(tile[1]) + '/'\
            + str(tile[2]) + '/' + file_name
        r = urllib.request.urlopen(url)
        image = np.asarray(bytearray(r.read()), dtype='uint8')
        img_true.append(cv2.imdecode(image, cv2.IMREAD_COLOR))

from pylab import rcParams
rcParams['figure.figsize'] = 10, 10

row_images = []
for i in range(1, len(img_true)):
    if all_tiles[i][2] == all_tiles[i-1][2]:
        img_true[i] = np.concatenate([img_true[i-1], img_true[i]], axis=1)
    else:
        row_images.append(img_true[i-1])
row_images.append(img_true[-1])
image_true = np.concatenate(row_images)

for i in range(image_true.shape[0]):
    for j in range(image_true.shape[1]):
        if image_car_blue[i, j, 2] == BLUE:
            image_true [i, j, 0] = 0
            image_true [i, j, 1] = 0
            image_true [i, j, 2] = BLUE
#image_car_blue.shape

plt.imshow(image_true)# + image_car_blue)
print('number of cars: ' + str(n_cars))






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

