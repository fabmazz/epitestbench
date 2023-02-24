import numpy as np

def gen_obs_single_t(epitrace:np.ndarray, p_choose:float, seed=None, t_obs=None):
    T, N = epitrace.shape

    if seed == None:
        rng = np.random
    else:
        rng = np.random.RandomState(np.random.PCG64(seed))

    idcs = np.where(rng.rand(N) < p_choose)[0]
    if t_obs is None:
        times = rng.randint(0,T, len(idcs))
    else:
        times = np.full(len(idcs), int(t_obs))

    obs = epitrace[times, idcs]

    return list(zip(idcs, obs, times))

def gen_obs_fixed_inf(times, frac_inf, n_obs_day, T, rng):
    ti=times[0][0]+1
    tr = ti+times[1]
    
    N = len(ti)
    isinf=np.where(~np.isinf(ti))[0]
    tot_ninf = len(isinf)

    nobs_inf = int(rng.rand()+(frac_inf*tot_ninf))
    rng.shuffle(isinf)
    ### nodes to be observed
    nodes_obs=isinf[:nobs_inf]

    ti_obs=ti[nodes_obs]
    delay_t=(rng.rand(len(ti_obs))*(T-ti_obs+1))

    tobs_inf=(ti_obs+delay_t).astype(int)

    obs_node={t: [] for t in range(0,T+1)}
    ## add i to observe:
    all_obs =[]
    for i,tt in zip(nodes_obs, tobs_inf):
        obs_node[tt].append(i)
        all_obs.append((i,1,tt))

    for t in range(0,T+1):
        notinf = np.where(ti>t)[0]
        rng.shuffle(notinf)
        #rng.shuffle(notinf)
        nodes_sel = notinf[:(n_obs_day-len(obs_node[t]))]
        obs_node[t].extend(nodes_sel)
        all_obs.extend((i,0,t) for i in nodes_sel)
    

    return all_obs

def sort_obs(all_obs):
    return sorted(all_obs, key=lambda x: (x[2],x[1],x[0]))