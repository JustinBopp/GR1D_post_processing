import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

@plot_task(files=["rho_c_t.dat"])
def plot_multi_rho(sim_name, data, images_dir):
    """
    Collect rho vs t - t_bounce for each simulation.
    Uses t_bounce from post_process to align curves.
    """
    cache = data["cache"]
    t_bounce = data.get("t_bounce", 0.0)

    rho_file = "rho_c_t.dat"
    rho_path = os.path.join(data["sim_dir"], rho_file)
    if not os.path.isfile(rho_path):
        print(f"No {rho_file} for {sim_name}")
        return

    arr = np.loadtxt(rho_path)
    if arr.ndim == 1 or arr.shape[1] < 2:
        print(f"Unexpected format in {rho_file} for {sim_name}")
        return

    times = arr[:,0] - t_bounce
    rho = arr[:,1]   

    # Store per-simulation in data_dict for finalize
    data["rho_multi"] = (times, rho)

def finalize_multi_rho(pipeline_data, images_dir):
    plt.figure()
    for sim_name, data in pipeline_data.items():
        if "rho_multi" not in data:
            continue
        times, rho = data["rho_multi"]
        plt.plot(times*1000, rho, label=sim_name)

    plt.xlabel(r"$t - t_{bounce} \ [ms]$")
    plt.ylabel(r"$\rho \ [\mathrm{g}/\mathrm{cm^3}]$")
    plt.title("Density evolution for all simulations")
    plt.grid(True)
    plt.xlim(left=0)
    plt.legend()
    os.makedirs(images_dir, exist_ok=True)
    outfile = os.path.join(images_dir, "rho_all_sims.png")
    plt.savefig(outfile, dpi=200)
    plt.close()
    print(f"Saved multi-simulation rho plot -> {outfile}")

# Attach finalize to the decorator so post_process calls it
plot_multi_rho.finalize = finalize_multi_rho