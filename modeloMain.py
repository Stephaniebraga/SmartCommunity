# -*- coding: utf-8 -*-
###########################################################################
# Universidade Federal do Ceará
# Doutorado - PPGETI 
# Autor:  Stéphanie A. Braga dos Santos
# Algoritmo Distribuído - Stackelberg Equilibrium Game
###########################################################################
import numpy as np
import scenarioParameters as sn
import aggregator as ag
import matplotlib.pyplot as plt
import time
import Tariffs

start_time = time.time()


# Cria Objeto para o Community Aggregator (CA), configurando os seus devidos
# atributos.
ca = ag.Aggregator(sn.minAggPower,sn.maxAggPower, sn.lambda_)

# Cria lista de Objetos dos consumidores ativos, configurando os seus devidos
# atributos.
activeConsumers = sn.setConsumers()
#sn.setRandomIntervalLoads()
#activeConsumers = sn.setNConsumers(1000)



#CA recebe informações de todos os consumidores e 
# Calcula Total Initial load Profile (L0)
initLoadProfile = ca.calcLoadProfile(activeConsumers)
ca.setLoadProfile(initLoadProfile)

#CA lê o perfil de geração previsto do sistema fotovoltaico e o armazenamento
#inicial da bateria
ca.setBatteryProfile(sn.agBat_initEnergy, sn.agBat_minEnergy, sn.agBat_maxEnergy, sn.agBat_minPower, sn.agBat_maxPower, sn.agBat_effc)
ca.setPVProfile(sn.getPVpower())

#Para Plotar (Calcula base do consumo dos consumidores ativos)
baseActiveLoad = ca.calcActiveLoad(activeConsumers)

#Calcula o P_ag, sem a energia da bateria, apenas com PV
init_P_ag = ca.calcNetDemand(initLoadProfile, 0)
initCost = ca.calcNetCostFunction(init_P_ag)

Solutions = [None]*len(activeConsumers)
i=0
for n in activeConsumers:
   
    [U,solution] = n.shcToActiveConsumer() #Resolve 43
    Solutions[i] = solution
    nLoadProfile = n.calcLoadProfile(solution)
    n.setLoadProfile(nLoadProfile)
    i+=1
          

caLoadProfile = ca.calcLoadProfile(activeConsumers)
ca.setLoadProfile(caLoadProfile)          

#Calcula o P_ag após SHC, sem a energia da bateria, apenas com PV
shc_P_ag = ca.calcNetDemand(caLoadProfile, 0)


P_ag_B , P_ag = ca.calcBatteryDispatch() #resolve 36 (na verdade é 35)
Zca = ca.calcZca(P_ag_B)
finCost = ca.calcNetCostFunction(P_ag)



tempo = (time.time() - start_time)
print("Finalizou em", tempo/60, 'minutos')


print("Custo sem Bateria:", initCost/sn.one_hour_in_samples)
print("Custo com Bateria:", finCost/sn.one_hour_in_samples)

print('Ganho de:',((initCost - finCost)/initCost)*100)

"""
    Plots
"""
N_SAMPLES = sn.n_samples # Quantidade de amostras em 1 dia
ONE_HOUR_IN_SAMPLES = sn.one_hour_in_samples

 
xlabel = 'Tempo [horas]'
ylabel = 'Power [kW]'
xticks1 = np.hstack(([1*ONE_HOUR_IN_SAMPLES, 2*ONE_HOUR_IN_SAMPLES, 3*ONE_HOUR_IN_SAMPLES, 4*ONE_HOUR_IN_SAMPLES,
5*ONE_HOUR_IN_SAMPLES, 6*ONE_HOUR_IN_SAMPLES, 7*ONE_HOUR_IN_SAMPLES, 8*ONE_HOUR_IN_SAMPLES,
9*ONE_HOUR_IN_SAMPLES, 10*ONE_HOUR_IN_SAMPLES, 11*ONE_HOUR_IN_SAMPLES, 12*ONE_HOUR_IN_SAMPLES, 
13*ONE_HOUR_IN_SAMPLES, 14*ONE_HOUR_IN_SAMPLES, 15*ONE_HOUR_IN_SAMPLES, 16*ONE_HOUR_IN_SAMPLES,
17*ONE_HOUR_IN_SAMPLES, 18*ONE_HOUR_IN_SAMPLES, 19*ONE_HOUR_IN_SAMPLES, 20*ONE_HOUR_IN_SAMPLES,
21*ONE_HOUR_IN_SAMPLES, 22*ONE_HOUR_IN_SAMPLES, 23*ONE_HOUR_IN_SAMPLES, 24*ONE_HOUR_IN_SAMPLES ]))
xticks2 = ('01','','03','','05','','07','','09','','11','',
'13','','15','','17','','19','','21','','23', '')
 
xmin = 0
xmax = sn.n_samples + 1
X = np.arange(0,sn.n_samples)

fig = plt.figure(1)
fig, ax = plt.subplots()
plt.axis([xmin,xmax,0,100])
plt.grid(True)

