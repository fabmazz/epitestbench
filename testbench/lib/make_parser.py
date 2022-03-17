import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from epigen import EpInstance, observ_gen
from epigen import get_git_revision_hash as epigen_version
from epigen.epidemy_gen import epidemy_gen_epinstance

from .version import git_version



def create_parser():
    # read arguments
    parser = argparse.ArgumentParser(description="Run a simulation and don't ask.")

    # generic options
    parser.add_argument('-N', type=int, default=100, dest="N", help='network size')
    parser.add_argument('-d', type=int, default=3, dest="d", help='network degree')
    parser.add_argument('--height', type=int, default=3, dest="h", help='network height (for TREE only)')
    parser.add_argument('--scale', type=float, default=1, help='network scale (for proximity only)')
    parser.add_argument('--p_edge', type=float, default=1, help='probability of temporal contacts')
    parser.add_argument('-T',"--t_limit", type=int, default=10, dest="t_limit", help='total time')
    parser.add_argument('-s', '--seed', type=int, default=1, dest="seed", help="seed used to generate all the data")
    parser.add_argument('--type_graph', type=str, default="TREE", dest="type_graph", help="type_graph")
    parser.add_argument('--small_lambda_limit', type=float, default=900, dest="small_lambda_limit", help='small time cut for real contacts data')
    parser.add_argument('--gamma', type=float, default=5e-4, dest="gamma", help="gamma (rate of infection for real data)")
    parser.add_argument('--path_contacts', type=str, default="i_bird_contacts.npz", dest="path_contacts", help="path real data contacts")
    parser.add_argument('--dir', type=str, default="results/", dest="output_dir", help='output directory')
    parser.add_argument('--lambda', type=float, default=0.5, dest="lambda_", help="lambda")
    parser.add_argument('--mu', type=float, default=1e-10, dest="mu", help="mu")
    parser.add_argument('--init_name_file', type=str, default="", dest="str_name_file", help="str_name_file")
    parser.add_argument('--path_dir', type=str, default="not_setted", dest="path_dir", help="path_dir")
    
    parser.add_argument("--lambda_rand", type=str, default="", dest="rand_lambda",
        help="Sample lambdas from this distribution, values: exponential, pareto, ecc")

    parser.add_argument("--p_gen", type=float, default=None,
        help="prob used in the random graph generation (gnp, WS)")

    parser.add_argument('--num_conf', type=int, default=10, dest="num_conf", help="num_conf with observations")
    parser.add_argument("--n_sources", type=int, default=1, help="Number of sources (seeds) for the epidemic cascades")
    parser.add_argument('--start_conf', type=int, default=0, dest="start_conf", help="starting number of the range of configurations to be computed")

    parser.add_argument("--ninf_min", type=float, default=1, dest="ninf_min", help="""minimum number of infected in the generated epidemies. \
        If < 1 but > 0, it is considered the fraction of the population""")
    parser.add_argument("--ninf_max", type=float, default=None, dest="ninf_max", help="""maximum number of infected in the generated epidemies. \
        If < 1 it is considered the fraction of the population""")
    parser.add_argument("--unique_numinf",  action="store_true", help="Make epidemies with unique number of final infected and recovered")
    parser.add_argument("--no_ver_gen", action="store_false", dest="verbose_gen", 
            help="Don't be too verbose in the generation of epidemies")

    parser.add_argument("--node_drop_p", type=float, default=0., dest="p_drop_node",
            help="Probability of dropping a node after generating random graph (only for dynamic graphs)")
    ###Observations args
    parser.add_argument("--sparse_obs", action="store_true", 
            help="Generate and run with sparse observations")
    parser.add_argument("--sparse_rnd_tests", type=int, default=-1, dest="sparse_n_test_time", 
            help="Number of random daily tests for each time")

    parser.add_argument("--sparse_obs_last", action="store_true",
            help="Only observe the infected, at the last time instant. No random observations are done")
    parser.add_argument("--sp_obs_min_t", type=int, default=None, help="Minimim time to start the observations")
    
    parser.add_argument("--pr_sympt", type=float, default=0., dest="sp_p_inf_symptoms", 
        help="probability for each infected individual to be symptomatic and get tested")
    parser.add_argument("--delay_test_p", type=float, nargs="*", dest="sp_p_test_delay", 
        help="List of probabilities for the time delay in testing symptomatic individuals, starting from 0. Enter one probability after the other, they will get normalized")
    parser.add_argument("--save_data_confs", action="store_true", 
            help="Save data of generated epidemies")
    ## use the new generator
    parser.add_argument("--sp_obs_new", action="store_true", 
            help="Use the new generator for observations")
    


    return parser
    
