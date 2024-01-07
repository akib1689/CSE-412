# main file to run the simulation

# import inventory_system
from inventory_system import InventorySystem

InputFileName = "in.txt"
outputFileName = "out.txt"

def writeParameters(inventorySystem, outputFile):
    with outputFile as file:
        file.write("------Single-Product Inventory System------\n\n")
        file.write("Initial inventory level: %d items\n\n" % (inventorySystem.initialInventoryLevel))
        file.write("Number of demand sizes: %d\n\n" % (inventorySystem.numValuesDemand))
        file.write("Distribution function of demand sizes: ")
        
        for i in range(1, inventorySystem.numValuesDemand + 1):
            file.write("%.2f " % (inventorySystem.probDistribDemand[i]))
        
        file.write("\n\n")
        
        file.write("Mean inter-demand time: %.2f months\n\n" % (inventorySystem.meanInterDemand))
        file.write("Delivery lag range: %.2f to %.2f months\n\n" % (inventorySystem.minLag, inventorySystem.maxLag))
        file.write("Length of simulation: %d months\n\n" % (inventorySystem.numMonths))
        file.write("Costs:\n")
        file.write("K = %.2f\n" % (inventorySystem.setupCost))
        file.write("i = %.2f\n" % (inventorySystem.incrementalCost))
        file.write("h = %.2f\n" % (inventorySystem.holdingCost))
        file.write("pi = %.2f\n\n" % (inventorySystem.shortageCost))
        file.write("Number of policies: %d\n\n" % (inventorySystem.numPolicy))
        file.write("Policies:\n")
        file.write("--------------------------------------------------------------------------------------------------\n")
        file.write(" Policy        Avg_total_cost     Avg_ordering_cost      Avg_holding_cost     Avg_shortage_cost\n")
        file.write("--------------------------------------------------------------------------------------------------\n\n")
        

def createInventorySystem(inputFile):
    with inputFile as file:
        line = file.readline()
        initialInventoryLevel, numMonths, numPolicy = map(int, line.split())
        
        line = file.readline()
        numValuesDemand, meanInterDemand = map(float, line.split())
        numValuesDemand = int(numValuesDemand)
        
        line = file.readline()
        setupCost, incrementalCost, holdingCost, shortageCost = map(float, line.split())
        
        line = file.readline()
        minLag, maxLag = map(float, line.split())
        
        line = file.readline()
        probDistribDemand = list(map(float, line.split()))
        
        #insert 0.0 at the beginning of the list
        probDistribDemand.insert(0, 0.0)
        
        policies = []
        for i in range(numPolicy):
            line = file.readline()
            policies.append(list(map(int, line.split())))
            
        # create the inventory system
        inventorySystem = InventorySystem(initialInventoryLevel, numMonths, numPolicy, numValuesDemand, meanInterDemand, setupCost, incrementalCost, holdingCost, shortageCost, minLag, maxLag, probDistribDemand, policies)
        
        return inventorySystem
    
def writeResults(inventorySystem, outputFile):
    with outputFile as file:
        file.write(inventorySystem.report_string)
        file.write("--------------------------------------------------------------------------------------------------")

def main():
    # read the input file and create the inventory system
    infile = open(InputFileName, "r")
    outfile = open(outputFileName, "w")
    inventorySystem = createInventorySystem(infile)
    writeParameters(inventorySystem, outfile)
    inventorySystem.simulate()
    outfile = open(outputFileName, "a")
    writeResults(inventorySystem, outfile)
    
    
if __name__ == "__main__":
    main()