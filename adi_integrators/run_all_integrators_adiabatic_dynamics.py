import os
import sys
from itertools import product
from recipes import submit_jobs
import time

#============================== Set 1, 
models = [0,1,2,3]
#======= Initial conditions, Both coords and momenta are sampled, istate=[1,0]
iconds = [6]
#======= Different integration schemes for TDSE and Liouville
reps    = [2]#,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25] 
#======= TSH or Ehrenfest
tsh_ehr = [0,2]
#======= No surface hopping
sh_opt = [0]
#======= No decoherence
deco_opt = [0]
#======= Decoherence time option
deco_time_opt = [0]
#======= E+
hop_acc = [0]
#======= NAC calculations type, Explicit
nac_update = [0]
#======= SSY correction
ssy = [0]
# Make the recipes as below so that we can feed through Python arg parser
recipes = list(product(models, iconds, reps, tsh_ehr, sh_opt, deco_opt, deco_time_opt, hop_acc, nac_update, ssy)) 
# Adding case 22, Zhu's method, Eqs. 3.34-3.35 with TSH only
#for model in models:
#    recipes.append((model,2,22,0,0,0,0,0,0,0))
print(len(recipes))
print(recipes)
#======= With only 1 trajectory
for dt in [200.0, 100.0, 80.0, 50.0, 40.0, 20.0, 10.0, 8.0, 5.0, 4.0, 2.0, 1.0, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]:
    nsteps = int(25000/dt)
    submit_jobs('submit.slm', 'run_namd_2states_models.py', recipes, dt=dt, nsteps=nsteps, ntraj=1)
    time.sleep(10.0)

