import os
import sys
import h5py
import numpy as np
import time
import matplotlib.pyplot as plt
from libra_py import units
from adi_integrators.recipes import set_recipe_v2
from analysis import compute_error 


# ================================== Computing all the errors for model 1 to 4, all dts, and all cases
all_errors = []
dts = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 50.0, 100.0, 200.0]#, 500.0, 1000.0]
for model in [0,1,2,3]:
    # set up a timer
    t1 = time.time()
    # Define the reference density, this density is obtained from adiabatic initialization and diabatic integration using TSH
    reference_rho = F'adi_integrators/test_model_{model}_icond_6_case_2_tsh__noSH__noDeco__infDecoTime__E+__expplicit__noSSY_dt_0.001_nsteps_25000000/mem_data.hdf'
    # Since reading this large file is time consuming (takes about 16 seconds to load), we only read this once and feed
    # the density matrix, x1, to the error function. This increases the speed of the calculations.
    F1 = h5py.File(reference_rho)
    x1 = np.array(F1['D_adi/data'])
    F1.close()
    # The errors of this model
    model_errors = []
    # For each dt in the calculations
    for dt in dts:
        # Some printing to follow the calculations procedure 
        print(model, dt)
        # Define the number of steps in each calculations
        nsteps = int(25000/dt)
        # Now, for this dt and nsteps, we start computing the errors with respect to the reference density matrix
        errors_dt = []
        for case in [9,10,11,12,13,14,15,16,17,18,19,20,21]:
            # The recipe would change for only "model" and "case"
            recipe = ((model,6,case,0,0,0,0,0,0,0))
            # Now, let's generate the name of the folder in which the data are present for this recipe and dt
            # We feed an empty dictionary and ignore the returned values by set_recipe_v2 {}
            _, _, _, _, name = set_recipe_v2({}, recipe, "test")
            name += F'_dt_{dt}_nsteps_{nsteps}'
            # The name of the model2_path 
            model2_path = F'adi_integrators/{name}/mem_data.hdf'
            x1, x2, error = compute_error(x1, model2_path, prop='D_adi', method=1, min_nsteps=125)
            # Appending this case error
            errors_dt.append(error)
        # Appending the errors for all cases and this dt value
        model_errors.append(errors_dt)
    # Appending this model error for all cases and dt values
    all_errors.append(model_errors)
    print(time.time()-t1)
all_errors = np.array(all_errors)

# Save the errors computed by far
np.save('all_errors_method_1.npy', all_errors) 


# ================================== Plotting the errors

dts = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 50.0, 100.0, 200.0]
#labels = ['LD, crude with exp','LD, symmetric splitting with exp',
#           'LD, original with exp','1-point integration, with exp','2-points integration, with exp',
#           '3-points integration, with exp','LD, crude with rotations','LD, symmetric splitting with rotations',
#           'LD, original with rotations','1-point integration with rotations','2-points integration with rotations',
#           '3-points integration with rotations','Lowdin method, mid-point integration']

#titles = ['Local diabatization approach with exp', 'n-points integration with exp', 
#         'Local diabatization approach with rotations', 'n-points integration with rotation', 
#         'Lowdin method, mid-point integration']

methods = [[0,1,2],[3,4,5],[6,7,8],[9,10,11],[12]]
for c, method in enumerate(methods):
    for c1, model in enumerate([0,1,2,3]):
        plt.figure(figsize=(3.21*1.4, 2.41*1.4), dpi=600, edgecolor='black', frameon=True)
        plt.clf()
        title = titles[c] 
        for i in method: 
            plt.plot(dts, all_errors[model,:,i], marker='s', ls='--', label=labels[i])
        plt.title(F'Model {model+1}')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('$\Delta$t, a.u.')
        plt.ylabel('Error, a.u.')
        # plt.ylim(1e-30,100)
        if c1==0:
            plt.legend()
        plt.tight_layout()
        plt.savefig(F'Model_{model+1}_{title}_density_error_analysis_log_plot.jpg', dpi=600)
        plt.close()

# ================================== Plotting the density and total energy vs time

prop = 'D_adi'
dts = [0.01, 0.1, 1.0, 10.0, 50.0, 100.0]
for model in [0,1,2,3]:#= 1
    print(model)
    cases = [9,10,11,12,13,14,15,16,17,18,19,20]
    
    labels = ['LD, crude with exp','LD, symmetric splitting with exp',
               'LD, original with exp','1-point integration, with exp','2-points integration, with exp',
               '3-points integration, with exp','LD, crude with rotations','LD, symmetric splitting with rotations',
               'LD, original with rotations','1-point integration with rotations','2-points integration with rotations',
               '3-points integration with rotations','Lowdin method, mid-point integration']
    
    reference_rho = F'adi_integrators/test_model_{model}_icond_6_case_2_tsh__noSH__noDeco__infDecoTime__E+__expplicit__noSSY_dt_0.001_nsteps_25000000/mem_data.hdf'
    cases_1 = [[9,10,11],[12,13,14],[15,16,17],[18,19,20]] 
    c1 = 0
    for i in range(len(cases_1)): 
        cases = cases_1[i]
        plt.figure(figsize=(3.21*3, 2.41*1.0), dpi=600, edgecolor='black', frameon=True)
        F1 = h5py.File(reference_rho)
        x1 = np.abs(np.array(F1[F'{prop}/data']).real)
        time1 = np.array(F1['time/data'])
        F1.close()
        
        for c, case in enumerate(cases):
            plt.subplot(1,3,c+1)
            plt.plot(time1, x1, ls='-', lw=2.0, label='0.001')
            print(case)
            for dt in dts:
                nsteps = int(25000/dt)
                recipe = ((model,6,case,0,0,0,0,0,0,0))
                _, _, _, _, name = set_recipe_v2({}, recipe, "test")
                name += F'_dt_{dt}_nsteps_{nsteps}'
                F2 = h5py.File('adi_integrators/'+name+'/mem_data.hdf')
                if prop=='D_adi':
                    x2 = np.abs(np.array(F2[F'{prop}/data']).real)[:,0,0]
                    #x2 = np.abs(np.array(F2[F'{prop}/data']).real)[:,0,1]
                elif prop=='Etot_ave':
                    x2 = np.abs(np.array(F2[F'{prop}/data']).real)
                time2 = np.array(F2['time/data'])
                F2.close()
                plt.plot(time2, x2, ls='--', label=F'{dt}', lw=1.0)
            if c1==0:
                plt.legend(loc='upper right')
            #plt.ylim(-0.08,1.1)
            if c%3==0:
                if prop=='D_adi':
                    plt.ylabel('Population of 0$^{th}$ state')
                    #plt.ylabel('|Coherence|, a.u.')
                elif prop=='Etot_ave':
                    plt.ylabel('Total energy, a.u.')
            else:
                plt.yticks([]) 
            plt.xlim(0,25000)
            plt.xlabel('Time, a.u.') 
            plt.title(labels[c1])
            c1 += 1
        plt.tight_layout()
        if prop=='D_adi':
            plt.savefig(F'Model_{model}_density_{i}.jpg', dpi=600)
            #plt.savefig(F'Model_{model}_coherence_{i}.jpg', dpi=600)
        elif prop=='Etot_ave':
            plt.savefig(F'Model_{model}_total_energy_{i}.jpg', dpi=600)
        plt.close()


