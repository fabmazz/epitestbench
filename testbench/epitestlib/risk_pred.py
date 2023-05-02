import numpy as np
import pandas as pd
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


def calc_stats_risk_inst(risks, nodes_idx, fin_conf, state=1, stat=roc_curve):
    true_states = fin_conf[list(nodes_idx)]
    valid = (true_states == state)
    
    
    prs = risks[list(nodes_idx)]
    #print(prs.index)

    res = stat(valid.astype(np.int8), prs)
    
    return res

def calc_stats_risk(risks_arr, fin_confs_seed, obs_all_seed, instance,
            st_exclude=(1,2), st_find=(1,), stat=roc_curve):
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
        errs = calc_stats_risk_inst(risks_arr[i], sel_idx, conf_fin, state=st_find[0], stat=stat)
        resu.append(errs)
        
    return resu

def find_pos_risks(true_v, rs):
    midx = rs.sort_values(ascending=False).index
    perc_pos = pd.Series(np.linspace(0.,1.,len(midx)),index=midx)
    return perc_pos[np.where(true_v!=0)[0]]
