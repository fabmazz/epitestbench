import numpy as np
import pandas as pd
from collections import namedtuple

Dummy = namedtuple("dummy", ["info"])

def prepare_contacts(conts):
    t_limit = int(conts[:,0].max())+1
    conts_df = pd.DataFrame(
        {"t": conts[:,0].astype(int),
        "i": conts[:,1].astype(np.int_),
        "j": conts[:,2].astype(np.int_),
        "lam": conts[:,3]
        })
        #conts[:,:3].astype(int), columns=["t","i","j"], dtype=int)
    #conts_df["lam"]=conts[:,3]
    ## add fake contact for the last time
    #print({k: conts_df[k].dtype for k in conts_df})
    r1 = conts_df.iloc[1].to_dict()
    r1=dict(t=[t_limit],i=[int(r1["i"])], j=[int(r1["j"])], lam=[0.]) #t_limit
    #r1 = {k: np.array(r1[k]) for k in r1}
    #r1["lam"] = 0.
    #print(r1)
    conts_all = pd.concat([conts_df, pd.DataFrame(r1)],ignore_index=True)

    conts_all = conts_all[["i","j","t", "lam"]]
    print({k: conts_all[k].dtype for k in conts_all})
    return conts_all #conts_all.convert_dtypes(convert_integer=True)

def launch_ranker(ranker, epinstance,contacts_df, observations):
    data={}
    data["logger"] = Dummy(info=print)
    ranker.init(epinstance.n, epinstance.t_limit+1)
    dummy_c_last = contacts_df.iloc[-1:].to_records(index=False)[0]
    for t in range(0,epinstance.t_limit+1):
        print(f"{t}",end="  ")
        #obs_day = obser[obser.time == t]
        obs_day = filter(lambda o: o[2] == t, observations) 
        #obs_day.to_records(index=False)
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
    return res