import numpy as np
from sklearn.metrics import roc_curve

def get_obs_idx(obs_df, states=(1,2)):
    """
    Get the index of the nodes which are observed in the mentioned states
    """
    r = None
    for l in states:
        if r is None:
            r = obs_df.obs == l
        else:
            r = r | (obs_df.obs == l)
    
    obs_i_r = set(obs_df.node[r])
    return obs_i_r

def get_err_rocs_risks(risks, nodes_idx, fin_conf, state=1):
    true_states = fin_conf[list(nodes_idx)]
    valid = (true_states == state)
    
    
    prs = risks[list(nodes_idx)]
    #print(prs.index)

    roc = roc_curve(valid.astype(np.int8), prs)
    
    return roc

def calc_rocs_risk(risks_arr, fin_confs_seed, obs_all_seed, instance,
            st_exclude=(1,2), st_find=(1,)):
    """
    Calculate ROCs on the marginals
    excluding those with observed state in `st_exclude`,
    finding the nodes with state in `st_find` at time `t_obs`
    """
    resu =[]
    if len(st_find) > 1:
        raise ValueError("Only one state possible")
    n_inst = min(len(fin_confs_seed), len(risks_arr))
    for i, conf_fin in enumerate(fin_confs_seed[:n_inst]):
        nidx = get_obs_idx(obs_all_seed[i], states=st_exclude)
        sel_idx = set(range(instance.n)).difference(nidx)
        errs = get_err_rocs_risks(risks_arr[i], sel_idx, conf_fin, state=st_find[0])
        resu.append(errs)
        
    return resu