import numpy as np
import sib

def make_callback(converged, eps_conv):
    def callback_print(t,err,f):
        print(f"iter: {t:6}, err: {err:.5e} ", end="\r")
        if err < eps_conv:
            converged[0] = True
    return callback_print

def sib_marginals(f, N, t_limit):
    M = np.zeros((N, t_limit+1, 3), dtype=float)
    for t in range(0,t_limit+1):
        MM = sib.marginals_t(f,t)
        for n in MM:
            M[n,t] = MM[n]
    return M

def run_sib_fg(instance, contacts, obs_list, mu_rate, maxit=1000):
    """
    Instance, contacts, obs_list, mu_rate, maxit
    """
    contacts_sib = [(int(i),int(j),int(t),l) for t,i,j,l in contacts]
    obs_l = obs_list
    #print(obs_l)
    obs_list_sib =[(i,-1,t) for t in range(instance.t_limit+1) for i in range(instance.n) ]
    obs_list_sib.extend(obs_l)

    obs_list_sib.sort(key=lambda tup: tup[2])

    params_sib = sib.Params(prob_r = sib.Exponential(mu=mu_rate), 
                                        prob_i = sib.Uniform(p=1-1e-6),
                                        pseed=1e-4, 
                                        psus=0.5,
                        pautoinf=1e-6)
    tol=1e-5
    conver = [False]
    f = sib.FactorGraph(params=params_sib, 
                        contacts = contacts_sib, 
                        observations = obs_list_sib)

    callback = make_callback(conver, tol)
    sib.iterate(f, maxit=maxit, tol=tol,
                callback=callback)
    #print(f"\nConverged: {conver[0]}")
    print("")
    sib.iterate(f, maxit=maxit, damping=0.5,
                tol=tol,
                callback=callback,)
    #print(f"\nConverged: {conver[0]}")
    print("")
    sib.iterate(f, maxit=maxit, damping=0.95,
                tol=tol,
                callback=callback,)
    print(f"\nConverged: {conver[0]}")
    return f



def run_sib_margs(instance, contacts, obs_list, mu_rate, maxit=1000):
    """
    Instance, contacts, obs_list, mu_rate, maxit
    """
    f = run_sib_fg(instance, contacts, obs_list, mu_rate, maxit=maxit)

    margs_sib = sib_marginals(f, instance.n, instance.t_limit)

    return margs_sib