import json
import numpy as np
from lib.make_parser import create_parser, create_data

from pyepi import epi_runner as runner

def add_arguments(parser):
    parser.add_argument('--p_source', type=float, default=-1, dest="p_source", help="p_source")
    parser.add_argument("--max_iter", type=int, default=100, help="maximum number of iterations")

    parser.add_argument("--eps_conv", type=float, default=1e-6, help="ɛ to convergence")

    parser.add_argument("-v","--verbose", action="store_true", help="be verbose in the convergence")

    return parser

if __name__ == "__main__":

    parser = create_parser()
    parser = add_arguments(parser)

    args = parser.parse_args()



    data_, name_file, epInstance = create_data(args)

    if args.p_source <= 0:
        p_src = 1/epInstance.n
    else:
        p_src = args.p_source

    prob_sources_EPI =  np.full(epInstance.n, p_src)
    ## parse contacts
    contacts_py = data_["contacts"]
    contacts = np.vstack((contacts_py[:,1]+1, contacts_py[:,2]+1, contacts_py[:,0], contacts_py[:,3])).T
    ### check
    assert np.max(contacts[:,0:2]) <= epInstance.n
    assert np.max(contacts[:,2]) <= epInstance.t_limit

    cts_EPI = runner.adapt_contacts(contacts)

    start_i = args.start_conf
    t_limit = epInstance.t_limit
    for inst_i in range(start_i, start_i+args.num_conf):
        print(f"Instance {inst_i}")
        real_src = data_["test"][inst_i][0]
        print("Real source:",np.where(real_src)[0])

        name_file_instance = name_file + "_" + str(inst_i)

        if not args.sparse_obs:
            obs_list = []
            last_obs = data_["test"][inst_i][1]
            for i, s in enumerate(last_obs):
                obs_list.append([i,s,t_limit])
            
        else:
            obs_df = data_["observ_df"][inst_i]
            obs_list = []
            obs_v = obs_df[["node","obs_st","time"]].to_numpy()
            obs_list = obs_v.tolist()
            print(obs_list)

            obs_df.to_csv(name_file_instance+"_obs_sparse.csv",index=False)
        #obs_list = list(obs_list)
        obs_list.sort(key=lambda tup: tup[2])
        ## convert to matrix
        if len(obs_list) > 0:
            observ_mat = np.array(obs_list).astype(int)
            observ_mat[:,0]+=1
            assert np.max(observ_mat[:,2]) <= epInstance.t_limit +1
            assert np.max(observ_mat[:,0]) <= epInstance.n
        else:
            observ_mat = []

        nodes = runner.iface().run_mp_trajectories(epInstance.n, epInstance.t_limit, cts_EPI, prob_sources_EPI,
            obs=observ_mat, epsconv=args.eps_conv,
            printout=True,maxiter=args.max_iter, damp=0., verbose=args.verbose)

        margins = np.stack([n.marg for n in nodes])

        all_args = vars(args)
        with open(name_file_instance+"_args.json","w") as mfile:
            json.dump(all_args,mfile, indent=1)

        np.savez_compressed(name_file_instance+"_margs.npz", marginals=margins)

        print("Saved data")

    