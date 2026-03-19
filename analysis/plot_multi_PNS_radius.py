import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

rho_surface=1e11
pns_radius_multi=[]

def get_times(path):

    times=[]
    with open(path) as f:
        for line in f:
            if "Time" in line:
                times.append(float(line.split("=")[1]))
    return np.array(times)


@plot_task(files=["rho.xg"])
def plot_multi_pns_radius(sim_name,data,images_dir):

    global pns_radius_multi

    cache=data["cache"]
    run_dir=data["sim_dir"]
    t_bounce=data.get("t_bounce",0.0)

    rho_blocks=cache.get_xg("rho.xg")

    times=get_times(os.path.join(run_dir,"rho.xg"))

    t_out=[]
    r_out=[]

    for i,block in enumerate(rho_blocks):

        t=times[i]-t_bounce
        if t<0:
            continue

        r=block[:,0]
        rho=block[:,1]

        idx=np.argmin(np.abs(rho-rho_surface))

        t_out.append(t*1000)
        r_out.append(r[idx]/1e5)

    if t_out:
        pns_radius_multi.append((sim_name,np.array(t_out),np.array(r_out)))


def finalize_multi_pns_radius(data_dict,images_dir):

    if not pns_radius_multi:
        return

    plt.figure()

    for sim,t,r in pns_radius_multi:
        plt.plot(t,r,label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("PNS Radius [km]")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=0)

    outfile=os.path.join(images_dir,"pns_radius_all_sims.png")
    plt.savefig(outfile,dpi=200)
    plt.close()

plot_multi_pns_radius.finalize=finalize_multi_pns_radius