def create_data(args):
    """
    Generate the configurations needed for running
    """

    num_conf = args.num_conf 

    mInstance = EpInstance(type_graph=args.type_graph,
        n=args.N,
        d=args.d,
        t_limit=args.t_limit,
        lamda=args.lambda_,
        mu=args.mu, seed=args.seed,
        p_edge=args.p_edge,
        n_source=args.n_sources)

    if mInstance.mu < 0:
        raise ValueError("Negative value of mu")
    if mInstance.lambda_ < 0:
        raise ValueError("Negative value of lambda")
    data_gen = vars(args)
    data_gen.update({
        "start_time":0,
        "shift_t":True,
    })


    path_dir = args.path_dir
    if args.path_dir == "not_setted":
        path_dir = mInstance.type_graph

    data_ = epidemy_gen_epinstance(mInstance,
                    lim_infected=args.ninf_min,
                    max_infected=args.ninf_max,
                    num_conf=num_conf+args.start_conf,
                    extra_gen=data_gen,
                    unique_ninf=args.unique_numinf,
                    verbose=args.verbose_gen)

    
    if data_ == None:
        return data_, "", mInstance

    t_limit = mInstance.t_limit
    seed = mInstance.seed
    # Generate observations
    if args.sparse_obs:
        ##check args
        print("Generating sparse observations...")
        nrnd_tests = args.sparse_n_test_time
        pr_sympt = args.sp_p_inf_symptoms
        p_test_delay = args.sp_p_test_delay

        t_obs_lim = args.sp_obs_min_t if args.sp_obs_min_t != None else -1
        if (p_test_delay is None and nrnd_tests < 0):
            raise ValueError(
                "In order to run sparse observations you have to put the number of tests and the test delay")
        if p_test_delay is None:
            p_test_delay = np.array([1.])
        else:
            p_test_delay = np.array(p_test_delay)/sum(p_test_delay)
        ## get full epidemies
        if args.sp_obs_new:
            if args.sparse_obs_last:
                nrnd_tests = 0
                t_obs_lim = t_limit

            g = observ_gen.gen_obs_new_data(data_, mInstance,p_test_delay=p_test_delay,
                p_sympt=pr_sympt,
                n_test_rnd=nrnd_tests, seed=mInstance.seed,
                tobs_inf_min=t_obs_lim,
                tobs_rnd_lim=(t_obs_lim, None),
                allow_testing_pos=False
            )
            obs_df = [pd.DataFrame(x, columns=["node","obs_st","time"]) for x in g]
            obs_json = None
            
        else:
            #old code
            if args.sparse_obs_last:
                obs_df, obs_json = observ_gen.make_sparse_obs_last_t(data_,
                    t_limit, pr_sympt=pr_sympt, seed=seed, verbose=args.verbose_gen,
                    numeric_obs=True
                    )
            else:
                obs_df, obs_json = observ_gen.make_sparse_obs_default(data_,
                        t_limit, ntests=nrnd_tests, pr_sympt=pr_sympt,
                        p_test_delay=p_test_delay, seed=seed, verbose=args.verbose_gen,
                        min_t_inf=t_obs_lim,
                        numeric_obs=True)
        for df in obs_df:
            if "obs" in df:
                df["obs_st"] = df["obs"]
        data_["observ_df"] = obs_df
        if obs_json is not None:
            data_["observ_dict"] = obs_json
        #print(obs_df[0])
        print("DONE.")


    path_save =Path(path_dir)
    if not path_save.exists():
        raise ValueError("Save folder doesn't exist")

    
    ## ************ CREATE NAME FILE  ************

    name_file = get_name_file_instance(args, args.str_name_file, mInstance)

    #name_file += f"_h_source_{h_source}_h_log_p_{h_log_p}_h_obs_{h_obs}"
    #print(name_file)
    return data_, name_file, mInstance



def get_name_file_instance(args, str_name_f, instance):
    path_dir = args.path_dir
    if args.path_dir == "not_setted":
        path_dir = args.type_graph
    path_fold = Path(path_dir)
    return str(path_fold / str_name_f) + str(instance)

def get_base_name_file(args):
    """
    helper function
    """
    return args.str_name_file

def get_versions():
    version = {}
    try:
        version["epigen"] = epigen_version()
    except FileNotFoundError as e:
        print("Cannot find version of epigen", e)
    
    try:
        version["epitestbench"] = git_version()
    except FileNotFoundError as e:
        print("Cannot find version of epitestbench", e)
    
    return version