from pathlib import Path
import numpy as np
import pandas as pd

def _make_range_confs(in_range):
    if isinstance(in_range, range):
        return in_range
    
    if len(in_range) < 2:
        raise ValueError("Input start and finish")
    elif len(in_range) == 2:
        load_range = range(*in_range)
    else:
        load_range = in_range
    return load_range

def read_margs_inst(fold, inst, prefix="", name_npz="margs", range_confs=(0,1),
    post_inst="", name_array="marginals", outprint=True):
    """
    Read marginals with instance naming
    """
    name = f"{prefix}"+ str(inst)+ post_inst
    
    margs = []
    path = Path(fold)
    if outprint:
        print(path.resolve().as_posix())

    load_range = _make_range_confs(range_confs)

    if outprint: print(load_range)
    for i in load_range:
        nam_f = name + f"_{i}_{name_npz}.npz"
        d = np.load(path / nam_f)
        try:
            margs.append(d[name_array])
        except KeyError as e:
            raise ValueError(f"KEY '{name_array}' not found, keys are: "+str(tuple(d.keys())) ) from e

        d.close()
    return margs

def read_risk_inst(fold, inst, ranker, prefix="", range_confs=(0,1), outprint=True):
    """
    Read marginals with instance naming
    """
    name = f"{prefix}"+ str(inst)+f"_rk_{ranker}"
    
    ranking = []
    path = Path(fold)
    if outprint:
        print(path.resolve().as_posix())
    
    load_range = _make_range_confs(range_confs)
    if outprint: print(load_range)

    for i in load_range:
        nam_f = name + f"_{i}_rank.npz"
        d = np.load(path / nam_f)
        rep = d["ranking"]
        ser = pd.Series(index=rep["idx"], data=rep["risk"])
        ranking.append(ser)
        d.close()
    return ranking