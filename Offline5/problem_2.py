import numpy as np
import matplotlib.pyplot as plt

NUM_SIMULATIONS = 10000

def simulate(n, m, s):
    success = 0
    for _ in range(NUM_SIMULATIONS):  # number of simulations
        # generate rank of candidates
        candidates = np.random.permutation(n) + 1 # add 1 to start from 1
        # find the standard from first m candidates
        standard = min(candidates[:m]) if m > 0 else n + 1
        # find the first candidate that is better than the standard
        sample = candidates[m:]
        selected_candidate = None
        for candidate in sample:
            if candidate < standard:
                selected_candidate = candidate
                break
        # check if the selected candidate is better than s
        if selected_candidate is not None and selected_candidate <= s:
            success += 1
                
    return success / NUM_SIMULATIONS


n = 100
success_criteria = [1, 3, 5, 10]

for s in success_criteria:
    success_rates = [simulate(n, m, s) for m in range(n)]
    # print(success_rates)
    plt.plot(success_rates, label=f's={s}')

plt.xlabel('Sample Size (m)')
plt.ylabel('Success Rate')
plt.legend()
# save the plot
plt.savefig('success_rate.png')
# close the plot
plt.close()
