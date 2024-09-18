# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 22:11:18 2023

@author: Usuario
"""
import numpy as np
import scenarioParameters as sn
#import copy
import geneticAlgorithmAggregator as ga


#A 20 kWp solar PV system and 


class Aggregator:
    """
    Classe que representa o Community Aggregator (CA)
    ...

    Attributes (em construção)
    ----------
    p_agMin: float
        Potência mínima do agregador
    p_agMax:: float
        Potência máxima do agregador
    lambda_: int
        Valor que representa os custos adicionais aplicados para forçar os
        consumidores a satisfazer as restrições compartilhadas.
    E_agB_min: float
        Energia Mínima da bateria
    E_agB_max: float
        Energia Máxima da bateria
    p_agB_disch: float
      limite de DESCARGA da bateria (valor negativo)
    p_agB_ch: float
      limite de CARGA da bateria (valor negativo)
    batEfficiency: float
      Efficiência da bateria
    p_agPV: float
        Potência do sistema de energia solar
    
    Methods
    -------
    setBatteryProfile()
        Configura os parâmetros do sistema de bateria do Agregador
    
    setPVProfile():
        Configura os parâmetros do sistema fotovoltaico do Agregador
        
    updateLoadProfile():
       Calcula o perfil de carga dos consumidores = soma do 
       consumo de todos os condumidores ativos.
    
    calcBatteryEnergyInTimeSlot():
        Calcula a energia da bateria do agregador, ao longo do dia.
    
    calcNetCostFunction():
        Função para calculacar Zc: a função de custo de energia elétrica

    calcViolation(): 
        Função para calcular Zviol:(overall violation value of inequality and
        equality constraints) 
    
    initPopulation():
        Função para inicializar, de forma aleatória, a população do algoritmo
        genético do agregador. 
    
    calcFitness():
        Função para calcular função Fitness, ou seja Zca, função objetivo do 
        agregador(CA). 
    
    geneticAlgorithmForCA():
        Função para o procedimento do algoritmo genético do agregador
       
    """

    def __init__(self, p_agMin, p_agMax, lambda_):
        """
         Parameters
         ----------
         p_agMin: float
             Limite de demanda de Potência mínima do agregador
         p_agMax:: float
             Limite de demanda de Potência máxima do agregador
         lambda_: int
             Valor que representa os custos adicionais aplicados para forçar os
             consumidores a satisfazer as restrições compartilhadas.   
        """
        self.p_agMin = p_agMin
        self.p_agMax = p_agMax
        self.lambda_ = lambda_ 
        
        self.loadProfile = np.zeros(int(sn.n_samples))
        
        self.P_ag_B = np.zeros(int(sn.n_samples))
        
    def setPagB(self, p_ag_B):
        self.P_ag_B = p_ag_B
        
    #OK
    def setBatteryProfile(self, bat_initEnergy, bat_minEnergy, bat_maxEnergy, bat_dischPower, bat_chPower, bat_effc):
        """Função para configurar os parâmetros do sistema de bateria do Agregador
        
        Parameters
        ----------
        bat_minEnergy: float
          limite de Energia Mínima da bateria
        bat_maxEnergy: float
          Limite de Energia Máxima da bateria
        bat_dischPower: float
          limite de DESCARGA da bateria (valor negativo)
        bat_chPower: float
          limite de CARGA da bateria (valor positivo)
        bat_effc: float
          Efficiência da bateria
                    
        """
        self.E_agB_init = bat_initEnergy 
        self.E_agB_min = bat_minEnergy 
        self.E_agB_max = bat_maxEnergy 
        self.p_agB_disch = bat_dischPower
        self.p_agB_ch = bat_chPower
        self.batEfficiency = bat_effc 
        
    #OK    
    def setPVProfile(self, pvPower):
        """Função para configurar os parâmetros do sistema fotovoltaico do
        agregador.
        
        Parameters
        ----------
        pvPower : list
          vetor com os vlaores de Potência do sistema de energia solar
                    
        """
        self.p_agPv = pvPower 
   
    #OK
    def calcActiveLoad(self, aConsumers):
        """Função para calcular o perfil de carga ativa = soma do 
        consumo de todos os condumidores ativos.

        Parameters
        ----------
        aConsumers : list<ActiveConsumer>
            lista dos consumidores ativos
        
        Returns
        -------
        activeLoad : list
            vetor com o valor do consumo total de todos os consumidores ativos
            ao longo do dia

       """
        self.activeLoad = np.zeros(int(sn.n_samples))
    
        for n in aConsumers:
            self.activeLoad = self.activeLoad + n.loadProfile
            
        
        return self.activeLoad

    #OK        
    def calcLoadProfile(self, aConsumers):
        """Função para calcular o perfil inicial de carga total (L_t ^D) = soma do 
        consumo inicial de todos os condumidores ativos + consumo dos consumidores
        passivos. L

        Parameters
        ----------
        aConsumers : list<ActiveConsumer>
            lista dos consumidores ativos
                   
        Returns
        -------
        loadProfile : list
            vetor com o valor do consumo total de todos os consumidores (ativos
            e passivos) ao longo do dia 

       """
        
        loadProfile = self.calcActiveLoad(aConsumers) + sn.getPassiveDemand()
        
        return loadProfile
    
    #OK
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
    
        
    #OK
    # def calcLminusN(self, activeConsumer, p_ag_B):
    #     """Função para configurar o valor de L-n, consumo total do agregador 
    #     menos o consumo do consumidor n.

    #     Parameters
    #     ----------
    #     activeConsumer : ActiveConsumer
    #         consumidores ativo n
    #     P_ag_B : list
    #         vetor com os valores de potência da bateria do agregador
        
    #     Returns
    #     -------
    #     LminusN : list
    #         vetor com o consumo total do agregador menos o consumo do
    #         consumidor n.
    #    """
       
    #     L = self.loadProfile
    #     LminusN = (L - activeConsumer.loadProfile ) - self.p_agPv + p_ag_B
        
    #     return LminusN
    
   
    #OK    
    def calcBatteryEnergy(self, p_agB):
        """Função para calcular a energia da bateria do agregador, ao longo do
        dia. Eq.18
        
        Parameters
        ----------
        p_agB : list
          vetor com a potência da bateria (carga/descarga), ao longo do dia
          
        Returns
        -------
        E_agB : list
            vetor com a energia da bateria do agregador, ao longo do dia.
                    
        """
        Delta_t = sn.sampleInterval/60 #amostras em 1 hora
        E_agB = np.zeros(int(sn.n_samples)) #inicialização
        
        #E_agB[0] = p_agB[0]*Delta_t*self.batEfficiency
        E_agB[0] = self.E_agB_init + p_agB[0]*Delta_t*self.batEfficiency
        
        for t in range(int(sn.n_samples-1)):
            E_agB[t+1] = E_agB[t] + p_agB[t]*Delta_t*self.batEfficiency
        
        
        return E_agB
    
    #OK
    def calcNetDemand(self, L, p_agB):
        """Função para calculacar a demanda líquida do agregador ao longo do 
        dia. Eq. 02

        Parameters
        ----------
        L : list
            Consumo total de todos os consumidores (ativos e passivos) 
        p_agB : list
          vetor com a potência da bateria (carga/descarga), ao longo do dia
          
        Returns
        -------
        p_ag : list
           Demand líquida do agregador
        """
       
        p_ag = L - self.p_agPv + p_agB
        
        return p_ag        

    #OK        
    def calcNetCostFunction(self, p_ag):
        """Função para calculacar Zc: a função de custo de energia elétrica.
        Eq. 27

        Parameters
        ----------
        p_ag : list
           Demand líquida do agregador
           
        Returns
        -------
        Zc : float
            Valor da custo total de energia elétrica
            do dia
        """
        #escalares referentes ao preço da energia em cada timeslot
        tb = sn.getNetCostFunction() 
        Zc = sum(p_ag*tb)
        
        # [a,b] = sn.getNetCostFunction() 
    
        # Zc=0
        # for t in range(int(sn.n_samples)):
        #     Zc= Zc + a[t]*np.power(p_ag[t],2) + b[t]*p_ag[t]
                
        return Zc
    
    #OK
    def calcViolation(self, L, p_ag, p_agB): 
        """Função para calcular Zviol:(overall violation value of inequality and
        equality constraints). Eq. 48 

        Parameters
        ----------
        L : 
            Consumo total de todos os consumidores (ativos e passivos) 
        p_ag:
            Demand líquida do agregador
        p_agB : list
          vetor com a potência da bateria (carga/descarga), ao longo do dia
          
        Returns
        -------
        Zviol : float
            valor da violação das igualdades e igualdades das restrições
       """
        
        delta_ = 0.0001 #valor de tolerância para as restrições de igualdade
        
        Zviol = 0
        E_agB = self.calcBatteryEnergy(p_agB)
        
        for t in range(int(sn.n_samples)):    
            aux=(L[t] - self.p_agPv[t] - p_ag[t] + p_agB[t])
            p1 = max(0,  abs(aux) - delta_) 
            pmax = max(0, (E_agB[t] - self.E_agB_max))
            #pmin = max(0, (-E_agB[t] - self.E_agB_min))
            pmin = max(0, (self.E_agB_min - E_agB[t]))
            
            # if(pmin>0):
            #     print('aqui:', E_agB[t])
            
            Zviol_aux = p1 + pmax + pmin
            
            Zviol = Zviol + Zviol_aux
        
        return Zviol
    
    #OK
    def calcZca(self, p_agB):
        """Função para calcular a função Fitness, ou seja Zca, função objetivo do 
        agregador(CA). Eq. 47

        Parameters
        ----------
        L : 
            Consumo total de todos os consumidores (ativos e passivos)    
        p_ag_B: 
            Vetor de estratégias da bateria
        
        Returns
        -------
        Zviol : float
            valor da violação das igualdades e igualdades das restrições
       """
        M = 500000 #a large positive number
        
        L = self.loadProfile
        
        #Calcula p_ag : demanda líquida do agregador
        p_ag = self.calcNetDemand(L, p_agB)
        
        #Calcula Zc: (Overall Energy Cost)
        Zc = self.calcNetCostFunction(p_ag)
        
            
        #Calcula q: (shared constraints) Eq. 34
        # q = 0
        # q_max = 0
        # for t in range(int(sn.n_samples)):    
        #     #q_min = q_min + ( self.p_agMin - (L[t] - self.p_agPv[t] + p_agB[t]) )
        #     q_max = ( (L[t] - self.p_agPv[t] + p_agB[t]) - self.p_agMax )
        #     q += max(0,q_max)
        
        #p_ag = p_ag + 10*self.rules(p_agB, p_ag)
        
        
        #Calcula Zviol: 
        #(overall violation value of inequality and equality constraints)
        Zviol = self.calcViolation(L, p_ag, p_agB)
        
        # if(q>0):
        #     print('PAre')
            
        Zca = Zc + M*Zviol
        #print('Zca:',Zca)
        return Zca
    

    def calcInitBatteryDispatch(self):
                
        [p_ag_B,Zca] = ga.runGeneticAlgorithm(self, 50, 'Init')
        
        netDemand = self.calcNetDemand(self.loadProfile, p_ag_B)
        
        return [p_ag_B, netDemand]
    
    def calcBatteryDispatch(self):
        print("------   Início     -------")
                
        [p_ag_B,Zca] = ga.runGeneticAlgorithm(self, 3000, 'Sol')
        
        netDemand = self.calcNetDemand(self.loadProfile, p_ag_B)
        
        return [p_ag_B, netDemand]
    
    def rules(self, p_ag_B, netDemand):
        rules = np.zeros(int(sn.n_samples))
        for t in range(int(sn.n_samples)):
            if(netDemand[t]>170):
                rules[t] = netDemand[t] - 170
        return rules
    
    # def rulesOtmimization(self):
    #     for t in range(int(sn.n_samples)):
            
    #         if(self.loadProfile[t] > self.p_agMax):
    #             if(self.p_agPv <= (self.loadProfile[t] - self.p_agMax)):
    #                 #Regra 1
    #             elif ( ):
    #         else:
                
                