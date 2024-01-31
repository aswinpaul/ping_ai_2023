# -*- coding: utf-8 -*-

"""
Spyder Editor

This is a temporary script file.
"""

import pongGymEnv as pongEnv

env = pongEnv.CartPoleEnv()
from pong_statetoobs import state_to_obs
env.reset(5000);

import os 
import sys

mtrial = int(sys.argv[1])
print(mtrial)

from pathlib import Path

path = Path(os.getcwd())
module_path = str(path.parent) + '/'
sys.path.append(module_path)

import numpy as np
import random
# agent
from pymdp.utils import random_A_matrix, random_B_matrix, obj_array_uniform, norm_dist_obj_arr
from agents.agent_si_z_learning import si_agent_learnc as si_agent
random.seed(mtrial)
np.random.seed(mtrial);

# generative model of the pong-game environment

# [ self.game_state.ball0.position.x : 4-40,
# self.game_state.ball0.position.y: 8,
# self.game_state.ball0.velocity.y,
# self.game_state.paddle0.position.top.y,
# self.game_state.paddle0.position.bottom.y]

# o1 length: 38
# o2 length: 8
# o3 length: 8

# Generative model

# (Hidden)Factors
# Ball x (Hypothesis)
s1_size = 38
# Ball y (Hypothesis)
s2_size = 8
# Pad (Hypothesis)
s3_size = 8

num_states = [s1_size, s2_size, s3_size]
num_factors = len(num_states)

# Controls
s1_actions = ['Stay', 'Play-Up', 'Play-Down']
s2_actions = ['Do nothing']
s3_actions = ['Do nothing']

num_controls = [len(s1_actions), len(s2_actions), len(s3_actions)]

# Observations
# Ball x (Hypothesis)
o1_size = 38
# Ball y (Hypothesis)
o2_size = 8
# Paddle y (Hypothesis)
o3_size = 8

num_obs = [o1_size, o2_size, o3_size]
num_modalities = len(num_obs)

####

EPS_VAL = 1e-16
A = random_A_matrix(num_obs, num_states)*0 + EPS_VAL

for i in range(s2_size):
    for j in range(s3_size):
        A[0][:,:,i,j] = np.eye(s1_size)
        
for i in range(s1_size):
    for j in range(s3_size):
        A[1][:,i,:,j] = np.eye(s2_size)
        
for i in range(s1_size):
    for j in range(s2_size):
        A[2][:,i,j,:] = np.eye(s3_size)
        
B = random_B_matrix(num_states, num_controls)*0 + EPS_VAL
B = norm_dist_obj_arr(B)

C = obj_array_uniform(num_obs)

D = obj_array_uniform(num_states)

####

EPS_VAL = 1e-16 # Negligibleconstant

#number of pong episodes in a trial
n_trials = 70
        
a = si_agent(A = A,
             B = B,
             C = C,
             D = D,
             planning_horizon = 1,
             action_precision = 1024) 

a.lr_pB = 1e+16

tau_trial = 0
t_length = np.zeros((n_trials, 2))

for trial in range(n_trials):
    
    state = env.reset(mtrial)
    obs_list = state_to_obs(state)

    done = False
    old_reward = 0
    reward = 0
    tau = 0
    a.tau = 0
    
    while(done == False):
        cc = a.C[0]
        cd = a.C[1]
        ce = a.C[2]
        
        # Decision making
        action = a.step(obs_list)
        
        old_reward = reward
        n_state, reward, done, info = env.step(int(action[0]))
        
        # Inference
        prev_obs = obs_list
        obs_list = state_to_obs(n_state)
         
        hit = True if(reward > old_reward) else False
        
        if(hit):
            r = -1
            a.update_c(prev_obs, obs_list, reward = r, terminal = False)
        if(done):
            r = 1
            a.update_c(prev_obs, obs_list, reward = r, terminal = True)
            
        if(reward > 100):
            done = True
            
        tau += 1
        tau_trial += 1
        
    t_length[trial, 0] = reward
    t_length[trial, 1] = tau_trial
    
sep = int(tau_trial/4)
sep_trial = np.argwhere(t_length[:,1] <= sep)[-1][0]      
sep_trial = 1 if sep_trial == 0 else sep_trial

d_1 = t_length[0:sep_trial, 0]
d_2 = t_length[sep_trial:n_trials, 0]

file1 = str('data_n_plot_si/') + str('data_si_1_M1_') + str(mtrial)
file2 = str('data_n_plot_si/') + str('data_si_2_M1_') + str(mtrial)

with open(file1, 'wb') as file:
    np.save(file, d_1)
with open(file2, 'wb') as file:
    np.save(file, d_2)