from julia import Main
import json, sys, os
import numpy as np
import pandas as pd
from pathlib import Path
import time
from copy import deepcopy

from networkx.algorithms import is_connected

from epigen.observ_gen import calc_epidemies
'''
def module_path():
    #encoding = sys.getfilesystemencoding()
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)
p = Path(module_path()).absolute()
sys.path.append(str(p)+"/")
'''
#from julia.api import Julia
#jl = Julia(compiled_modules=False)
from epitestlib.make_parser import create_parser, create_data, get_versions
try:
    from pyepi import epi_runner as epi_run
except ImportError as e:
    print("Cannot find pyepi, have you run `pip install -e .` ?")
    print("Path: ",sys.path)
    raise e

def add_arguments(parser):
    parser.add_argument('--p_source', type=float, default=-1, dest="p_source", help="p_source")
    parser.add_argument("--max_iter", type=int, default=800, help="maximum number of iterations")
    parser.add_argument("-mi","--min_iter", type=int, default=100, help="minimum number of iterations per run")

    #parser.add_argument("--max_iter", type=int, default=100, help="maximum number of iterations")

    parser.add_argument("--eps_conv", type=float, default=1e-6, help="ɛ to convergence")

    parser.add_argument("-v","--verbose", action="store_true", help="be verbose in the convergence")

    parser.add_argument("--seeds_range", nargs="*", type=int, help="Seeds to run sequentially (different instances, start to end)")

    parser.add_argument("--damps", nargs="*", type=float, default=[0.3,0.6], help="Sequence of damping to use")

    parser.add_argument("--beta_conv", type=float, default=-1., help="Fraction or number of steps to do annealing observations")

    #parser.add_argument("--t_lim_cut", type=int, default=-1, help="Final time to cut the epidemic (resizing)")
    return parser

def round_f(k,n):
    try:
        _ = round(k,n)
        ## it's numeric
        return _
    except TypeError:
        return k

