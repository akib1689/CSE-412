# The inventory system is a class that uses the random number generator to
# simulate a single-product inventory system.  The random number generator



# Path: inventory_system.py

# import lcg_rand
from lcg_rand import Lcgrand

# import math
import math


# constants (event types)
NONE = 0
ARRIVAL = 1
DEMAND = 2
END = 3
EVALUATE = 4

class InventorySystem:
    # constructor
    def __init__(self, initialInventoryLevel, numMonths, numPolicy, numValuesDemand, meanInterDemand, setupCost, incrementalCost, holdingCost, shortageCost, minLag, maxLag, probDistribDemand, policies, numEventsTypes=4):
        self.generator = Lcgrand()
        
        
        self.amount = 0                 # order quantity
        self.bigs = 0                   # number of big demands
        self.smalls = 0                 # number of small demands
        self.initialInventoryLevel = initialInventoryLevel # initial inventory level
        self.inventoryLevel = initialInventoryLevel
        
        self.nextEventType = NONE       # next event type
        self.numEventsTypes = numEventsTypes    # number of event types in the simulation (ARRIVAL, DEMAND, END, EVALUATE)
        
        self.numMonths = numMonths      # number of months to simulate
        self.numPolicy = numPolicy      # number of policies to consider
        
        self.numValuesDemand = numValuesDemand      # number of values of demand
        self.meanInterDemand = meanInterDemand      # mean interdemand time
        
        self.setupCost = setupCost      # setup cost
        self.incrementalCost = incrementalCost      # incremental cost
        self.holdingCost = holdingCost      # holding cost
        self.shortageCost = shortageCost      # shortage cost
        
        
        self.minLag = minLag      # minimum lag between order placement and receipt
        self.maxLag = maxLag      # maximum lag between order placement and receipt
        
        self.probDistribDemand = probDistribDemand      # probability distribution of demand
        
        self.policies = policies      # policies to simulate
        
        self.areaHolding = 0.0          # area under holding cost curve
        self.areaShortage = 0.0         # area under shortage cost curve
        
        
        self.simTime = 0.0              # current simulation time
        self.timeLastEvent = self.simTime      # time of last event processed
        
        
        self.totalOrderingCost = 0.0    # total ordering cost
        
        self.timeNextEvent = [0.0] * (self.numEventsTypes + 1)      # time of next event of each type
        self.report_string = ""
        
        
    def __expon__(self, mean):
        return -mean * math.log(self.generator.lcgrand(1))
    
    def __timing__(self):
        self.nextEventType = NONE               # set default next event type
        minTimeNextEvent = 1.0e+29              # set default min time next event
        
        for i in range(1, self.numEventsTypes + 1):
            if self.timeNextEvent[i] < minTimeNextEvent:
                minTimeNextEvent = self.timeNextEvent[i]        # update min time next event
                self.nextEventType = i                          # update next event type
        
        if self.nextEventType == NONE:
            print("Event list empty at time %f" % (self.simTime))
            exit(1)
        
        self.simTime = minTimeNextEvent
        
    def __updateTimeAvgStats__(self):
        timeSinceLastEvent = self.simTime - self.timeLastEvent
        self.timeLastEvent = self.simTime
        
        if self.inventoryLevel < 0:
            self.areaShortage -= self.inventoryLevel * timeSinceLastEvent
        elif self.inventoryLevel > 0:
            self.areaHolding += self.inventoryLevel * timeSinceLastEvent
            
    def __orderArrival__(self):
        self.inventoryLevel += self.amount
        self.timeNextEvent[ARRIVAL] = 1.0e+30
        
    def __demand__(self):
        demand = self.__randomInteger__(self.probDistribDemand)
        # print("Demand: ", demand)
        self.inventoryLevel -= demand
        self.timeNextEvent[DEMAND] = self.simTime + self.__expon__(self.meanInterDemand)
        
    def __evaluate__(self):
        # print("Evaluate at time: ", self.simTime)
        if self.inventoryLevel < self.smalls:
            self.amount = self.bigs - self.inventoryLevel
            self.totalOrderingCost += self.setupCost + self.incrementalCost * self.amount
            self.timeNextEvent[ARRIVAL] = self.simTime + self.__uniform__(self.minLag, self.maxLag)
        self.timeNextEvent[EVALUATE] = self.simTime + 1.0
        
    def __randomInteger__(self, probDistrib):
        i = 0
        u = self.generator.lcgrand(1)
        for i in range(1, self.numValuesDemand + 1):
            if u <= probDistrib[i]:
                break
        return i
        
    def __uniform__(self, a, b):
        return a + (b - a) * self.generator.lcgrand(1)
    
    def __reset__(self):
        self.simTime = 0.0
        self.inventoryLevel = self.initialInventoryLevel
        self.timeLastEvent = self.simTime
        
        self.totalOrderingCost = 0.0
        self.areaHolding = 0.0
        self.areaShortage = 0.0
        
        self.timeNextEvent[ARRIVAL] = 1.0e+30
        self.timeNextEvent[EVALUATE] = 0.0
        self.timeNextEvent[DEMAND] = self.simTime + self.__expon__(self.meanInterDemand)
        self.timeNextEvent[END] = self.numMonths
    
    def __simulateSinglePolicy__(self, s, S):
        self.smalls = s
        self.bigs = S
        
        self.__reset__()
        
        while True:
            self.__timing__()
            self.__updateTimeAvgStats__()
            if self.nextEventType == ARRIVAL:
                self.__orderArrival__()
            elif self.nextEventType == DEMAND:
                self.__demand__()
            elif self.nextEventType == EVALUATE:
                self.__evaluate__()
            elif self.nextEventType == END:
                self.__report__()
                break
            
    def __report__(self):
        avgOrderingCost = self.totalOrderingCost / self.numMonths
        avgHoldingCost = self.areaHolding * self.holdingCost / self.numMonths
        avgShortageCost = self.areaShortage * self.shortageCost / self.numMonths
        report_str = "(%2d,%3d) %19.2f %19.2f %19.2f %19.2f\n\n" % (self.smalls, self.bigs, avgOrderingCost + avgHoldingCost + avgShortageCost, avgOrderingCost, avgHoldingCost, avgShortageCost)
        self.report_string += report_str
            
    
    def simulate(self):
        for i in range(self.numPolicy):
            s, S = self.policies[i]
            self.__simulateSinglePolicy__(s, S)
        