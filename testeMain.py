# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:43:18 2024

@author: Usuario
"""
import numpy as np
import scenarioParameters as sn
import matplotlib.pyplot as plt
import scipy as sp
import appliance as app
import activeConsumer as ac
import time
import geoFind as gf
import Tariffs as tf
import math
#Teste


def setPUloads():
    l1 = app.TimeFlexLoad('Bomba booster', '07:00','08:00','17:00','00:20', 2.0, 1.0, 0.1)
    l2 = app.TimeFlexLoad('Bomba Piscina', '07:00','08:00','17:00','02:00', 0.75, 0.75, 0.1)
    l3 = app.TimeFlexLoad('Ferro de Passar', '14:00','15:00','17:00','02:00', 1.0, 0.2, 0.2)
    l4 = app.TimeFlexLoad('Máquina de lavar', '07:00','08:00','17:00','01:00', 0.3033, 0.7, 0.5);
    
    l5 = app.TimeFlexLoad('lâmpadas externas', '17:00','18:00','23:59','04:30', 0.3, 0.3, 0.3);
    l6 = app.TimeFlexLoad('lâmpadas internas', '17:00','18:00','23:59','04:30', 0.15, 0.15, 0.7);
    l7 = app.TimeFlexLoad('AC F1', '17:00','20:00','23:59','01:15', 1.3266, 1.7, 1);
    l8 = app.TimeFlexLoad('AC F2', '17:00','20:00','23:59','01:15', [2.066], [2.1], 1);
    l9 = app.TimeFlexLoad('AC 3', '17:00','19:50','23:59','04:00', 1.1520, 1.2, 1);
    l10 = app.TimeFlexLoad('AC 4', '17:00','20:00','23:59','00:45', 1.011, 1.1, 1);
    l11 = app.TimeFlexLoad('Lava-louças', '18:00','21:00','22:00','00:45', 0.77366, 1.76, 1);

    L=[l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11]
    return L
    

#Cenário Rodolfo
# l1 = app.TimeFlexLoad('L1', '06:35', '13:00', '23:05', '04:25', 0.440, 0.615, 1)
# l2 = app.TimeFlexLoad('L2', '03:25', '05:10', '23:50', '00:50', 2.7067, 2.9509, 1)
# l3 = app.TimeFlexLoad('L3', '07:15', '12:05', '19:05', '04:45', 0.4603, 0.5510, 1)

L = setPUloads()
gF = gf.GeoFind()

tariff = tf.Tariffs(0.58878, 0.48771, 0.80221, 1.26812) 

def sampleTotime(s):
    hour = math.trunc(s/sn.one_hour_in_samples)
    minuts = (s - (hour*sn.one_hour_in_samples))*sn.sampleInterval
    
    return "%02d:%02d" % (hour, minuts)

solution = gF.bestGeoFindVector(L, tariff)

for s in solution:
    print(sampleTotime(s))