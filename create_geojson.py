#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 09:49:44 2018
@author: roman
"""
import geojson

def create_geojson(file_name, geometry, type_="Polygon"):
    extent = {"type": "GeometryCollection",
              "geometries": [{"type": type_,"coordinates": [geometry]}]}
    with open(file_name, 'a') as f:
        geojson.dump(extent, f)

geometry = [[153.1035,-27.392545],
            [153.10541,-27.3934],
            [153.10687,-27.3908],
            [153.10517,-27.389906],
            [153.1035,-27.392545]]
file_name = 'brisbane_staff_parking.geojson'
create_geojson(file_name, geometry)