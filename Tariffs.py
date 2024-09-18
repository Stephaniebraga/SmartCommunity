# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:12:15 2024

@author: Usuario
"""
import numpy as np

class Tariffs:
    
    def __init__(self, constTarValue, offPeakTarValue, intTarValue, peakTarValue):
        self.constTarValue = constTarValue
        self.offPeakTarValue = offPeakTarValue
        self.intTarValue = intTarValue
        self.peakTarValue = peakTarValue
        
    def tarifaBranca(self):
        return np.array([self.offPeakTarValue, self.intTarValue, self.peakTarValue])
    
    def getTarifaBrancaVector(self, sampleInterval):
        nSamples = int(60*24 / sampleInterval)
        tbVector = np.ones(nSamples)*self.offPeakTarValue
        
        one_hour_in_samples = (60/sampleInterval)
        
        # define os postos da Tarifa Branca
        Ti_start = 16.5*one_hour_in_samples #16:30 (Início do período intermediário)
        Ti_finish = 21.5*one_hour_in_samples #21:30 (Início do período intermediário)
        
        Tp_start = 17.5*one_hour_in_samples #17:30 (Início do período de pico)
        Tp_finish = 20.5*one_hour_in_samples #20:30 (Início do período de pico)

        tbVector[int(Ti_start):int(Ti_finish)] = np.ones(int(Ti_finish - Ti_start))*self.intTarValue
        tbVector[int(Tp_start):int(Tp_finish)] = np.ones(int(Tp_finish - Tp_start))*self.peakTarValue

        return tbVector
    
    def tarifaConstante(self):
        return self.constTarValue
        
  