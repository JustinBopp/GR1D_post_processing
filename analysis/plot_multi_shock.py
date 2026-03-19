import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

@plot_task(files=["shock_radius_t.dat"])
def plot_multi_shock_radius(sim_name, data, images_dir):
    """
    Collect shock radius vs t - t_bounce for each simulation.
    Uses t_bounce from post_process to align curves.
    """
    cache = data["cache"]
    t_bounce = data.get("t_bounce", 0.0)

    shock_file = "shock_radius_t.dat"
    shock_path = os.path.join(data["sim_dir"], shock_file)
    if not os.path.isfile(shock_path):
        print(f"No {shock_file} for {sim_name}")
        return

    arr = np.loadtxt(shock_path)
    if arr.ndim == 1 or arr.shape[1] < 2:
        print(f"Unexpected format in {shock_file} for {sim_name}")
        return

    times = arr[:,0] - t_bounce
    r_shock = arr[:,1] / 1e5  # km

    # Store per-simulation in data_dict for finalize
    data["shock_multi"] = (times, r_shock)

def finalize_multi_shock(pipeline_data, images_dir):
    plt.figure()
    for sim_name, data in pipeline_data.items():
        if "shock_multi" not in data:
            continue
        times, r_shock = data["shock_multi"]
        plt.plot(times*1000, r_shock, label=sim_name)

    plt.xlabel(r"$t - t_{bounce} \ [ms]$")
    plt.ylabel("Shock radius [km]")
    plt.title("Shock radius evolution for all simulations")
    plt.grid(True)
    plt.xlim(left=0)
    plt.legend()
    os.makedirs(images_dir, exist_ok=True)
    outfile = os.path.join(images_dir, "shock_radius_all_sims.png")
    plt.savefig(outfile, dpi=200)
    plt.close()
    print(f"Saved multi-simulation shock radius plot -> {outfile}")

# Attach finalize to the decorator so post_process calls it
plot_multi_shock_radius.finalize = finalize_multi_shock