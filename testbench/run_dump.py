#!/usr/bin/env python
# coding: utf-8

import sys
import os
import json
import time
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

#path_script = Path(sys.argv[0]).parent.absolute()
#sys.path.append(os.fspath(path_script.parent/"src"))

from epitestlib.make_parser import create_parser, create_data, get_versions

try:
    import sib
except ImportError:
    print("sib is not installed. Install from https://github.com/sibyl-team/sib")
    sys.exit(1)

def make_callback(converged, eps_conv, damp):
    dstring = f"damp {damp}"
    def callback_print(t,err,f):
        print(dstring+f" : {t:6}, err: {err:.5e} ", end="\r")
        #-- iter_params: {ii} -- lambda: {params_sib.prob_i.theta[0]:.3} -- mu: {float(params_sib.prob_r.mu):.3}", end="\r")
        if err < eps_conv:
            converged[0] = True
    return callback_print

def marginals_all(fg,T):
    N = len(fg.nodes)
    margs = [] #p.empty((T,N,3))
    for n in fg.nodes:
        margs.append(n.marginal())
    margs= np.array(margs)
    assert margs.shape == (N,T,3)
    return margs

def add_arg_parser(parser):
    # sib options
    """
    parser.add_argument('--p_source', type=float, default=-1, dest="p_source", help="p_source")
    parser.add_argument('--p_sus', type=float, default=0.5, dest="p_sus", help="p_sus")
    parser.add_argument('--maxit', type=int, default=1000, dest="maxit", help="maxit")
    #parser.add_argument('--t_obs', type=int, default=0, dest="t_obs", help="time to compute marginals")
    parser.add_argument('--lr_param', type=float, default=0, dest="lr_param", help="learning rate params")
    parser.add_argument('--iter_learn', type=int, default=1, dest="iter_learn", help="Number of iterations of learning of parameters")
    #parser.add_argument('--lr_gamma',  action="store_true", help="learning rate of infection instead of probability of the propagation model [gamma]")
    parser.add_argument("--nthreads", type=int, default=-1, dest="num_threads",
        help="Number of threads to run sib with")
    parser.add_argument("--sib_tol", type=float, default=1e-3, help="Sib tolerance in convergence")
    parser.add_argument("--prior_test", action="store_true", help="Put prior as fake tests on unobserved nodes")
    parser.add_argument("--avg_m_steps", type=int, default=-1, help="Number of steps to do for average")
    """

    return parser



def _run(parse_args=None):
    parser = create_parser()
    parser = add_arg_parser(parser)
    args = parser.parse_args(args=parse_args)
    print("arguments:")
    print(args)


## ************ GENERATE EPIDEMIES ************

    data_, name_file, INSTANCE = create_data(args)
    if data_ == None:
        quit()

    #direc = Path("problem_data")
    #if not direc.exists():
    #    direc.mkdir(parents=True)
    #direc = direc.absolute()
    #print(direc.absolute())
    
    confs = np.array(data_["test"])
    contacts = data_["contacts"]
    observations = data_["observ_df"]

    #np.save(Path(args.path_dir) / (args.str_name_file+f"_{INSTANCE}_confs.npy"), confs)
    print("We have {} epidemies".format(len(confs)))
    print("CONFS: ",confs, "dtype ",type(confs))

    print("Contacts_dtype ",type(contacts))

    print("Observs: ",observations[0])

    name_file_instance = lambda i: f"{name_file}_{i}" #name_file + "_" + str(i)

    print(f"NAME FILE: {name_file}")
    for i, obs_df in enumerate(observations):
        ff=(name_file_instance(i)+"_obs_sparse.csv")
        obs_df.to_csv(ff,index=False)
    
    ff = f"{name_file}_confs.npy"
    np.save(ff, confs)

    ff = f"{name_file}_contacts.npy"
    np.save(ff, contacts)

    print("SAVED")
    #confs_d = {i: }
    #np.savez_compressed(ff,**{i:})

if __name__ == "__main__":
    _run()