#plt.plot(X,sn.getPassiveDemand(),'k--',color='blue',label='Passive Load')
#plt.plot(X,baseActiveLoad,'k-.',color='red', label='Base Active Load')
plt.plot(X,init_P_ag,color='orange',label='Agggregate Demand Pag')
#plt.plot(X,initialNetElectricity,color='black',label='Optimal Agggregate Demand Pag*')
#plt.plot(X,ca.calcActiveLoad(activeConsumers),'k-.',color='purple', label='Optimal Active Load')
plt.plot(X,P_ag,color='green',label='Optimal Agggregate Demand Pag*')
plt.plot(X,shc_P_ag,color='yellow',label='Agggregate Demand Pag after SHCs')


plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.xticks(xticks1, xticks2 )   
plt.legend()

color = [ ['darkblue'],
         ['magenta'],
         ['aqua'],
         ['darkgreen'],
         ['sienna'],
         ['lime', 'lime'],
         ['yellow'],
         ['orange'],
         ['red'],
         ['black']]
lab = ['Bomba Booster',
         'Bomba Piscina',
         'Máquina de lavar',
         'Lâmpadas Externas',
         'Lâmpadas Internas',
         'AC office',
         'AC couples',
         'AC F1',
         'AC F2', 
         'Lava-louças']



fig = plt.figure(1)
fig, ax = plt.subplots(2)
plt.axis([xmin,xmax,0,0.15])
plt.grid(True)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.xticks(xticks1, xticks2 )   

# Plota as cargas com o tempo esperado
APP = np.zeros((int(sn.n_samples)))
APP_aux = np.zeros((int(sn.n_samples)))
i=0
for a in activeConsumers[0].appliances:
    
    DURATION = int(a.durationInSamples)
    
    startTime = int(a.expectedTimeInSamples) 
                    
    init = startTime  
    fin = startTime + DURATION
    
    APP[init:fin] +=  np.ones(DURATION)*a.avgPower
    
    APP_aux[init:fin] = APP[init:fin]
    ax[0].plot(X,APP_aux, color[i][0],label=lab[i])
    ax[0].stackplot(X,APP_aux, colors=color[i], alpha=0.7)
    
    
    APP_aux = np.zeros((int(sn.n_samples)))
    
    i+=1 

# Plota as cargas com o tempo solution
APP = np.zeros((int(sn.n_samples)))
APP_aux = np.zeros((int(sn.n_samples)))
i=0
for a in activeConsumers[0].appliances:
    
    DURATION = int(a.durationInSamples)
    
    startTime = int(Solutions[0][i]) 
                    
    init = startTime  
    fin = startTime + DURATION
    
    APP[init:fin] +=  np.ones(DURATION)*a.avgPower
    
    APP_aux[init:fin] = APP[init:fin]
    ax[1].plot(X,APP_aux, color[i][0],label=lab[i])
    ax[1].stackplot(X,APP_aux, colors=color[i], alpha=0.7)
    
    
    APP_aux = np.zeros((int(sn.n_samples)))
    
    i+=1 



#for s in solution
#s=solutionList[0]  

#Calc 


# i=0     
# for a in activeConsumers:
   
#     fig = plt.figure(1)
#     fig, ax = plt.subplots()
#     plt.axis([xmin,xmax,0,15])
#     plt.grid(True)
    
#     plt.title("Perfil " + a.name)
#     plt.plot(X,a.initialLoadProfile, color='red',label='base')
#     plt.plot(X,a.loadProfile, color='green',label='optimal')
#     plt.xlabel(xlabel)
#     plt.ylabel(ylabel)
#     plt.xticks(xticks1, xticks2)   
#     plt.legend()
#     i+=1

fig = plt.figure(1)
fig, ax = plt.subplots()
plt.axis([xmin,xmax,-20,20])
plt.grid(True)
#stem=plt.stem(X,init_P_ag_B,linefmt='red')
#stem[1].set_linewidth(0.8)
stem=plt.stem(X,P_ag_B,label='teste')
stem[1].set_linewidth(1)
#stem[1].xticks(xticks1, xticks2)
#plt.xticks(xticks1, xticks2) 
plt.xticks(xticks1, xticks2 )   
plt.legend()


fig = plt.figure(1)
fig, ax = plt.subplots(3)
plt.grid(True)

ax[0].plot(X,ca.calcBatteryEnergy(P_ag_B),color='green',label='Energy Battery')
ax[0].set_ylabel('Energia Kwh')
ax[0].legend()
ax[0].set_ylim(0,65)
ax[0].grid(True)

ax[1].plot(X,sn.getPVpower(),color='yellow',label='PV Generation')
ax[1].set_ylabel('Potência Kw')
ax[1].legend()
ax[1].set_ylim(0,15)
ax[1].grid(True)

ax[2].plot(X, sn.getNetCostFunction(), color='blue',label='Tarifa Branca')
ax[2].set_ylim(0,2)
ax[2].set_ylabel('Preço R$')
ax[2].legend(loc='center')
ax[2].grid(True)
#ax.set_xticklabels(xticks2)
plt.legend()
plt.show()
