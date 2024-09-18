# -*- coding: utf-8 -*-

import time
import numpy as np
import scenarioParameters as sn
import math

class Appliance:
    """
    Classe que representa um appliance de um consumidor ativo
    
    Attributes
    ----------
    name: str
        nome do appliance
    minTime: time
        limite mínimo para funcionamento do app
    expectedTime: time 
        melhor instante para funcionamento do app
    maxTime: time
        limite máximo para funcionamento do app
    duration: duration
        duração do funcionamento do app
    avgPower: float
        valor da potência média do app
    peakPower: float
        valor da potência de pico do app
    comfortLevel: float
        nível de relevãncia para o conforto 

    Methods
    -------
    getTimeInSamples(t)
        Retorna a amostra equivalente ao instante t
    
    fillPowerInSamples(self)
        Calcula o valor discreto dos atributos do app
    
    cal
    """
        
    def __init__(self, name, minTime, expectedTime, maxTime, duration, avgPower, peakPower, comfortLevel):
        self.name = name
        self.minTime = minTime # r-Release Time
        self.expectedTime = expectedTime #e-Expectec Time
        self.maxTime = maxTime # d-Deadline
        self.duration = duration #C-width of the i-th load
        self.avgPower = avgPower #average power
        self.peakPower = peakPower #peak power
        self.comfortLevel = comfortLevel #$μ_i relevance of the i th load, ∈ [ 0, 1 ]
        
        self.fillPowerInSamples()        
        self.solutionTimeInSamples = self.expectedTimeInSamples
        
    def getTimeInSamples(self, T):
        t = time.strptime(T, "%H:%M")
        hour = t.tm_hour
        minuts = t.tm_min
        
        return hour*sn.one_hour_in_samples + math.floor(minuts/sn.sampleInterval)
    
    def calcAvgPowerProfile(self, ts):
        avgPowerProfile = np.zeros(int(sn.n_samples))
        
        lmin= int(ts)
        lmax= int(ts + self.durationInSamples)
        avgPowerProfile[lmin:lmax] = self.avgPowerInSamples 
        return avgPowerProfile
        
    def fillPowerInSamples(self):
        
        # Amostra associada ao tempo minimo de inicio da carga
        self.minTimeInSamples = self.getTimeInSamples(self.minTime)

        # Amostra associada ao tempo máximo de término
        self.maxTimeInSamples = self.getTimeInSamples(self.maxTime)
        
        # Amostra associada ao tempo ideal de inicio da carga
        self.expectedTimeInSamples = self.getTimeInSamples(self.expectedTime)  
        
        # Duração total da carga em numero de amostras
        self.durationInSamples = self.getTimeInSamples(self.duration) 
        
        s = int(self.minTimeInSamples)
        f = int(self.maxTimeInSamples - self.durationInSamples) + 1
        self.startTimeInSamples = range(s,f)
        
        #self.finishTimeInSamples = self.startTimeInSamples + self.durationInSamples

        AVG = np.ones((int(self.durationInSamples)))*self.avgPower
        PEAK = np.ones((int(self.durationInSamples)))*self.peakPower
        
        self.peakPowerInSamples = PEAK
        self.avgPowerInSamples =  AVG
        
            
class TimeFlexLoad(Appliance):
    def __init__(self, name, minTime, expectedTime, maxTime, duration, avgPower, peakPower, comfortLevel):
        Appliance.__init__(self, name, minTime, expectedTime, maxTime, duration, avgPower, peakPower, comfortLevel)
        
class PowerFlexLoad(Appliance):
    def __init__(self, name, minTime, expectedTime, maxTime, duration, avgPower, peakPower, comfortLevel, minPower, maxPower):
        super(Appliance, self).__init__(name, minTime, expectedTime, maxTime, duration, avgPower, peakPower, comfortLevel)
        self.minPower = minPower
        self.maxPower = maxPower
        
