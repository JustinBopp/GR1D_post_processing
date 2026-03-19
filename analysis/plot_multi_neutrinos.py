import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

# Global storage for all simulations
neutrino_data = {
    "lum": {"nu_e": [], "nu_ae": [], "nu_x": []},
    "rms": {"nu_e": [], "nu_ae": [], "nu_x": []}
}

# Column mapping
COL_MAP = {1: "nu_e", 2: "nu_ae", 3: "nu_x"}

@plot_task(files=["M1_flux_lum.dat", "M1_flux_rmsenergy_lab.dat"])
def plot_multi_neutrinos(sim_name, data, images_dir):
    """
    Collect neutrino luminosities and RMS energies for multiple simulations
    using M1_flux_lum.dat and M1_flux_rmsenergy_lab.dat (4 columns: t, ν_e, ν̄_e, ν_x)
    """
    global neutrino_data
    run_dir = data["sim_dir"]
    t_bounce = data.get("t_bounce", 0.0)

    # --- Luminosities ---
    lum_file = os.path.join(run_dir, "M1_flux_lum.dat")
    if os.path.isfile(lum_file):
        arr = np.loadtxt(lum_file)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 4)
        times = arr[:, 0] - t_bounce
        mask = times >= 0.02   # only post-bounce
        times = times[mask]
        for i, key in COL_MAP.items():
            neutrino_data["lum"][key].append((sim_name, times, arr[mask, i]))

    # --- RMS energies ---
    rms_file = os.path.join(run_dir, "M1_flux_rmsenergy_lab.dat")
    if os.path.isfile(rms_file):
        arr = np.loadtxt(rms_file)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 4)
        times = arr[:, 0] - t_bounce 
        mask = times >= 0.02   # only post-bounce
        times = times[mask]
        for i, key in COL_MAP.items():
            neutrino_data["rms"][key].append((sim_name, times, arr[mask, i]))

def finalize_multi_neutrinos(data_dict, images_dir):
    """
    Generate 6 multi-sim overlay plots: 3 luminosity, 3 RMS energy
    """
    global neutrino_data
    os.makedirs(images_dir, exist_ok=True)

    # --- Luminosity plots ---
    for key, sims in neutrino_data["lum"].items():
        if not sims:
            continue
        plt.figure()
        for sim_name, times, lum in sims:
            plt.plot(times*1000, lum, label=sim_name)
        plt.xlabel("t - t_bounce [ms]")
        plt.ylabel("Luminosity [erg/s]")
        plt.title(f"Neutrino luminosity: {key}")
        #plt.yscale("log")
        plt.xlim(left=0)
        plt.grid(True)
        plt.legend()
        outfile = os.path.join(images_dir, f"neutrino_lum_{key}.png")
        plt.savefig(outfile, dpi=200)
        plt.close()
        print(f"Saved plot -> {outfile}")

    # --- RMS Energy plots ---
    for key, sims in neutrino_data["rms"].items():
        if not sims:
            continue
        plt.figure()
        for sim_name, times, rms in sims:
            plt.plot(times*1000, rms, label=sim_name)
        plt.xlabel("t - t_bounce [ms]")
        plt.ylabel("RMS energy [MeV]")
        plt.title(f"Neutrino RMS energy: {key}")
        plt.xlim(left=0)
        plt.grid(True)
        plt.legend()
        outfile = os.path.join(images_dir, f"neutrino_rms_{key}.png")
        plt.savefig(outfile, dpi=200)
        plt.close()
        print(f"Saved plot -> {outfile}")

# Attach finalize
plot_multi_neutrinos.finalize = finalize_multi_neutrinos