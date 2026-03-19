import numpy as np
from post_tasks import calc_task, Msun

G = 6.67430e-8
c = 2.99792458e10
Msun = 1.98847e33

@calc_task(files=["omega.xg"])
def initial_central_omega(sim_name, data):
    """
    Calculate the initial central angular velocity Omega_c from omega.xg
    Returns in rad/s.
    """
    cache = data["cache"]
    blocks = cache.get_xg("omega.xg")
    if not blocks or len(blocks) == 0:
        return {"Omega_c": np.nan}

    # Take first block (pre-SN)
    omega_data = blocks[0]
    r = omega_data[:,0]       # radius in cm
    omega = omega_data[:,1]   # angular velocity in rad/s

    # Central angular velocity = omega at smallest radius
    Omega_c = omega[0] if len(omega) > 0 else np.nan

    return {"Omega_c": Omega_c}