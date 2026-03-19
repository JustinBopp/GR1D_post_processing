import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

Msun = 1.98847e33
rho_surface = 1e11  # PNS surface density threshold

# global storage
pns_bary_multi = []
pns_grav_multi = []


def get_block_times(filepath):
    """Extract snapshot times from .xg file headers."""
    times = []
    with open(filepath) as f:
        for line in f:
            if "Time" in line:
                try:
                    times.append(float(line.split("=")[1]))
                except:
                    pass
    return np.array(times)


@plot_task(files=["rho.xg", "mass_bary.xg", "mass_grav.xg"])
def plot_multi_pns_mass(sim_name, data, images_dir):

    global pns_bary_multi, pns_grav_multi

    cache = data["cache"]
    run_dir = data["sim_dir"]
    t_bounce = data.get("t_bounce", 0.0)

    rho_blocks = cache.get_xg("rho.xg")
    bary_blocks = cache.get_xg("mass_bary.xg")
    grav_blocks = cache.get_xg("mass_grav.xg")

    if not rho_blocks:
        print(f"No rho data for {sim_name}")
        return

    times = get_block_times(os.path.join(run_dir, "rho.xg"))

    Mb = []
    Mg = []
    t_post = []

    n = min(len(rho_blocks), len(bary_blocks), len(grav_blocks), len(times))

    for i in range(n):

        t = times[i] - t_bounce
        if t < 0:
            continue

        rho_profile = rho_blocks[i][:,1]
        bary_profile = bary_blocks[i][:,1]
        grav_profile = grav_blocks[i][:,1]

        # find zone closest to rho = 1e11
        idx = np.argmin(np.abs(rho_profile - rho_surface))

        Mb.append(bary_profile[idx] / Msun)
        Mg.append(grav_profile[idx] / Msun)
        t_post.append(t)

    if t_post:
        pns_bary_multi.append((sim_name, np.array(t_post), np.array(Mb)))
        pns_grav_multi.append((sim_name, np.array(t_post), np.array(Mg)))


def finalize_multi_pns_mass(data_dict, images_dir):

    os.makedirs(images_dir, exist_ok=True)

    if pns_bary_multi:
        plt.figure()
        for sim, t, m in pns_bary_multi:
            plt.plot(t*1000, m, label=sim)

        plt.xlabel("t - t_bounce [ms]")
        plt.ylabel("PNS Baryonic Mass [M$_\\odot$]")
        plt.title("PNS Baryonic Mass Evolution")
        plt.grid(True)
        plt.legend()
        plt.xlim(left=0)

        outfile = os.path.join(images_dir, "pns_mass_bary_all_sims.png")
        plt.savefig(outfile, dpi=200)
        plt.close()
        print(f"Saved plot -> {outfile}")


    if pns_grav_multi:
        plt.figure()
        for sim, t, m in pns_grav_multi:
            plt.plot(t*1000, m, label=sim)

        plt.xlabel("t - t_bounce [ms]")
        plt.ylabel("PNS Gravitational Mass [M$_\\odot$]")
        plt.title("PNS Gravitational Mass Evolution")
        plt.grid(True)
        plt.legend()
        plt.xlim(left=0)

        outfile = os.path.join(images_dir, "pns_mass_grav_all_sims.png")
        plt.savefig(outfile, dpi=200)
        plt.close()
        print(f"Saved plot -> {outfile}")


plot_multi_pns_mass.finalize = finalize_multi_pns_mass