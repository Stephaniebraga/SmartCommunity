# -*- coding: utf-8 -*-
###########################################################################
# Universidade Federal do Ceará
# Doutorado - PPGETI
# Autor:  Stéphanie A. Braga dos Santos
# Rascunho - Cooperative Energy Management
###########################################################################
import numpy as np
import scenarioParameters as sn
import geoFind as gf
 
class ActiveConsumer:
    """
    Classe que representa um Consumidor ativo
    ...

    Attributes
    ----------
    appliances: 
        objeto que representa um appliance
    w1: float
        fator de prioridade para func. obejtivo 1
    w2: float
        fator de prioridade para func. obejtivo 2
    w3: float
        fator de prioridade para func. obejtivo 3
    beta_app: float
        fator de importância para os appliances termostaticamente controlados
    gama_app: float
        fator de importância para os appliances shiftables
    Cldemand: list
        vetor que representa o consumo crítico não schedulable (Critical Loads)
    loadProfile: list
        vetor com o valor do consumo total ao longo do dia
    pvPower: list
        vetor com a potência do sistema fotovoltaico do consudor, ao longo do dia
    batteryPower: list
        vetor com a potência da bateria do consumidor, ao longo do dia
        
    Methods
    -------
    setBatteryProfile()
        Configura os parâmetros do sistema de bateria do Agregador
        
    calcCostFunction()
        Calcula a função de custo de energia da rede (C)
        
    cal
    """

    def __init__(self, name, appliances, w1, w2, w3, beta_app, gama_app, CLdemand):
        """
        Parameters
        ----------
        name: str
            nome do consumidor
        appliances: appliance
            objeto que representa um appliance
        w1: float
            fator de prioridade para func. obejtivo 1
        w2: float
            fator de prioridade para func. obejtivo 2
        w3: float
            fator de prioridade para func. obejtivo 3
        beta_app: float
            fator de importância para os appliances termostaticamente controlados
        gama_app: float
            fator de importância para os appliances shiftables
        Cldemand: list
            vetor que representa o consumo crítico não schedulable (Critical Loads)
           
       """
        self.name = name
        self.appliances = appliances #appliances 
        self.w1 = w1 #fator de prioridade para func. obejtivo 1
        self.w2 = w2 #
        self.w3 = w3 #
        self.beta_app = beta_app #fator de importância para os appliances
        self.gama_app = gama_app #fator de importância para os appliances
        self.CLdemand = CLdemand
        
        self.pvPower = np.zeros(int(sn.n_samples))
        self.batteryPower = 0
        
        self.setBatteryStorage(0,0,0)
        
        self.solution = 0
        self.count = 0
        self.limitList = 4
        self.listSolution = []
        
        n_apps = len(appliances)
        self.n_apps = n_apps
        expectedApps = np.zeros(n_apps)
        for i in range(n_apps):
            expectedApps[i] = appliances[i].solutionTimeInSamples
            
        self.loadProfile = self.calcLoadProfile(expectedApps)
        self.initialLoadProfile = self.loadProfile
           
    def calcLoadProfile(self, startTimeApps):
        """Função para calcular o perfil inicial de carga de um consumidor 
        ativo = consumo total com as preferências iniciais das cargas. Eq. 20

        Returns
        -------
        loadProfile : list
            vetor com o valor do consumo total ao longo do dia

       """

        APPS_PROFILE = np.zeros((int(sn.n_samples)))
        
        i=0
        for a in self.appliances:
            
            DURATION = int(a.durationInSamples)
            
            startTime = int(startTimeApps[i]) 
                            
            init = startTime  
            fin = startTime + DURATION
            #print(a.name)
            if((fin>288)):
                print("Vai dar erro", fin)
            
            APPS_PROFILE[init:fin] += np.ones(DURATION)*a.avgPower
            i+=1
            
            
        loadProfile = (APPS_PROFILE + self.CLdemand) - self.pvPower + self.batteryPower
        return loadProfile 
    
    def setLoadProfile(self, loadProfile):
        """Função para configurar o atributo perfil de carga total = soma do 
        consumo de todos os condumidores ativos + consumo dos consumidores pas-
        sivos.

        Parameters
        ----------
        loadProfile : list<float>
            lista dos valores perfil de consumo de todos os consumidores ao longo do dia

       """
        self.loadProfile = loadProfile

    def setLminusN(self,LminusN):
        self.LminusN = LminusN
        
    def setPvGeneration(self, pvGenPower):
        self.pvGenPower = pvGenPower
    
    def setBatteryStorage(self, Eb_max, Eb_min, batteryStPower):
        self.Eb_max = Eb_max
        self.Eb_min = Eb_min
        self.batteryStPower = batteryStPower
        
    #Para Geofind
    def calcCost(self, solutionTimes):
        #eq. 21
        
        Delta_t = sn.sampleInterval/60
        tb = sn.getNetCostFunction()
        
        ln = self.calcLoadProfile(solutionTimes)     
        
        f1 = (ln*tb )*Delta_t
                
        return sum(f1)
           
    def calcConfort(self, timeSolution):
    #Eq 23
    
        An =self.n_apps
   
        i=0
        disConf = np.zeros(An)
        for a in self.appliances:
            dn = max(0,abs(timeSolution[i] - a.expectedTimeInSamples))
            dn_tol = max( a.expectedTimeInSamples - a.minTimeInSamples, a.maxTimeInSamples - a.expectedTimeInSamples)
            Ia = 100*(dn/dn_tol)
            
            disConf[i] = Ia*a.comfortLevel
            i+=1
        
        f2 = (1/abs(An))*sum(disConf)
                   
        return f2


    def calcFitness(self, solutionTimes):
        """Função para calcular a função Fitness, ou seja Un, função objetivo do 
         consumidor ativo(n). (É pra ser a Eq. 43, mas ainda não está implemen
         tada.                            
        
         Parameters
         ----------
         subject: list
            função que representa um individuo, ou seja, os vetores referentes 
         aos respectivos app ao longo do dia.
                  
         Returns
         -------
         Un : float
         valor da função objetivo
        """   
        f1 = self.calcCost(solutionTimes)
        f2 = self.calcConfort(solutionTimes)
        Fn = self.w1*f1 + self.w2*f2
            
        M = 500000 #a large positive number
        Fviol = self.calcFnViol(solutionTimes)
        
        qn = 0
        
        Un = Fn + M*Fviol + sn.lambda_*qn

        return Un
    
    def calcFnViol(self, timeSolution):
        #Eq. 44
        
        delta_ = 0.0001 #valor de tolerância para as restrições de igualdade

        #Set energia da bateria em 0, por enquanto        
        Eb = np.zeros(int(sn.n_samples))
        
        ln = self.calcLoadProfile(timeSolution)
        
        profileApp = np.zeros(int(sn.n_samples))
        i=0
        for a in self.appliances:
            profileApp += a.calcAvgPowerProfile(timeSolution[i])
            i+=1
        
        Fn_viol = 0
        for t in range(int(sn.n_samples)):    
            #Restrições relacionadas a bateria do usuário (comentadas por enquanto)
            # pmax =  max(Eb[t] - self.Eb_max)
            # pmin = max(0, (-self.Eb_min - Eb[t]))
            
            #Restrições relacionadas a igualdade de demanda
            aux = abs(ln[t] - ( profileApp[t] + self.CLdemand[t] - self.pvPower[t] + self.batteryPower) )
            p = max(0, aux - delta_)

            Fn_viol += p  #+ pmax + pmin         
        
        return Fn_viol

        
    def shcToActiveConsumer(self):
        
        #Chama método para solucionar o shc
        timeSolution = self.geoFindToActiveConsumer()
        U = self.calcFitness(timeSolution)
                     
        return [U, timeSolution]

    def geoFindToActiveConsumer(self):
        #Cria objeto do tipo Geofind
        gF = gf.GeoFind(self)
        
        #Pega objeto referente a tarifa que esta sendo utilizada no cenário
        tariff = sn.tariff
            
        return gF.bestGeoFindVector(self.appliances, tariff)