def run_epi_(args_all, seed):

    #print(args)
    args = deepcopy(args_all)
    if seed is not None:
        args.seed = seed

    data_epi, name_file, epInstance = create_data(args)

    if args.p_source <= 0:
        p_src = 1/epInstance.n
    else:
        p_src = args.p_source

    prob_sources_EPI =  np.full(epInstance.n, p_src)
    ## parse contacts
    contacts_py = data_epi["contacts"]
    contacts = np.vstack((contacts_py[:,1]+1, contacts_py[:,2]+1, contacts_py[:,0], contacts_py[:,3])).T
    ### check
    assert np.max(contacts[:,0:2]) <= epInstance.n
    assert np.max(contacts[:,2]) <= epInstance.t_limit

    ##check for static graphs
    if data_epi["G"] is not None:
        v=is_connected(data_epi["G"])
        print(f"Graph connected: {v}")
        assert v

    #print("Min t", contacts[:,2].min())

    #np.savez_compressed(name_file+"_contacts.npz", contacts_py)

    cts_EPI = epi_run.adapt_contacts(contacts)
    print("cts_EPI", cts_EPI.keys())

    start_i = args.start_conf
    t_limit = epInstance.t_limit
    versions = get_versions()
    try:
        versions["EPI"] = epi_run.git_rev_hash()
    except:
        print("Cannot find EPI version")
    
    #print(cts_EPI[0])
    #print(contacts[-200:])
    if args.beta_conv <= 0 :
        betas_conv = [1.,1.,1.]
    else:
        if args.beta_conv <= 1:
            nbetas = int(args.max_iter*args.beta_conv)
        else:
            nbetas = int(args.beta_conv)
        print(f"Have {nbetas} beta")
        betas_conv = list(np.linspace(0,1,nbetas))
    
    mRunner = epi_run.Runner(epInstance, cts_EPI, prob_sources_EPI, p_obs_error=1e-6)
    for inst_i in range(start_i, start_i+args.num_conf):
        print(f"Instance {inst_i}")
        real_src = data_epi["test"][inst_i][0]
        print("Real source:",np.where(real_src)[0])

        name_file_instance = name_file + "_" + str(inst_i)
        all_args = dict(vars(args))
        all_args["versions"] = versions
        all_args["convergence"] = []

        if not args.sparse_obs:
            obs_list = []
            last_obs = data_epi["test"][inst_i][1]
            for i, s in enumerate(last_obs):
                obs_list.append([i,s,t_limit])
            
        else:
            obs_df = data_epi["observ_df"][inst_i]
            obs_list = []
            obs_v = obs_df[["node","obs_st","time"]].to_numpy()
            obs_list = obs_v.tolist()
            print(obs_list)

            obs_df.to_csv(name_file_instance+"_obs_sparse.csv",index=False)
        #obs_list = list(obs_list)
        obs_list.sort(key=lambda tup: tup[2])
        ## convert to matrix
        print("Num obs: ", len(obs_list))
        if len(obs_list) > 0:
            observ_mat = np.array(obs_list).astype(int)
            observ_mat[:,0]+=1
            assert np.max(observ_mat[:,2]) <= epInstance.t_limit +1
            assert np.max(observ_mat[:,0]) <= epInstance.n
        else:
            observ_mat = []
        
        mRunner.clear_o()
        mRunner.set_obs(observ_mat)
        
        t0 = time.time()
        print("nodes check:",mRunner.nodes())
        epsi = 1000*args.eps_conv
        damping = [(l, v) for l,v in zip([args.max_iter]*len(args.damps),args.damps)]
        print(damping)
        min_iter = args.min_iter
        betas_do = True

        for maxit, damp in damping:
            try:
                epsi = mRunner.iterate(eps=args.eps_conv,
                        maxiter=maxit, damp=damp, miniter=min_iter,
                        verbose=args.verbose,
                        shuffle_every=1,
                        betas= betas_conv if betas_do else [1.,1.,1.,1.])
            except RuntimeError as e:
                print(e)
                print("ERROR CONVERGING, trying more shuffling and damping")
                try:
                    epsi = mRunner.iterate(eps=args.eps_conv,
                        maxiter=maxit, miniter=min_iter, damp=damp+0.1, 
                        verbose=args.verbose,
                        shuffle_every=1)
                except RuntimeError:
                    try:
                        epsi = mRunner.iterate(eps=args.eps_conv,
                            maxiter=maxit,miniter=min_iter, damp=min(damp+0.5,0.99), 
                            verbose=args.verbose,
                            shuffle_every=1)
                    except RuntimeError as ee:
                        def myf(dat, t):
                            df = pd.DataFrame(epi_run.EPI.get_contacts_vector(dat), columns=["i","j","lam"])
                            df["t"] = t
                            return df
                        cts_out = [myf(cts_EPI[k], k)  for k in sorted(cts_EPI.keys())]
                        cts_out_c = pd.concat(cts_out, ignore_index=True)
                        cts_out_c.to_csv(name_file_instance+"_contacts.csv", index=False)
                        print("RUNTIME ERROR, saving contacts: ")
                        print("Saved at ", name_file_instance+"_contacts.csv")
                        raise ee
            #all_args["convergence"].append({"damp":0., "eps_final":epsi,"maxiter":args.max_iter})
            if np.max(epsi) > args.eps_conv:
                print(f"Not converged yet, eps: {epsi}")
                if betas_do: betas_do=False
            else:
                break
                """epsi = mRunner.iterate(eps=args.eps_conv,
                        maxiter=args.max_iter, damp=0.3, 
                        verbose=args.verbose,
                        shuffle_every=30)
                #all_args["convergence"].append({"damp":0.3, "eps_final":epsi,"maxiter":args.max_iter})
                """

        out_margs = dict()
        if np.max(epsi) > args.eps_conv:
            print(f"Not converged by the end. eps: {epsi}")

            res = mRunner.get_margs_error(
                eps=args.eps_conv, maxiter=500, damp=0.8,verbose=args.verbose,
                shuffle_every=1
            )
            margs_max, margs_min, margs_avg, margs_var = res[:4]
            out_margs["max"] = margs_max
            out_margs["min"] = margs_min

            out_margs["mean"] = margs_avg
            out_margs["var"] = margs_var
        
        margins = np.stack([n.marg for n in mRunner.nodes()])
        t_taken = time.time() -t0
        print("Took {} sec".format(t_taken))
        out_margs["marginals"] = margins

        
        all_args["time_convergence"] = t_taken
        all_args["convergence"] = mRunner.history
        with open(name_file_instance+"_args.json","w") as mfile:
            json.dump(all_args,mfile, indent=1)

        np.savez_compressed(name_file_instance+"_margs.npz", **out_margs)

        np.savez_compressed(name_file_instance+"_eps_traces.npz", 
            **({f"eps_{round_f(e,2)}": c for e,c in mRunner.error_trace.items()}) )

        print("Saved data")

    
if __name__ == "__main__":
    import gc

    parser = create_parser()
    parser = add_arguments(parser)

    args = parser.parse_args()
    print("arguments:")
    print(args)

    seeds_range = args.seeds_range
    if seeds_range is None or len(seeds_range) == 0:
        ## proceed as normal
        run_epi_(args, None)

    elif len(seeds_range) < 2 or len(seeds_range) > 2:
        raise ValueError("Insert start and stop as `seeds_range`")
    else:
        for s in range(*seeds_range):
            ### run over different seeds
            #args.seed = s
            print(f"SEED: {s}")
            run_epi_(args, s)
            gc.collect()