# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 14:47:26 2024

@author: Stephanie Braga
"""
import numpy as np
import appliance as app
import activeConsumer as ac
import Tariffs as tf
import math
from random import randrange

"""
    Módulo para configurar os parâmetros do cenário de simulação
...
"""

n_actConsumers = 10 #Número de consumidores ativos
n_pasConsumers = 20 #Número de consumidores passivos
lambda_= 0 #overprice p/ violação de restrição compartilhada de limite de demanda
passiveDemand = 1117 #(kwh) Demanda dos consumidores passivos

minAggPower = 35 #(kw) limite mínimo de demanda líquida do agregador
maxAggPower = 135 #(kw) limite máximo de demanda líquida do agregador

#Cria objeto para a tarifa usada
tariff = tf.Tariffs(0.58878, 0.48771, 0.80221, 1.26812) 


"""
Parâmetros de amostragem
"""
sampleInterval = 5 #Intervalo de amostragem (em Minutos)
MINUTS_IN_ONE_DAY = (60*24) #Minutos em 1 dia
one_hour_in_samples = (60/sampleInterval) # 1 Hora em Amostas
n_samples = (MINUTS_IN_ONE_DAY / sampleInterval) # Quantidade de amostras em 1 dia
first_sample = 1 #Primeira amostra
last_sample = n_samples #Última amostra


"""
Parâmetros da bateria do agregador
"""
agBat_initEnergy = 20 #800  #20  # (kwh) Energia inicial da bateria
agBat_minEnergy = 12.5 #200  #12.5 # (kwh) Energia Mínima da bateria
agBat_maxEnergy = 62.5 #1600  #62.5 # (kwh) Energia Máxima da bateria
agBat_minPower = -15 #-400  #-15 # (Kw) Limite de DESCARGA máximo (valor é nagativo) 
agBat_maxPower = 15 #400    #15 # (Kw) Limite de CARGA máximo (valor positivo)
agBat_effc = 0.9 # = 90(%) Efficiência da bateria

"""
Parâmetros da bateria dos consumidores ativos
"""
#bat_minEnergy =  # (kwh) Energia Mínima da bateria
bat_maxEnergy = 13.4 # (kwh) Energia Máxima da bateria
bat_minPower = -2 # (Kw) Limite de DESCARGA máximo (valor é nagativo) 
bat_maxPower = 2 # (Kw) Limite de CARGA máximo (valor positivo)
bat_effc = 0.9 # = 90(%) Efficiência da bateria

    
"""
Parâmetros do algoritmo genético do agregador (Alg3)
"""
popLengthforCA = 10
numbGenerations = 30

"""
Parâmetros do algoritmo genético do consumidor ativo (Alg2)
"""
popLengthforConsumer = 10

def getPVpower():
    pvPower = np.zeros(int(n_samples))
    
    fator = int(one_hour_in_samples)
    pvPower[6*fator:7*fator] = np.ones(int(one_hour_in_samples))*0.402
    pvPower[7*fator:8*fator] = np.ones(int(one_hour_in_samples))*4.064
    pvPower[8*fator:9*fator] = np.ones(int(one_hour_in_samples))*8.033
    pvPower[9*fator:10*fator] = np.ones(int(one_hour_in_samples))*11.162
    pvPower[10*fator:11*fator] = np.ones(int(one_hour_in_samples))*13.033
    pvPower[11*fator:12*fator] = np.ones(int(one_hour_in_samples))*13.905
    pvPower[12*fator:13*fator] = np.ones(int(one_hour_in_samples))*13.894
    pvPower[13*fator:14*fator] = np.ones(int(one_hour_in_samples))*12.605
    pvPower[14*fator:15*fator] = np.ones(int(one_hour_in_samples))*10.209
    pvPower[15*fator:16*fator] = np.ones(int(one_hour_in_samples))*7.195
    pvPower[16*fator:17*fator] = np.ones(int(one_hour_in_samples))*3.294
    pvPower[17*fator:18*fator] = np.ones(int(one_hour_in_samples))*0.175
    
    
    #Plot Test
    # X = np.arange(0,n_samples)
    # xmin = 0
    # xmax = n_samples + 1
    # fig = plt.figure(1)
    # fig, ax = plt.subplots()
    # plt.axis([xmin,xmax,0,20])
    # plt.grid(True)
    # plt.plot(X,pvPower,'-b','LineWidth',3)
    # plt.show()
    
    return pvPower

def getPassiveDemand():
    passiveDemand = np.ones(int(n_samples))
      
    value = np.array([20,51,15,18,17,16,17,14, #0 a 8
                      17,15,21,16,18,15,18,17, #8 a 16
                      16,17,15,16,18,15,21,14, #16 a 24
                    15,13,10,15,16,17,77,82, #24 a 32
                     81,33,65,55,50,25,32,58, #32 a 40
                     37,40,42,44,46,48,50,52, #40 a 48
                     50,48,46,54,53,69,55,60, #48 a 56
                     48,63,42,48,48,38,46,37, #56 a 64
                    35,33,62,64,30,29,30,40, #64 a 72
                    40,36,65,80,70,82,110,121,
                      123,121,110,109,107,125,122,122,
                      70,75,57,60,55,62,63,48])
    
    fator = int(n_samples/96)
    for i in range(96):
        passiveDemand[i*fator:3*(i+1)] = value[i] 
    
    return passiveDemand

def getCLdemand():
    """
    Função para configurar a demanda fixa para as CL-Critical Loads (compu-
        tador,iluminação, TV, tomadas, etc) no perfil dos consumidores.
    
    Returns
    -------
    PEAK_LIMIT: list
        vetor que representa as Critical Loads
    """
                    
    # # Limite de pico durante o dia
    # PEAK_LIMIT = np.array(12.0*np.ones(int(n_samples)))
    
    # X = np.arange(0,3*one_hour_in_samples + 1)
    # Y = sp.signal.gaussian(np.size(X), 7) 
    # Y = 1.0*Y# Pico de 1kwh
    # PEAK1 = np.hstack((np.zeros(int(18*one_hour_in_samples)),
    # Y,
    # np.zeros(int(3.0*one_hour_in_samples - 1))))

    # PEAK_LIMIT = PEAK_LIMIT - PEAK1
    
    # return PEAK_LIMIT
    
    clDemand = getPassiveDemand()/3/10
    return clDemand


def getNetCostFunction():
    """
    Função para configurar os parâmetros constantes "a" e "b" da função de 
    custo de energia da rede. Eq. 01: C(p_agB) = a*p_agB^2 + b*p_agB
    
    Returns
    -------
    [a,b]: lista de arrays
        parâmetros da função de custo de energia da rede
    """
       
    # firstLimit = 32
    # a = np.zeros(int(n_samples))
    # b = np.zeros(int(n_samples))
    
    # a[0:firstLimit] = np.ones(int(firstLimit))*0.6      
    # a[firstLimit:int(n_samples)] = np.ones(int(n_samples-firstLimit))*0.8
    
    # b[0:firstLimit] = np.ones(int(firstLimit))*0.045      
    # b[firstLimit:int(n_samples)] = np.ones(int(n_samples-firstLimit))*0.06
    
    # return [a,b]
    
    tarifaBranca = tf.Tariffs(0.58878, 0.48771, 0.80221, 1.26812)
    return tarifaBranca.getTarifaBrancaVector(sampleInterval) 

#Método para o Geofind
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
    #L=[l1,l2,l3,l4,l5]
    return L

def getTime(sample):
    hour = math.floor(sample/one_hour_in_samples)
    minuts = int((sample - (hour*one_hour_in_samples))*sampleInterval)
    
    return str(hour) + ':' + str(minuts)

    
    
def setRandomLoads(size):
    L = [None]*size
    maxLoadPower = 3
    for i in range(int(size)):
        minT = np.random.randint(0,n_samples-1)
        
        cond = True
        while(cond):
            duration = np.random.randint(1,6*one_hour_in_samples)
            if(minT + duration <= n_samples-1):
                cond = False
        
        if(minT + duration >= (n_samples)):
            print('Vai dar erro')
        
                    
        maxT = np.random.randint((minT + duration), n_samples)
        
        if(minT >= (maxT - duration)+1):
            print('Vai dar erro')
        
        expect = np.random.randint(minT, (maxT - duration)+1)
        
        avg =  (maxLoadPower/100)*randrange(1, maxLoadPower, 1)
        peak = 0.1*randrange(1, 5, 1)
            
        L[i] = app.TimeFlexLoad('L'+str(i+1), getTime(minT), getTime(expect), getTime(maxT), getTime(duration), avg, peak, 1)
        
        print(getTime(expect))
    return L


def setRandomIntervalLoads():
    
    # apps1=[app.TimeFlexLoad('Clothes WS 1', 1, int(np.random.normal(34, 4)), int(np.random.normal(70, 5)), [int(np.random.normal(47, 4))], [45], False, [1.3], [1.7], 1),

    size=10
    L = [None]*size
    maxLoadPower = 3
    for i in range(int(size)):
        
        if(i>2):
            minT = np.random.randint(0,n_samples-1)
            
            cond = True
            while(cond):
                duration = np.random.randint(1,3*one_hour_in_samples)
                if(minT + duration <= n_samples-1):
                    cond = False
            
            if(minT + duration >= (n_samples)):
                print('Vai dar erro')
            
                        
            maxT = np.random.randint((minT + duration), n_samples)
            
            if(minT >= (maxT - duration)+1):
                print('Vai dar erro')
            
            expected = np.random.randint(minT, (maxT - duration)+1)
        else:
            t=11*one_hour_in_samples
            minT = int(np.random.normal(t, 5))
            
            cond = True
            while(cond):
                duration = np.random.randint(1,3*one_hour_in_samples)
                
                t=22*one_hour_in_samples
                maxT = int(np.random.normal(t, 5))
                
                if(maxT > n_samples-1):
                    maxT = n_samples-1
                
                t=18*one_hour_in_samples
                expected = int(np.random.normal(t, 7))
                
                if( (minT + duration <= maxT) and (expected + duration < maxT)):
                    cond = False
            
        
        #avg =  (maxLoadPower/100)*randrange(1, maxLoadPower, 1)
        avg = np.random.normal(2, 0.5)
        
        peak = 0.1*randrange(1, 5, 1)
            
        L[i] = app.TimeFlexLoad('L'+str(i+1), getTime(minT), getTime(expected), getTime(maxT), getTime(duration), avg, peak, 1)
        
        print(getTime(expected))
    
    return L


def setloads():
    l1 = app.TimeFlexLoad('Bomba booster', '7:00', '8:00','17:00','00:15', 2, 3, 0.1)
    l2 = app.TimeFlexLoad('Bomba Piscina', '7:00','8:00','17:00','02:00', 0.75, 1.2, 0.1)
    l3 = app.TimeFlexLoad('maquina de lavar', '7:00', '8:00','17:00','00:15', 0.13, 0.7, 0.5)
    l4 = app.TimeFlexLoad('lâmpadas externas', '17:00','18:00','23:59', '04:30', 0.3, 0.3, 0.3);
    l5 = app.TimeFlexLoad('lâmpadas internas', '17:00','18:00','23:00', '04:30', 0.15,0.3, 0.7);
    l6 = app.TimeFlexLoad('AC office', '15:00','16:00','23:59', '00:45', 1.3, 1.7, 1);
    l7 = app.TimeFlexLoad('AC couples','17:00','20:00','23:59', '00:30', 2, 2.1, 1);
    l8 = app.TimeFlexLoad('AC F1', '17:00','20:00','23:59','04:00',  1.1, 1.2, 1);
    l9 = app.TimeFlexLoad('AC F2', '17:00','20:00','23:59', '00:45',  0.9, 1.1, 1);
    l10 = app.TimeFlexLoad('lava-louças', '18:00','21:00','22:00', '00:45', 1.0, 1.76, 0.3);


    L=[l1,l2,l3,l4,l5,l6,l7,l8,l9,l10]
    #L=[l1,l2,l3,l4,l5]
    return L


    
def setConsumers():
    """
    Função para criar os cosumidores ativos e configura os seus devidos 
        parâmetros.

    Returns
    -------
    [h1, ..., hn]: list
    lista contendo todos os n consumidores ativos criados (h1,...,hn)
    """
   
    #loads = setPUloads()
    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    
    w_n=[0.8,0.2,0]
    beta_app = 1
    gama_app = 1
    CLdemand = getCLdemand()
    
    h1=ac.ActiveConsumer('H1',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
    
    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    h2=ac.ActiveConsumer('H2',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
    
    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    h3=ac.ActiveConsumer('H3',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
    
    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    h4=ac.ActiveConsumer('H4',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)

    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    h5=ac.ActiveConsumer('H5',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
    
    #loads = setRandomLoads(10)    
    loads = setRandomIntervalLoads()
    h6=ac.ActiveConsumer('H6',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)

    #loads = setRandomLoads(10)    
    loads = setRandomIntervalLoads()
    h7=ac.ActiveConsumer('H7',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
    
    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    h8=ac.ActiveConsumer('H8',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
    
    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    h9=ac.ActiveConsumer('H9',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
    
    #loads = setRandomLoads(10)
    loads = setRandomIntervalLoads()
    h10=ac.ActiveConsumer('H10',loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)

    
    return [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10]
    #h1, h2, h3, h4, h5, h6, h7, h8, h9, h10]
    #return [h1, h2, h3, h4, h5]


def setNConsumers(N):
    w_n=[0.8,0.2,0]
    beta_app = 1
    gama_app = 1
    CLdemand = getCLdemand()
    
    consumers = [None]*N
    for i in range(N):
        loads = setRandomLoads(10)
        loads = setRandomIntervalLoads()
        consumers[i] = ac.ActiveConsumer('H'+str(i+1),loads, w_n[0], w_n[1], w_n[2], beta_app, gama_app, CLdemand)
        
    return consumers

