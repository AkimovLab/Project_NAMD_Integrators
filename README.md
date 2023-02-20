# Project_NAMD_Integrators

This repository contains all the Python files that uses different integrators to solve the time-dependent Schrodinger equation (TD-SE)
and the quantum-classical Liouville's equations (QCLE). We use the `tsh_revision` branch of the [Libra code](https://github.com/Quantum-Dynamics-Hub/libra-code/tree/tsh_revision). 


The calculations here are run for a set of standard nonadiabatic model problems where different types of integrators with different timesteps 
are used to solve the TD-SE. We first setup all these integrators in form of multiple recipes where detailed information are brought in the `adi_integrators/recipes.py` file.
The calculations are run systematically for a set of parameters in the `adi_integrators/run_all_integrators_adiabatic_dynamics.py` file as follows:

`model`: This parameter takes the values of `0`, `1`, `2`, and `3`. Each of the models are defined in the `model_params` in the `set_recipe_v2` function.

`icond`: The initial condition for position and momentum. 

`reps`: This parameter defines the representation where integrators are defined. Different integrators cases are defined in this function.

`tsh_ehr`: This parameter is what we use for computing the forces derived from the adiabatic surfaces.

`sh_opt`: This parameter defines the surface hopping option such as FSSH, GFSH, etc. Since we do the dynamics only for the adiabatic case here we set it to `0`.

`deco_opt`: This parameter defines the decoherence option such as ID-A, mSDM, etc. Since we do the dynamics in the adiabatic case we set it to `0`.

`deco_time_opt`: This parameter defines how to compute the decoherence time.

`hop_acc`: This parameter is used for hop acceptance algorithm which is used when we perform surface hopping.

`nac_update`: This parameter is used for how to compute the nonadiabatic couplings where multiple options are available such as explicit method, NPI, and HST.

`ssy`: This parameter is used for applying nuclear phase correction by Shenvi, Subotnik, and Yang.


The calculations are run simultaneously for a set of recipes using:

```
# Make the recipes as below so that we can feed through Python arg parser
recipes = list(product(models, iconds, reps, tsh_ehr, sh_opt, deco_opt, deco_time_opt, hop_acc, nac_update, ssy))
#======= With only 1 trajectory
for dt in [200.0, 100.0, 80.0, 50.0, 40.0, 20.0, 10.0, 8.0, 5.0, 4.0, 2.0, 1.0, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]:
    nsteps = int(25000/dt)
    submit_jobs('submit.slm', 'run_namd_2states_models.py', recipes, dt=dt, nsteps=nsteps, ntraj=1)
```


In the above part, we pass the name of the submit file and the Python script used to run the calculations. The calculations in the submit file are
run through `argparser` for efficient submission and without regenerating new Python files. The set of parameters are passed thorugh the `argparser` and in the `run_namd_2states_models.py`
these parameters are parsed and passed to the main function `tsh_dynamics.generic_recipe`. 








