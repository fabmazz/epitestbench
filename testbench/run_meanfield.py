#!/usr/bin/env python
# coding: utf-8
# Author: Fabio Mazza

import sys,os
import json
from pathlib import Path


import numpy as np
import pandas as pd

path_script = Path(sys.argv[0]).parent.absolute()
sys.path.append(os.fspath(path_script.parent))

from lib.make_parser import create_data, create_parser, get_versions
from lib.ranker import prepare_contacts

try:
    from statmf import meanfield as smf
except ImportError:
    print("Cannot find statmf, please install the package")
    sys.exit(-1)

def add_arg_parser(parser):

    parser.add_argument('--tau', type=int, default=-1, help="tau")
    parser.add_argument('--delta', type=int, default=-1, help="tau")

    parser.add_argument('--p_source', type=float, default=-1, dest="p_source", help="P source used by sib")


    return parser

if __name__ == "__main__":
    parser = create_parser()
    parser = add_arg_parser(parser)
    args = parser.parse_args()
    print("arguments:")
    print(args)

## ************* set algorithm specific parameters *********** 
    mu = args.mu

    SPARSE_OBS = True
## ************ GENERATE EPIDEMIES ************

    data_, name_file, INSTANCE = create_data(args)
    if data_ == None:
        quit()
    
    confs = np.array(data_["test"])
    #np.save(Path(args.path_dir) / (args.str_name_file+f"_{INSTANCE}_confs.npy"), confs)
    print("We have {} epidemies".format(len(confs)))
    

## ************ RUN INFERENCE ALGORITHMS ************
    

    

    name_file += f"_rk_MF_tr"

    #+1 t_limit times || +1 obs after contacts || +1 for susceptible
    contacts = data_["contacts"]
    #np.savez_compressed(name_file+"_contacts.npz", contacts=contacts)

    N = int(max(contacts[:, 1]) + 1)
    contacts_df = prepare_contacts(contacts)
    #print(contacts_df)
    
    t_limit = INSTANCE.t_limit
    version_scripts = get_versions()

    rng_MF = np.random.RandomState(np.random.PCG64(10))
    loglambs = [smf.contacts_to_csr(
            N,contacts_df[contacts_df.t == t].to_records(index=False),lamb=1.)
         for t in range(t_limit+1)]
    
    for instance_num in range(args.start_conf, args.start_conf+args.num_conf):
        last_obs = data_["test"][instance_num][1]
        real_src = data_["test"][instance_num][0]
        print(f"Instance {instance_num}, Real source:",np.where(real_src)[0][0])
        name_file_instance = name_file + "_" + str(instance_num)

        if not SPARSE_OBS:
            raise ValueError()

            
        else:
            obs_df = data_["observ_df"][instance_num].sort_values("time")
            obser = obs_df.copy()[["node","obs_st","time"]]

            obs_df.to_csv(name_file_instance+"_obs_sparse.csv",index=False)
            print(f"Have {len(obser)} observations")
        all_args = vars(args)
        all_args["versions"] = version_scripts
        with open(name_file_instance+"_args.json","w") as f:
            json.dump(all_args,f, indent=1)

        #obser.time -= 1
        
        if len(obs_df)< 100:
            print(obser.to_records(index=False))

        ## actual code
        obs_mf = smf.prepare_obs(obs_df.to_records(index=False))

        pinf = smf.ranking_backtrack(INSTANCE.t_limit,loglambs,obs_mf, delta=args.delta, tau=args.tau, 
            mu=INSTANCE.mu, rng=rng_MF)
        
        res = np.array([(i,x)for i,x in enumerate(pinf)], dtype=[("idx","i8"),("risk","f8")])
        print(f"Num I: {sum(pinf)}\n Saving")
        
        np.savez_compressed(name_file_instance+"_rank.npz", ranking=res)
