# -*- coding: utf-8 -*-
import numpy as np
import scenarioParameters as sn
#import Tariffs as tf
#import math
import copy


"""
    Variáveis Globais
"""
#numbGenerations = sn.numbGenerations
popSize = sn.popLengthforCA
global count
count = 0

solution = 0
limitList = 4
global listSolution 
listSolution = [np.array(None)]*limitList
ca = None

"""
Funções do algoritmo Genético do Agregador
"""
def initPopulation2(popLength, indLength):
    """Função alternativa para inicializar a população do algoritmo
    genético do agregador. Essa função limita o valor de potência, avaliando
    o valor da energia. O indivíduo é o vetor de estratégias da bateria.
    A potência em cada timeslot de tempo é limitada, após avaliação  dos
    intervalo min e max de energia da bateria.
    
    Parameters
    ----------
    popLength : int 
        tamanho da população
    indLength: int
        tamanho do indivíduo
    Returns
    -------
    pop : list
        vetor com a população de indivídios
    """
    global listSolution
    
    Delta_t = sn.sampleInterval/60 #amostras em 1 hora
    pop = [None]*popLength
    
    for i in range(popLength):
        ind = np.zeros(int(sn.n_samples)) 
        E_agB = np.zeros(int(sn.n_samples)) #inicialização
        ind[0] = 1.0*np.random.randint(ca.p_agB_disch, ca.p_agB_ch, 1)
        E_agB[0] = ca.E_agB_init + ind[0]*Delta_t*ca.batEfficiency
        
        #Verifica se há algum valor de potência que excederá os limites
        #de energia da bateria. Se sim, limita o valor de potência.
        for t in range(int(sn.n_samples-1)):
            ind[t+1] = 1.0*np.random.randint(ca.p_agB_disch, ca.p_agB_ch, 1)          
            E_agB[t+1] = E_agB[t] + ind[t+1]*Delta_t*ca.batEfficiency
            
            if(E_agB[t+1]) > ca.E_agB_max:
                ind[t+1] = (ca.E_agB_max - E_agB[t])/(Delta_t*ca.batEfficiency)
                E_agB[t+1] = E_agB[t] + ind[t+1]*Delta_t*ca.batEfficiency
            
            if (E_agB[t+1]) < ca.E_agB_min:
                ind[t+1] = (ca.E_agB_min - E_agB[t])/(Delta_t*ca.batEfficiency)
                E_agB[t+1] = E_agB[t] + ind[t+1]*Delta_t*ca.batEfficiency
        
        pop[i]=ind

    return pop

#OK
def calcFitness(p_agB):
    """Função para calcular a função Fitness, ou seja Zca, função objetivo do 
    agregador(CA). Eq. 47
    
    Parameters
    ----------
    p_ag_B: 
        Vetor de estratégias da bateria
    
    Returns
    -------
    Zviol : float
        valor da violação das igualdades e igualdades das restrições
    """
   
   
    return ca.calcZca(p_agB)

#OK
def susMatingPool(pop, k):
    """Função para realizar mating pool pelo método Stochastic Universal
    Sampling (SUS).
    
    Parameters
    ----------
    pop : list
    população    
    k: int
    número de indivídios selecionados  
    
    Returns
    -------
    keep:list
    array com os índicies dos indivíduos selecionados
    """

    size = int(len(pop))
    #Calcula Fitness total da população
    totalFitness = 0
    fitnessList = np.zeros(size)
    for i in range(size):
        fitnessList[i] = calcFitness(pop[i])
        totalFitness = totalFitness + fitnessList[i]
        
    dist = totalFitness/k
    points=np.zeros(k)
    
    start = np.random.randint(0,dist)
    for j in range(k):
        points[j] = start + j*dist
           
    keep=[] # lista de indices selecionados
    for p in points: 
        i=1
        while (sum(fitnessList[0:i]) < p):
           i= i+1
        keep.append(i-1)
    
    return keep

#OK          
def intermediateCrossover(parent1, parent2, ratio):
    """Função para realizar operação intermediate crossover
    
    Parameters
    ----------
    parent1 : list
        individuo pai 1
    parent2 : list
        individuo pai 2
    ratio: float
        número entre 0 e 1  
    
    Returns
    -------
    child:list
       individuo filho, resultante do cruzamento do pai1 e pai2
    """

    rand = np.random.rand()
    child = parent1 + rand*ratio*(parent2 - parent1)
    
    # size = len(parent1)
    # child = np.concatenate([parent1[0:int(size/2)], parent2[int(size/2):size]])
    return child

