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

    return parser

if __name__ == "__main__":
    parser = create_parser()
    parser = add_arg_parser(parser)
    args = parser.parse_args()
    print("arguments:")
    print(args)


## ************ GENERATE EPIDEMIES ************

    data_, name_file, INSTANCE = create_data(args)
    if data_ == None:
        quit()
    
    confs = np.array(data_["test"])
    #np.save(Path(args.path_dir) / (args.str_name_file+f"_{INSTANCE}_confs.npy"), confs)
    print("We have {} epidemies".format(len(confs)))
## ************* set algorithm specific parameters *********** 
    mu = args.mu
    p_source = args.p_source
    p_sus = args.p_sus
    if p_source < 0:
        p_source = INSTANCE.n_src/args.N
        print("Fix p_source to:", p_source)
    
    prob_seed = p_source / (2 - p_source)
    p_sus = p_sus * (1-prob_seed)


    print("sib version",sib.version())

## ************ RUN INFERENCE ALGORITHMS ************

    
    if args.num_threads > 0:
        ## set number of cores to use with sib
        sib.set_num_threads(args.num_threads)

    #+1 t_limit times || +1 obs after contacts || +1 for susceptible
    contacts = data_["contacts"]
    N = int(max(contacts[:, 1]) + 1)
    ## set no learning of parameters
    LR_PAR = 0
    if LR_PAR == 0:
        contacts = [(int(i),int(j),int(t),l) for t,i,j,l in contacts] #Setting lambda values in Params
        lambda_ = 1. - 1e-6
        mu = args.mu
        if mu==0.: # sib has issues with mu = 0
            mu+=1e-10
    else:
        contacts = [(int(i),int(j),int(t),1. - 1e-6) for t,i,j,l in contacts] #Setting lambda values in Params
        lambda_ = args.lambda_init_param
        mu = args.mu_init_param
        
    t_limit = INSTANCE.t_limit
    mu_rate = -np.log(1-mu)
    learn = LR_PAR > 0
    VERSIONS = get_versions()
    VERSIONS["sib"] = sib.version().split("(")[0].strip()
    lambdas=[]
    mus=[]
    convergence_all=[]
    end_conf_last = args.start_conf+args.num_conf
    range_confs = range(args.start_conf, args.start_conf+args.num_conf)
    for instance_num in range_confs:
        print(f"Instance {instance_num}")
        last_obs = data_["test"][instance_num][1]
        real_src = data_["test"][instance_num][0]
        print("Real source:",np.where(real_src)[0])
        name_file_instance = name_file + "_" + str(instance_num)

        if not args.sparse_obs:
            obs_list = []
            for tt in range(t_limit+1):
                obs_list.extend([(i,-1,tt) for i in range(N)])
            for i, s in enumerate(last_obs):
                obs_list.append([i,s,t_limit])
            
        else:
            obs_df = data_["observ_df"][instance_num]
            
            obs_list = obs_df[["node","obs_st","time",]].to_records(index=False)
            print("NUM OBS: ", len(obs_list))
            print(obs_list)
            obs_init_list =[(i,-1,t) for t in range(t_limit+1) for i in range(N) ]
            obs_init_list.extend(obs_list)
            
            nodes_obs = set(obs_df["node"])
            unobserved = set(range(N)).difference(nodes_obs)

            if args.prior_test:
                print(f" {len(unobserved)} unobserved nodes")
                for node in unobserved:
                    obs_init_list.append((node, sib.Test(ps=1, pi=0.5, pr=1), t_limit))
            #print(obs_list)
            #print(json.dumps(data_["observ_dict"][instance_num],), )
            obs_df.to_csv(name_file_instance+"_obs_sparse.csv",index=False)
            obs_list = obs_init_list
        
        obs_list.sort(key=lambda tup: tup[2])
        

        if  LR_PAR > 10:
            print("***** CHECK if sib is in right branch ******")
            params_sib = sib.Params(prob_r = sib.Exponential(mu=mu_rate), 
                        prob_i = sib.ConstantRate(gamma=lambda_),
                        pseed=prob_seed,
                        psus= p_sus)
            contacts = data_["deltas"]
            contacts = [(int(i),int(j),int(t),l) for t,i,j,l in contacts]
        else:
            params_sib = sib.Params(prob_r = sib.Exponential(mu=mu_rate), 
                                    prob_i = sib.Uniform(p=lambda_),
                                    pseed=prob_seed, 
                                    psus=p_sus)
        tol=args.sib_tol
        conver = [False]
        f = sib.FactorGraph(params=params_sib, 
                            contacts = contacts, 
                            observations = obs_list)
        
        tstart = time.time()
        for ii in range(args.iter_learn):
            
            sib.iterate(f, maxit=args.maxit, tol=tol,
                        callback=make_callback(conver, tol,0.), learn=learn)
            #print(f"\nConverged: {conver[0]}")
            print("")
            sib.iterate(f, maxit=args.maxit, damping=0.5,
                        tol=tol,
                        callback=make_callback(conver, tol,0.5), learn=learn)
            #print(f"\nConverged: {conver[0]}")
            print("")
            sib.iterate(f, maxit=args.maxit, damping=0.95,
                        tol=tol,
                        callback=make_callback(conver, tol,0.95), learn=learn)
            print(f"\nConverged: {conver[0]}")
            '''
            if args.lr_param > 0:
                
                lr_i = args.lr_param/100 if args.lr_gamma else args.lr_param
                if ii/args.iter_learn > 0.8:
                    lr_i /= 100
                lr_r = args.lr_param
                dfr=0
                dfi=0
                for n in f.nodes:
                    dfr += n.df_r[0]
                    dfi += n.df_i[0]
                params_sib.prob_i.theta[0] += dfi*lr_i
                params_sib.prob_i.theta[0] = min(max(1e-6, params_sib.prob_i.theta[0]), 1-1e-6)
                params_sib.prob_r.theta[0] += dfr*lr_r
                params_sib.prob_r.mu = max(1e-6, params_sib.prob_r.mu)
                lambdas.append(float(params_sib.prob_i.theta[0]))
                mus.append(float(params_sib.prob_r.mu))
            '''
        avg_margs = None
        if conver[0] == False and args.avg_m_step > 0:
            maxit = args.avg_m_step
            sum_av = None
            counts = 0
            print("Save avg marginals")
            for t in range(maxit):
                err= f.update(damping=0.8, learn=learn)
                print(f"Err:  : {t:6}, err: {err:.5e} ", end="\r")
                if err < tol:
                    conver[0] = True
                    sum_av = None
                    break
                if sum_av is None:
                    sum_av =  marginals_all(f, t_limit+1)
                else:
                    sum_av += marginals_all(f, t_limit+1)
                counts += 1
            
            avg_margs = sum_av/counts

        tend = time.time()
        all_args = vars(args)
        #all_args["sib_version"] = sib.version()
        all_args["versions"] = VERSIONS
        all_args["sib_convergence"] = conver[0]
        all_args["converge_time"] = round(tend-tstart, 3)
        with open(name_file_instance+"_args.json","w") as mfile:
            json.dump(all_args,mfile, indent=1)
        
        convergence_all.append(conver[0])
        
        sources_sib = sib.marginals_t(f,0)
        sources_sib = np.array([(k,sources_sib[k][0], 
                                 sources_sib[k][1], 
                                 sources_sib[k][2]) for k in sources_sib])
        print(f"S: {sources_sib[:,1].sum()}, I: {sources_sib[:,2].sum()}, R: {sources_sib[:,3].sum()}")

        M = np.zeros((N, t_limit+1, 3), dtype=float)
        for t in range(0,t_limit+1):
            MM = sib.marginals_t(f,t)
            for n in MM:
                M[n,t] = MM[n]
        array_save = {"marginals": M}
        ## AVERAGE MARGINALS
        avg_margs = None
        if conver[0] == False and args.avg_m_steps > 0:
            maxit = args.avg_m_steps
            sum_av = None
            counts = 0
            print("Get avg marginals")
            for t in range(maxit):
                err= f.update(damping=0.8, learn=learn)
                print(f"Err:  : {t:6}, err: {err:.5e} ", end="\r")
                if err < tol:
                    conver[0] = True
                    sum_av = None
                    break
                if sum_av is None:
                    sum_av =  marginals_all(f, t_limit+1)
                else:
                    sum_av += marginals_all(f, t_limit+1)
                counts += 1
            print("")
            if sum_av is not None:
                avg_margs = sum_av/counts

        if avg_margs is not None:
            print("Save avg margs")
        if avg_margs is not None:
            array_save["margs_avg"] = avg_margs
        np.savez_compressed(name_file_instance+"_sib_margs.npz", **array_save)
        #pd.DataFrame(data={"lambda":lambdas, "mu":mus}).to_csv(name_file_instance+"_params.gz")

    print("\nSib convergence: \n", pd.Series(convergence_all, index=range_confs))