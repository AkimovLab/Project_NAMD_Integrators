import os
import sys
import math
import time
import numpy as np
import h5py

from liblibra_core import *
import util.libutil as comn
from libra_py import units as units
from libra_py import data_conv, data_stat, data_outs, data_read, data_savers

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt

import adi_integrators.recipes


def plots(prefix, imdl, X, Y):
    """
    This function produces nice plots of the ground state populations for all calculations
    """

    plt.rc('axes', titlesize=12)      # fontsize of the axes title
    plt.rc('axes', labelsize=12)      # fontsize of the x and y labels
    plt.rc('legend', fontsize=10)     # legend fontsize
    plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=8)    # fontsize of the tick labels
    plt.rc('figure.subplot', left=0.2)
    plt.rc('figure.subplot', right=0.95)
    plt.rc('figure.subplot', bottom=0.13)
    plt.rc('figure.subplot', top=0.88)
   

    figure = plt.figure(num=imdl, figsize=(3.21, 2.41), dpi=300, edgecolor='black', frameon=True)    

    
    plt.plot(X[imdl, :], Y[imdl, :, 0, 0], color="black", label="reflection on state 0", linewidth=1)
    plt.plot(X[imdl, :], Y[imdl, :, 0, 1], color="blue", label="transmission on state 0", linewidth=1)
    plt.plot(X[imdl, :], Y[imdl, :, 1, 0], color="red", label="reflection on state 1", linewidth=1)
    plt.plot(X[imdl, :], Y[imdl, :, 1, 1], color="green", label="transmission on state 1", linewidth=1)


    
    plt.title("",fontsize=9.5)
    plt.legend(fontsize=6.75, ncol=1, loc='upper left')
    plt.xlabel('Momentum, a.u.',fontsize=10)
    plt.ylabel('Population ',fontsize=10)
    plt.tight_layout()
    plt.savefig(F"{prefix}.png", dpi=300)
    plt.show()                                                                                                            




def get_stats(prefix, mdls, P0, batches, ntraj, methods):

    nmdls = len(mdls)
    npts = len(P0)
    nstates = 2
    nscatt = 2 # scattering channels
  
    X = np.zeros((nmdls, npts), dtype=float)
    Y = np.zeros((nmdls, npts, nstates, nscatt), dtype=float)
    
    cols = list(range(ntraj))

    for method in methods:

        recipe = recipes.recipe_inv_mapping(method)
        rec_name, rec_params = recipes.set_recipe(recipe)
            
        for imdl, mdl in enumerate(mdls): 
        
            for ip0, p0 in enumerate(P0):
        
                X[imdl, ip0] = p0
        
                cnt = 0.0
                for batch in batches:
                    #filename = F"{prefix}{mdl}_{int(p0)}/start_s0_BC_FSSH_batch{batch}"
                    filename = F"{prefix}{mdl}_P0_{p0}_RECIPE_{method}/start_s0_{rec_name}_batch{batch}"
                    states = data_read.get_data_from_file2(F"{filename}/states.txt", cols)
                    coords = data_read.get_data_from_file2(F"{filename}/q.txt", cols)                 
        
                    for itraj in range(ntraj):                
        
                        ist = int(states[itraj][-1])
                        q = coords[itraj][-1]
        
                       
                        if q<-5: # reflection on state ist
                            Y[imdl, ip0, ist, 0 ] += 1 
                            cnt += 1 
        
                        elif q>5: # transmission on state ist
                            Y[imdl, ip0, ist, 1 ] += 1 
                            cnt += 1
        
                print(Y, cnt)
                if cnt > 0:
                    Y[imdl, ip0, :, :] = Y[imdl, ip0, :, :] / cnt
        
                    
            #plots(F"model_{mdl}", imdl, X, Y)
        
            with h5py.File(F"model_{mdl}_method_{method}.hdf", "w") as f:
                #g = f.create_group("data")
                f.create_dataset("X", data = X)
                f.create_dataset("Y", data = Y)


def plot(mdls, methods):

    for method in methods:

        for imdl, mdl in enumerate(mdls):
            with h5py.File(F"model_{mdl}_method_{method}.hdf", "r") as f: 
                print( list(f.keys() ) )
                print(f["X"].shape)
                print(f["Y"].shape)
            
                plots(F"model_{mdl}_method_{method}", imdl, f["X"], f["Y"])
            
def compute_error(x1, model2_path, prop='D_adi', method=0, min_nsteps=1, istate_model1=0, istate_model2=0):
    """
    This funtion computes the accumulation error between two set of coefficients.     
    Args:
        x1 (numpy array): The density of the reference model1 
        model2_path (string): The full path to model 2 hdf file data.
        method (integer): This argument can take two values of 0 and 1.
                              0: The minimum number of steps for time-grid is defined based on the 
                                 shape of model 2 and 1 length.
                              1: The minimum number of steps for time-grid is defined based on the 
                                 min_steps by the user.
        min_nsteps (integer): The minimum number of steps for the time-grid in case method=1 is selected.
        istate_model1 (integer): The initial state of model 1.
        istate_model2 (integer): The initial state of model 2.
    Returns:
        x1 (numpy array): The reference density matrix.
        x1 (numpy array): The second density matrix.
        error (float): The average value of error computed over a set of time-grid points.
    """
    F2 = h5py.File(model2_path)
    x2 = np.array(F2[F'{prop}/data'])
    nsteps1 = x1.shape[0]
    nsteps2 = x2.shape[0]
    if nsteps1 >= nsteps2 and nsteps1%nsteps2==0:
        if method==1:
            coeff2 = int(nsteps2/min_nsteps)
            nsteps2 = min_nsteps
        else:
            coeff2 = 1
        coeff1 = int(nsteps1/nsteps2)
        diff = x1[::coeff1]-x2[::coeff2]
        nsteps = nsteps2
    elif nsteps1 < nsteps2 and nsteps2%nsteps1==0:
        if method==1:
            coeff1 = int(nsteps1/min_nsteps)
            nsteps1 = min_nsteps
        else:
            coeff1 = 1
        coeff2 = int(nsteps2/nsteps1)
        diff = x1[::coeff1]-x2[::coeff2]
        nsteps = nsteps1
    else:
        print('Error! nsteps1 and nsteps2 are not divisible...')
        # Needs to sys.exit(0) as well but I do not do this in Jupyter notebook :)
    diff_squared = np.power(np.abs(diff),2)
    error = np.sum(diff_squared)/nsteps
    F2.close()
        
    return x1, x2, error

   
