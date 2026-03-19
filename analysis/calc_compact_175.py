import numpy as np
from post_tasks import calc_task, Msun

@calc_task(files=["mass_bary_at_bounce.xg"])
def compactness_1p75(sim_name, data):
    """Calculate ξ1.75 = (M/Msun) / (R(Mbary=M)/1000 km)"""
    cache = data["cache"]
    blocks = cache.get_xg("mass_bary_at_bounce.xg")
    if not blocks:
        return {"xi_1p75": np.nan}

    r_m = blocks[0]  # first block = time of bounce
    r = r_m[:,0]
    m = r_m[:,1] / Msun  # Msun units

    target_M = 1.75
    idx = np.searchsorted(m, target_M)
    if idx >= len(r):
        return {"xi_1p75": np.nan}

    R_M = r[idx] / 1000e5  # km
    xi = target_M / R_M
    return {"xi_1p75": xi}