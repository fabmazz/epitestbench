#!/usr/bin/env python
# coding: utf-8
# Author: Fabio Mazza

import sys,os
import json
from pathlib import Path
from collections import namedtuple


import numpy as np
import pandas as pd

path_script = Path(sys.argv[0]).parent.absolute()
sys.path.append(os.fspath(path_script.parent))

from epitestlib.make_parser import create_data, create_parser, get_versions



def add_arg_parser(parser):
    parser.add_argument("--ranker", type=str, help="Name of the ranker to use")
    parser.add_argument("--epi_mit_path", type=str, default=".",help="Path for the epidemic_mitigation repository")
    parser.add_argument('--tau', type=int, default=-1, help="tau")
    parser.add_argument('--delta', type=int, default=-1, help="tau")

    parser.add_argument('--p_source', type=float, default=-1, dest="p_source", help="P source used by sib")
    parser.add_argument('--p_sus', type=float, default=0.5, dest="p_sus", help="P sus used by sib")
    parser.add_argument('--sib_maxit', type=int, default=1000, help="Max iterations of sib")
   
    parser.add_argument("--nthreads", type=int, default=-1, dest="num_threads",
        help="Number of threads to run sib with")

    return parser

def prepare_contacts(conts):
    t_limit = int(conts[:,0].max())+1
    conts_df = pd.DataFrame(conts[:,:3].astype(int), columns=["t","i","j"], dtype=int)
    conts_df["lam"]=conts[:,3]
    ## add fake contact for the last time
    r1 = conts_df.iloc[1].to_dict()
    r1["t"] = t_limit
    r1["lam"] = 0.
    conts_all = conts_df.append(r1,ignore_index=True)

    conts_all = conts_all[["i","j","t", "lam"]]
    return conts_all.convert_dtypes(convert_integer=True)

if __name__ == "__main__":
    parser = create_parser()
    parser = add_arg_parser(parser)
    args = parser.parse_args()
    print("arguments:")
    print(args)

## ************* set algorithm specific parameters *********** 
    mu = args.mu

    SPARSE_OBS = True
    Dummy = namedtuple("dummy", ["info"])

    epid_mit_f = Path(args.epi_mit_path)
    srcfolder= epid_mit_f / "src"
    print(srcfolder.resolve().as_posix())
    sys.path.append(srcfolder.as_posix()+"/")
## ************ GENERATE EPIDEMIES ************

    data_, name_file, INSTANCE = create_data(args)
    if data_ == None:
        quit()
    
    confs = np.array(data_["test"])
    #np.save(Path(args.path_dir) / (args.str_name_file+f"_{INSTANCE}_confs.npy"), confs)
    print("We have {} epidemies".format(len(confs)))
    

## ************ RUN INFERENCE ALGORITHMS ************
    if args.ranker == "MF":
        from rankers import mean_field_rank
        if args.tau < 0 or args.delta < 0:
            raise ValueError("Input delta and tau")
        ranker = mean_field_rank.MeanFieldRanker(
                tau = args.tau,
                delta = args.delta,
                mu = INSTANCE.mu,
                lamb = 1.,
                )
        print("Using MeanFieldRanker")
    elif args.ranker == "CT":
        from rankers import tracing_rank
        if args.tau < 0:
            raise ValueError("Input tau")
        ranker = tracing_rank.TracingRanker(
            tau=args.tau, lamb=1.)
        print("Using TracingRanker")
    elif args.ranker == "BP":
        from rankers import sib_rank


        p_source = args.p_source
        p_sus = args.p_sus

        if p_source < 0:
            p_source = 1/INSTANCE.n

        prob_seed = p_source / (2 - p_source)
        mu_rate = -np.log(1-INSTANCE.mu)
        sib = sib_rank.sib
        if args.num_threads > 0:
            ## set number of cores to use with sib
            sib.set_num_threads(args.num_threads)

        params_sib = sib.Params(prob_r = sib.Exponential(mu=mu_rate), 
                                    prob_i = sib.Uniform(p=1.),
                                    pseed=prob_seed,
                                    psus=p_sus)
        ranker = sib_rank.SibRanker(params=params_sib,
                        maxit0=args.sib_maxit,
                        maxit1 =args.sib_maxit,
                        window_length=(INSTANCE.t_limit + 1),
                        print_callback= lambda t, err: print("\r", t, err,end=""))
        print("Using SibRanker")
    else:
        raise ValueError("Unrecognized ranker")

    

    name_file += f"_rk_{args.ranker}"

    #+1 t_limit times || +1 obs after contacts || +1 for susceptible
    contacts = data_["contacts"]
    #np.savez_compressed(name_file+"_contacts.npz", contacts=contacts)

    N = int(max(contacts[:, 1]) + 1)
    contacts_df = prepare_contacts(contacts)
    #print(contacts_df)
    print(contacts_df.i.dtype)
        
    t_limit = INSTANCE.t_limit
    version_scripts = get_versions()
    
    for instance_num in range(args.start_conf, args.start_conf+args.num_conf):
        last_obs = data_["test"][instance_num][1]
        real_src = data_["test"][instance_num][0]
        print(f"Instance {instance_num}, Real source:",np.where(real_src)[0][0])
        name_file_instance = name_file + "_" + str(instance_num)

        if not SPARSE_OBS:
            raise ValueError()

            
        else:
            obs_df = data_["observ_df"][instance_num]
            obser = obs_df.copy()[["node","obs_st","time"]]

            obs_df.to_csv(name_file_instance+"_obs_sparse.csv",index=False)
            print(f"Have {len(obser)} observations")
        all_args = vars(args)
        all_args["versions"] = version_scripts
        with open(name_file_instance+"_args.json","w") as f:
            json.dump(all_args,f, indent=1)

        #obser.time -= 1
        data={}
        data["logger"] = Dummy(info=print)
        if len(obs_df)< 100:
            print(obser.to_records(index=False))

        ranker.init(INSTANCE.n, INSTANCE.t_limit+1)
        dummy_c_last = contacts_df.iloc[-1:].to_records(index=False)[0]
        for t in range(0,INSTANCE.t_limit+1):
            print(f"{t}",end="  ")
            obs_day = obser[obser.time == t]
            obs_day = obs_day.to_records(index=False)
            daily_c = contacts_df[contacts_df.t == t].to_records(index=False)
            #print("N contacts daily:", len(daily_c))
            #print(type(t)0
            if len(daily_c) == 0:
                print("Zero contacts")
                daily_c = [(dummy_c_last[0], dummy_c_last[1], t, 0.)]
            #else: #print(daily_c[:2])
            r = ranker.rank(t,daily_contacts=daily_c, daily_obs=tuple(obs_day), data=data)
            #ranks.append()
            #print(type(r), r[0])
            if "<I>" in data.keys():
                print("I: ",data["<I>"][t])
            res = np.array([tuple(x) for x in r], dtype=[("idx","i8"),("risk","f8")])

        res.sort(axis=0, order="idx")
        print("\n Saving")
        
        np.savez_compressed(name_file_instance+"_rank.npz", ranking=res)
