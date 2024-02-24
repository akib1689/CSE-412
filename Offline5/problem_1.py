import numpy as np

SIM_NUM = 100000

def format_result(probabilities):
    """Format the result of the simulation
    Args:
        probabilities: 2D array of probabilities
    Returns:
        A string with the formatted result
    """
    result = ''
    for i in range(probabilities.shape[0]):
        result += f'Generation-{i+1}:\n'
        for j in range(probabilities.shape[1]):
            result += f'P({j}) = {probabilities[i][j]}\n'
        result += '\n'
        
    return result
    


# define the probabilities
p = [0.2126 * (0.5893)**(i-1) for i in range(4)]
p = [1 - sum(p[1:])] + p[1:]  # Adjust for p0

# initialize the result of the simulation
result = np.zeros((10, 5, SIM_NUM))

# run the simulation
for sim in range(SIM_NUM):
    neutrons = 1
    for gen in range(10):
        new_neutrons = 0
        for _ in range(neutrons):
            # determine the number of new neutrons
            r = np.random.rand()
            for i in range(4):
                if r < sum(p[:i+1]):
                    new_neutrons += i
                    break
            
        # update the number of neutrons
        neutrons = new_neutrons
        if neutrons < 4:
            result[gen, neutrons, sim] = 1
        else:
            result[gen, 4, sim] = 1
            
# calculate the probability of extinction
prob = result.mean(axis=2)

result = format_result(prob)
print(result)