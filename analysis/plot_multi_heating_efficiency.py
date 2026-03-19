import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

eff_multi=[]

@plot_task(files=["M1_net_heating.dat","M1_flux_lum.dat"])
def plot_multi_heating_efficiency(sim_name,data,images_dir):

    global eff_multi

    cache=data["cache"]
    t_bounce=data.get("t_bounce",0.0)

    heat=cache.get_dat("M1_net_heating.dat")
    lum=cache.get_dat("M1_flux_lum.dat")

    if heat is None or lum is None:
        return

    t=heat[:,0]
    qdot=heat[:,5]

    Lnu_e=lum[:,1]
    Lnu_ae=lum[:,2]

    eta=qdot/(Lnu_e+Lnu_ae)

    t_post=t-t_bounce
    mask=t_post>=0.02

    eff_multi.append((sim_name,t_post[mask]*1000,eta[mask]))


def finalize_multi_heating_efficiency(data_dict,images_dir):

    if not eff_multi:
        return

    plt.figure()

    for sim,t,e in eff_multi:
        plt.plot(t,e,label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("Heating efficiency")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=0)

    outfile=os.path.join(images_dir,"heating_efficiency_all_sims.png")
    plt.savefig(outfile,dpi=200)
    plt.close()

plot_multi_heating_efficiency.finalize=finalize_multi_heating_efficiency