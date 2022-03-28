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