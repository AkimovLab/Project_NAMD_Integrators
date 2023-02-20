import sys
import cmath
import math
import os
import h5py
import matplotlib.pyplot as plt   # plots
import numpy as np
import scipy.sparse as sp
import time
import warnings

from liblibra_core import *
import util.libutil as comn
from libra_py import units
import libra_py.models.Holstein as Holstein
import libra_py.models.Morse as Morse
from libra_py import dynamics_plotting
import libra_py.dynamics.tsh.compute as tsh_dynamics
import libra_py.dynamics.tsh.plot as tsh_dynamics_plot

import libra_py.dynamics.exact.compute as dvr
import libra_py.dynamics.exact.save as dvr_save

import libra_py.data_savers as data_savers
from recipes import *
import argparse

#from matplotlib.mlab import griddata
#%matplotlib inline 
warnings.filterwarnings('ignore')

colors = {}
colors.update({"11": "#8b1a0e"})  # red       
colors.update({"12": "#FF4500"})  # orangered 
colors.update({"13": "#B22222"})  # firebrick 
colors.update({"14": "#DC143C"})  # crimson   
colors.update({"21": "#5e9c36"})  # green
colors.update({"22": "#006400"})  # darkgreen  
colors.update({"23": "#228B22"})  # forestgreen
colors.update({"24": "#808000"})  # olive      
colors.update({"31": "#8A2BE2"})  # blueviolet
colors.update({"32": "#00008B"})  # darkblue  
colors.update({"41": "#2F4F4F"})  # darkslategray

clrs_index = ["11", "21", "31", "41", "12", "22", "32", "13","23", "14", "24"]

def compute_model(q, params, full_id):

    model = params["model"]
    res = None
    
    if model==1:        
        res = Holstein.Holstein2(q, params, full_id) 
    elif model==2:
        pass #res = compute_model_nbra(q, params, full_id)
    elif model==3:
        pass #res = compute_model_nbra_files(q, params, full_id)        
    elif model==4:
        res = Morse.general(q, params, full_id)    

    return res

def potential(q, params):
    full_id = Py2Cpp_int([0,0]) 
    
    return compute_model(q, params, full_id)


#================================= Set up dynamics parameters

parser = argparse.ArgumentParser(description='Runs excited states dynamics with different methodologies using Libra...')
parser.add_argument('--recipe', default='0500100000', type=str)
parser.add_argument('--ntraj', default=10, type=int)
parser.add_argument('--nsteps', default=2500, type=int)
parser.add_argument('--dt', default=10.0, type=float)
args = parser.parse_args()

# Adopted from https://stackoverflow.com/questions/21270320/turn-a-single-number-into-single-digits-python

recipes = args.recipe
recipe = [int(d) for d in recipes.split(',')]

### A ten element list
##recipe = [  0, # Model
##            2, # Initial condition
##            0, # Case
##            0, # Ehrenfest or TSH
##            1, # SH opt
##            4, # Decoherence option
##            2, # Decoherence times option
##            0, # Hop acceptance method
##            0, # NAC calculations
##            0] # SSY

ntraj = args.ntraj
dt = args.dt
nsteps = args.nsteps
# Decohrerence rates and average gaps matrices initialization
decoherence_rates = MATRIX(2,2)
ave_gaps = MATRIX(2,2)
# Set up dyn_general
dyn_general = { "nsteps": nsteps, "ntraj": ntraj, "nstates":2,
                "dt": dt, "num_electronic_substeps":1, "isNBRA":0, "is_nbra":0, 
                "ham_update_method":1, "ham_transform_method":1,
                "time_overlap_method":1,
                "hvib_update_method":1,
                "force_method":1, "rep_force":1,
                "dephasing_informed":0, "decoherence_rates":decoherence_rates, "ave_gaps":ave_gaps,               
                "progress_frequency":1.0, "which_adi_states":range(2), "which_dia_states":range(2),                
                "mem_output_level":3,
                "properties_to_save":[ "timestep", "time", "q", "p", "Etot_ave", "se_pop_adi", "se_pop_dia", "sh_pop_adi", "Cadi", "D_adi" ],
                "prefix":"adiabatic_md", "prefix2":"adiabatic_md"
              }

rnd = Random()

dyn_general, elec_params, nucl_params, model_params, name = set_recipe_v2(dyn_general, recipe, name="test")
name = F"{name}_dt_{dt}_nsteps_{nsteps}"
dyn_general.update({ "prefix":name, "prefix2":name })


try:
    res = tsh_dynamics.generic_recipe(dyn_general, compute_model, model_params, elec_params, nucl_params, rnd)
except:
    print('Error Flag: The TSH run could not be done with the following recipe:', recipe)

    
