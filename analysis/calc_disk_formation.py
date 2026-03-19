import numpy as np
from post_tasks import calc_task, Msun

G = 6.67430e-8
c = 2.99792458e10
Msun = 1.98847e33

@calc_task(files=["omega.xg", "mass_bary.xg"])
def disk_formation_time(sim_name, data):

    cache = data["cache"]

    omega_blocks = cache.get_xg("omega.xg")
    mass_blocks = cache.get_xg("mass_bary.xg")

    if not omega_blocks or not mass_blocks:
        return {"t_disk": np.nan}

    # Use pre-collapse profile
    omega_arr = omega_blocks[0]
    mass_arr = mass_blocks[0]

    r = omega_arr[:,0]
    omega = omega_arr[:,1]
    m_enc = mass_arr[:,1]

    Msun = 1.98847e33
    M_min =  0.1*Msun

    valid = m_enc > M_min

    j = r**2 * omega
    j_isco = 2*np.sqrt(3) * G * m_enc / c

    mask = (j > j_isco) & valid

    if not np.any(mask):
        return {"t_disk": np.nan, "M_disk": np.nan}

    idx = np.argmax(mask)

    r_disk = r[idx]
    M_disk = m_enc[idx]

        # free fall time
    t_ff = np.pi * np.sqrt(r_disk**3 / (8 * G * M_disk))

        # disk formation time
    t_df = 2 * t_ff

    return {"t_disk": t_df,
            "M_disk": M_disk / Msun
            }