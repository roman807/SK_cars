#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 15:52:03 2018
@author: roman
"""
import requests
import urllib.request
import numpy as np
import cv2
from operator import itemgetter

url = 'https://spaceknow-kraken.appspot.com/kraken/grid/'
geometry_id = '/-/'

class Cars():
    def __init__(self, mapId, tiles):
        self.mapId = mapId
        self.tiles = tiles
        all_x = list(set([tile[1] for tile in tiles]))
        all_y = list(set([tile[2] for tile in tiles]))
        all_tiles = [[tiles[0][0], all_x[i], all_y[j]] for i in range(len(all_x)) 
            for j in range(len(all_y))]
        self.all_tiles = sorted(sorted(all_tiles, key=itemgetter(1)), 
            key=itemgetter(2))
        self.zero_image = self.zero_image()
        self.img_cars = self.car_masks()
        
    def count_cars(self):
        file_name = 'detections.geojson'
        n_cars = 0
        for tile in self.tiles:
            url_pic = url + self.mapId + geometry_id + str(tile[0]) + '/' \
                + str(tile[1]) + '/' + str(tile[2]) + '/' + file_name
            r = requests.get(url_pic)
            r_json = r.json()
            for feature in r_json['features']:
                if feature['properties']['class'] == 'cars':
                    n_cars += feature['properties']['count']
        return n_cars
    
    def zero_image(self):
        file_name = 'cars.png'
        url_pic = url + self.mapId + geometry_id + str(self.tiles[0][0]) + '/'\
            + str(self.tiles[0][1]) + '/' + str(self.tiles[0][2]) + '/'\
            + file_name
        r = urllib.request.urlopen(url_pic)
        image = np.asarray(bytearray(r.read()), dtype='uint8')
        return cv2.imdecode(image, cv2.IMREAD_COLOR) * 0
        
    def car_masks(self):
        file_name = 'cars.png'
        img_cars = []
        for tile in self.all_tiles:
            if tile not in self.tiles:
                img_cars.append(self.zero_image)
            else:
                url_pic = url + self.mapId + geometry_id + str(tile[0]) + '/'\
                    + str(tile[1]) + '/' + str(tile[2]) + '/' + file_name
                r = urllib.request.urlopen(url_pic)
                image = np.asarray(bytearray(r.read()), dtype='uint8')
                img_cars.append(cv2.imdecode(image, cv2.IMREAD_COLOR))
        return img_cars
    
    def combine_tiles(self):
        row_images = []
        for i in range(1, len(self.img_cars)):
            if self.all_tiles[i][2] == self.all_tiles[i-1][2]:
                self.img_cars[i] = np.concatenate([self.img_cars[i-1], 
                                                self.img_cars[i]], axis=1)
            else:
                row_images.append(self.img_cars[i-1])
        row_images.append(self.img_cars[-1])
        image_car = np.concatenate(row_images)
        bin_ = image_car !=0
        BLUE = 150
        image_car_blue = BLUE * bin_
        image_car_blue[:, :, 0] = 0
        image_car_blue[:, :, 1] = 0
        return image_car_blue

class TrueImage():
    def __init__(self, mapId, tiles):
        self.mapId = mapId
        self.tiles = tiles
        all_x = list(set([tile[1] for tile in tiles]))
        all_y = list(set([tile[2] for tile in tiles]))
        all_tiles = [[tiles[0][0], all_x[i], all_y[j]] for i in range(len(all_x)) 
            for j in range(len(all_y))]
        self.all_tiles = sorted(sorted(all_tiles, key=itemgetter(1)), 
            key=itemgetter(2))
        self.zero_image = self.zero_image()
        self.img_true = self.true_image()

    def zero_image(self):
        file_name = 'truecolor.png'
        url_pic = url + self.mapId + geometry_id + str(self.tiles[0][0]) + '/'\
            + str(self.tiles[0][1]) + '/' + str(self.tiles[0][2]) + '/'\
            + file_name
        r = urllib.request.urlopen(url_pic)
        image = np.asarray(bytearray(r.read()), dtype='uint8')
        return cv2.imdecode(image, cv2.IMREAD_COLOR) * 0
    
    def true_image(self):
        file_name = 'truecolor.png'
        img_true = []
        for tile in self.all_tiles:
            if tile not in self.tiles:
                img_true.append(self.zero_image)
            else:
                url_pic = url + self.mapId + geometry_id + str(tile[0]) + '/'\
                    + str(tile[1]) + '/' + str(tile[2]) + '/' + file_name
                r = urllib.request.urlopen(url_pic)
                image = np.asarray(bytearray(r.read()), dtype='uint8')
                img_true.append(cv2.imdecode(image, cv2.IMREAD_COLOR))
        return img_true
    
    def combine_tiles(self):
        row_images = []
        for i in range(1, len(self.img_true)):
            if self.all_tiles[i][2] == self.all_tiles[i-1][2]:
                self.img_true[i] = np.concatenate([self.img_true[i-1], 
                                                  self.img_true[i]], axis=1)
            else:
                row_images.append(self.img_true[i-1])
        row_images.append(self.img_true[-1])
        return np.concatenate(row_images)
        
def combine_pictures(mask_cars, true_image):
    BLUE = 150
    for i in range(true_image.shape[0]):
        for j in range(true_image.shape[1]):
            if mask_cars[i, j, 2] == BLUE:
                true_image[i, j, 0] = 0
                true_image[i, j, 1] = 0
                true_image[i, j, 2] = BLUE
    return true_image