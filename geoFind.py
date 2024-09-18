# -*- coding: utf-8 -*-
import numpy as np
import scenarioParameters as sn
import Tariffs as tf
import math

class GeoFind:
    """
    Classe para o algoritmo GeoFind
    
    Attributes
    ----------
    
    Methods
    -------
   
    """
    def __init__(self, activeConsumer):
        self.activeConsumer = activeConsumer
        
    def bestGeoFindVector(self, H, tariff):
        sizeH = int(np.size(H))
        t = np.zeros(sizeH)
        
        for i in range(sizeH):
            t[i] = self.bestGeoFind(H[i], tariff) 
    	
        return t
    
    def bestGeoFind(self, l, tariff):
        
        #Set tariffSpace
        Pe = self.decomposeTime(l, l.expectedTimeInSamples)
        
        if(Pe[0] == l.durationInSamples): #completamente fora pico
            return l.expectedTimeInSamples
        
        A = self.geoFind(l, tariff)
        
        t = self.recomposeTime(l, A)
        
        endLimit = int(len(l.startTimeInSamples) - 1)
        if ((l.startTimeInSamples[0] <= t) and (t <= l.startTimeInSamples[endLimit]) ):
            return t
        
        C1 = self.evalBasicLoadComfort(l, l.startTimeInSamples[0])/self.evalBasicLoadCost(l, l.startTimeInSamples[0])
        Ce = self.evalBasicLoadComfort(l, l.expectedTimeInSamples)/self.evalBasicLoadCost(l, l.expectedTimeInSamples)
        Cend =self.evalBasicLoadComfort(l, l.startTimeInSamples[0])/self.evalBasicLoadCost(l, l.startTimeInSamples[endLimit])
        
        if C1>=Cend:
            val = C1
            tempo = l.startTimeInSamples[0]
        else:
            val = Cend
            tempo = l.startTimeInSamples[endLimit]
            
        return l.expectedTimeInSamples if Ce >= val else tempo
   
    def decomposeTime(self, l, s):
        # define _finish time
        #s = l.expectedTimeInSamples
        f = s + l.durationInSamples
               
        # define os postos da Tarifa Branca
        Ti_start = 16.5*sn.one_hour_in_samples #16:30 (Início do período intermediário)
        Ti_finish = 21.5*sn.one_hour_in_samples #21:30 (Início do período intermediário)
        
        Tp_start = 17.5*sn.one_hour_in_samples #17:30 (Início do período de pico)
        Tp_finish = 20.5*sn.one_hour_in_samples #20:30 (Início do período de pico)
    
        #vf = Componente Fora pico
        vf = 0
        if s >= Ti_finish or f <= Ti_start:
            vf = l.durationInSamples #completamente no fora pico
        
        if s < Ti_start and f > Ti_start :
            vf += Ti_start - s #uma parte fora pico e outra no intermediário
        
        if s < Ti_finish and f > Ti_finish:
            vf += f - Ti_finish #uma parte fora pico e outra no intermediário
            
        #vp = Componente Pico
        vp = 0
        if (s>= Tp_start and f <= Tp_finish):
            vp = l.durationInSamples #completamente no pico
        elif (s <= Tp_start and f >= Tp_start):
            vp = min(f,Tp_finish) - Tp_start #uma parte no intermediario e outra no pico
        elif (s <= Tp_finish and f >= Tp_finish):
            vp = Tp_finish - max(s,Tp_start) #uma parte no pico e outra no intermediario
    
        
        #vi = Componente intermediário
        vi = 0
        if (s >= Ti_start and f <= Tp_start) or (s >= Tp_finish and f <= Ti_finish):
            vi = l.durationInSamples #completamente no intermediário
        else:
            if (s <= Ti_start and f >= Ti_start):
                vi += min(f,Tp_start) - Ti_start #uma parte fora pico e outra no intermediário
            elif (s <= Tp_start and f >= Tp_start):
                vi += Tp_start - max(s,Ti_start) #uma parte no intermediario e outra no pico
            
            if (s <= Tp_finish and f >= Tp_finish):
                vi += min(f,Ti_finish) - Tp_finish #uma parte no pico e outra no intermediário
            elif (s <= Ti_finish and f >= Ti_finish):
                vi += Ti_finish - max(s,Tp_finish) #uma parte no intermediário e outra fora pico
        
        
        return np.array([vf,vi,vp])
        
        
    def geoFind(self, l, tariff):
        D = l.durationInSamples
        
        if (D <= 1):
            return np.array([D,0,0])
        
        # md" Define discrete quantity 1H related to Δt (taxa de amostragem)"
        k = sn.one_hour_in_samples
     
        # md" Load point (feasible) in which it has only intermediate and off peak post components"
        bi = math.floor(D*(tariff.constTarValue - tariff.offPeakTarValue)/(tariff.intTarValue - tariff.offPeakTarValue))
        bf = D - bi
        
        # md" Fist bes point"
        pBest1 = np.array([bf, bi, 0.0])
        
        if (D <= k):
            return pBest1
     
        # md" Load point (not feasible) in which it has only peak and off peak post components"
        ap = math.floor(D*(tariff.constTarValue - tariff.offPeakTarValue)/(tariff.peakTarValue - tariff.offPeakTarValue))
                
        p_b2 = (ap-(k*(ap/bi)))
        p_b2r = math.floor(p_b2)
        f_b2 = D - k - p_b2r #(af+(k*((bf-af)/bi)))
        pBest2 = np.array([f_b2, k, p_b2r])
        
        return pBest2 if p_b2 >= 0.0 else pBest1
     
            
    def recomposeTime(self, l, P):
        e = l.expectedTimeInSamples
        
        # define os postos da Tarifa Branca
        Ti_start = 16.5*sn.one_hour_in_samples #16:30 (Início do período intermediário)
        Ti_finish = 21.5*sn.one_hour_in_samples #21:30 (Início do período intermediário)
            
        if abs(Ti_start - e) <= abs(Ti_finish - e):
            return (Ti_start - P[0])
        else:
            # d2 = (P[1]/k) + (P[2]/k)
            # h2 = int(math.floor(math.trunc(d2,1)))
            # m2 = int(math.floor((d2%1)*60))
            return ( Ti_finish - (P[1] + P[2]) )
    
    def evalBasicLoadComfort(self, l, s, op="frac"):

        if s < l.minTimeInSamples or s > l.maxTimeInSamples:
           # @error "Start instant should be between release and dead line"
            return 0
        elif l.expectedTimeInSamples < l.minTimeInSamples or l.expectedTimeInSamples > l.maxTimeInSamples :
            #@error "Expected instant should be between release and dead line"
            return 0
        
        
        DMAX = max(abs(l.minTimeInSamples - l.expectedTimeInSamples), abs(l.maxTimeInSamples - l.expectedTimeInSamples))
        DISC = DMAX - abs(s - l.expectedTimeInSamples)
        
        if op == "frac":
            return DISC / DMAX
        elif op == "num":
  #          return Dates.value(DISC) / 1e9
            return DISC/1e9
        elif op == "den":
 #           return Dates.value(DMAX) / 1e9
            return DMAX/1e9
        else:
            #@error "Invalid parameter op [\"frac\" \"num\" \"dem\"]"
            return 0
        
    def evalBasicLoadCost(self, l, s, TB=np.array([0.48771, 0.80221, 1.26812]), TC=0.58878, OP="Norm"):
        P = self.decomposeTime(l, s)
        En = [P[0], P[1], P[2]]
        
        k = sn.one_hour_in_samples
    
        CustoBranca = k * l.avgPower * sum(TB * En)
        CustoComum = k * l.durationInSamples * l.avgPower * TC
        CustoMinimo = k * l.durationInSamples * l.avgPower * TB[0]
        
        #self.activeConsumer.calc
        
    
        if OP == "Norm":
            return (CustoBranca) / CustoComum
        elif OP == "Branca":
            return CustoBranca
        elif OP == "Comum":
            return CustoComum
        elif OP == "Min":
            return CustoMinimo
        else:
            #@error "Invalid parameter OP=[\"Norm\" \"Branca\" \"Comum\" \"Min\"]"
            return 0
        
    
    