#OK
def gaussianMutation(ind, mu, sigma, probMutation):
    """Função para realizar operação mutação pelo método gaussiano
    
    Parameters
    ----------
    ind : list
    individuo
    mu : float
    media
    sigma: float
    desvio padrão 
    probMutation: float
    probabilidade de mutação (entre 0 e 1)
    
    """

    size = len(ind)
    for i in range(size):
        if np.random.random() < probMutation:
            ind[i] += np.random.normal(mu, sigma)
            if(ind[i]> ca.p_agB_ch):
                ind[i]= ca.p_agB_ch
            elif(ind[i]< ca.p_agB_disch):
                ind[i]= ca.p_agB_disch

#OK   
def crossoverAndMutation(mpPop):
    """Função para realizar as operações crossover e mutação na mating pool
    population.
    
    Parameters
    ----------
    mpPop: list
        população após mating pool
            
    Returns
    -------
    childs: list
       geração de filhos gerados a partir da mating pool population
    """

    size = int(len(mpPop))
    ratio = 0.5 #taxa para crossover (entre 0 e 1)
    mu = 0 #media para função normal de mutação
    sigma = 0.3 #desvio padrão para função normal de mutação
    probMutation = 0.7 #probabilidade de mutação
    
    childs =[]
    i=0
    
    #Crossover e mutação entre pares consecutivos, do index 0 a n-2
    while(i < size-1):
        parent1 = mpPop[i] 
        parent2 = mpPop[i+1]
        child = intermediateCrossover(parent1, parent2, ratio)
    
        #mutação
        gaussianMutation(child, mu, sigma, probMutation)
        childs.append(child)
        i=i+1
    
    #Crossover e mutação entre os index n-1 e 0 (primeiro e ultimo elemento)
    parent1 = mpPop[i] 
    parent2 = mpPop[0]
    child = intermediateCrossover(parent1, parent2, ratio)
    gaussianMutation(child, mu, sigma, probMutation)
    childs.append(child)
    
    return childs

def tournamentSelection(parents, childs, n, k):
    """Função para realizar a seleção pelo método torneio para gerar a 
    próxima geração resultante da geração dos pais e dos filhos.
    
    Parameters
    ----------
    parents: list
        geração de pais
    parents: list
        geração de filhos
    n: int
        número de indivíduos que participarão do torneio
    k: int
        número de indivíduos da próxima geração
            
    Returns
    -------
    nextGeneration: list
       geração resultante do torneio entre pais e filhos.
    """
 
    oldGeneration = np.concatenate((parents,childs))
    size = len(oldGeneration)
    
    nextGeneration =[]
    for i in range(k):
        
        index = np.zeros(n)
        fitList = np.zeros(n)
        for a in range(n):
            index[a] = np.random.randint(0,size)
            fitList[a] = calcFitness(oldGeneration[int(index[a])])
        
        aux = np.argmin(fitList)
        print('Zca:',fitList[aux])
        ibest = int(index[aux])
        nextGeneration.append( oldGeneration[ibest])
    
    return nextGeneration                


def runGeneticAlgorithm(aggregator, numbGenerations, mode):
    """Função para o algoritmo genético do agregador. Algoritmo 3 do artigo
    
    Parameters
    ----------
    problemRef: char
        número inteiro que indica qual equação será resolvida. Valor '1' 
        significa equação 47 e '2' significa equação 35.
        
    Returns
    -------
    
    """
    global ca
    global count
    global modePop
    modePop = mode
    ca = aggregator
    #self.problemRef = problemRef
    
    # Inicializa população 
    population = initPopulation2(popSize, sn.n_samples)

    # if(mode == 'Sol' ):
    #     index = np.random.randint(0,popSize)
    #     population[index] = ca.P_ag_B
        
    genCount=0
    # Loop enquanto a população não converge
    while (genCount <= numbGenerations):
        genCount = genCount+1
        print('Geração:',genCount)
        
        #Aplica Stochastic Universal Sampling na população para mating pool
        selecIndex = susMatingPool(population, 10) 
        matingPollPop = [None]*popSize
        for i in range(popSize):
            index=selecIndex[i]
            matingPollPop[i] = (copy.copy(population[index]))
        
        
        # matingPollPop
        #Crossover e mutação em toda a população mating pool
        childs = crossoverAndMutation(matingPollPop)
        
        #Tournament Selection
        n=3
        k= popSize
        population = tournamentSelection(matingPollPop,childs, n, k)
              
    #Seleciona melhor solução (melhor individuo)
    fitnessList = np.zeros(int(popSize))
    for i in range(popSize):
        fitnessList[i] = calcFitness(population[i])
        
    iBest = np.argmin(fitnessList)
    bestIndiv = population[iBest]
    
    #Para ajudar na inicialização da população
    solution = bestIndiv  
    return [bestIndiv, fitnessList[iBest]]

#def rules():
    
