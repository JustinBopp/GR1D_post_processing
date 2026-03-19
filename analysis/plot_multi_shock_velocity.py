import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

shock_vel_multi = []

@plot_task(files=["shock_radius_t.dat"])
def plot_multi_shock_velocity(sim_name, data, images_dir):

    global shock_vel_multi

    cache = data["cache"]
    t_bounce = data.get("t_bounce",0.0)

    arr = cache.get_dat("shock_radius_t.dat")
    if arr is None:
        return

    t = arr[:,0]
    r = arr[:,1]

    t_post = t - t_bounce
    mask = t_post >= 0.02

    t_post = t_post[mask]
    r = r[mask]
    from scipy.signal import savgol_filter

# r: shock radius array
# window_length: must be odd, e.g., 15 or 21
# polyorder: usually 2 or 3
    r_smooth = savgol_filter(r, window_length=15, polyorder=2)

    v = np.gradient(r_smooth, t_post)

    shock_vel_multi.append((sim_name, t_post*1000, v/1e5))  # km/s


def finalize_multi_shock_velocity(data_dict, images_dir):

    if not shock_vel_multi:
        return

    plt.figure()

    for sim,t,v in shock_vel_multi:
        plt.plot(t,v,label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("Shock velocity [km s$^{-1}$]")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=0)

    outfile=os.path.join(images_dir,"shock_velocity_all_sims.png")
    plt.savefig(outfile,dpi=200)
    plt.close()

plot_multi_shock_velocity.finalize = finalize_multi_shock_velocity