import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

heating_multi=[]

@plot_task(files=["M1_net_heating.dat"])
def plot_multi_net_heating(sim_name,data,images_dir):

    global heating_multi

    cache=data["cache"]
    t_bounce=data.get("t_bounce",0.0)

    arr=cache.get_dat("M1_net_heating.dat")
    if arr is None:
        return

    t = arr[:,0]
    qdot = arr[:,5]   # <-- net heating column

    t_post = t - t_bounce
    mask = t_post >= 0.02

    heating_multi.append((sim_name,t_post[mask]*1000,qdot[mask]))


def finalize_multi_net_heating(data_dict,images_dir):

    if not heating_multi:
        return

    plt.figure()

    for sim,t,q in heating_multi:
        plt.plot(t,q,label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("Net heating rate [erg s$^{-1}$]")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=0)

    outfile=os.path.join(images_dir,"net_heating_all_sims.png")
    plt.savefig(outfile,dpi=200)
    plt.close()

plot_multi_net_heating.finalize=finalize_multi_net_heating