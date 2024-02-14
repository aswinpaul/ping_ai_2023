 
import numpy as np
import matplotlib.pyplot as plt

data = {}

with open('gamma_cl_1.npy', 'rb') as file:
    data[0] = np.load(file)

with open('gamma_cl_2.npy', 'rb') as file:
    data[1] = np.load(file) 
    
with open('gamma_cl_3.npy', 'rb') as file:
    data[2] = np.load(file) 

with open('gamma_cl_4.npy', 'rb') as file:
    data[3] = np.load(file) 
    
agents = 4
episodes = 69

sample = np.shape(data[0][:,0:episodes][0])[0]

data_mean = {}  
for i in range(agents):
    data_mean[i] = np.mean(np.transpose(data[i][:,0:episodes]), axis=1)
    plt.plot(range(sample-1),data_mean[i][:-1])

data_std = {}    
for i in range(agents):
    fact = 1
    data_std[i] = np.std(np.transpose(data[i][:,0:episodes]), axis=1)
    plt.fill_between(range(sample-1), 
                     data_mean[i][:-1] + fact*data_std[i][:-1],
                     data_mean[i][:-1] - fact*data_std[i][:-1],
                     alpha=0.3)

plt.legend(["CL agent (T=1)","CL agent (T=2)","CL agent (T=3)", "CL agent (T=4)"])

plt.title("Risk term in CL method")

plt.xlabel("Episode number")
plt.ylim(0, 1.01)
plt.xlim(0, episodes)
plt.ylabel("Risk term in CL method (Gamma)")
plt.savefig('cp_gamma.png', dpi=500, bbox_inches='tight');