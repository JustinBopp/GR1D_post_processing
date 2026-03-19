import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

vturb_max_multi = []
vturb_shock_multi = []
vturb_pns_multi = []
mach_gain_multi = []


def get_times(path):
    times = []
    with open(path) as f:
        for line in f:
            if "Time" in line:
                times.append(float(line.split("=")[1]))
    return np.array(times)


@plot_task(files=["v_turb.xg", "rho.xg", "rho_c_t.dat", "shock_radius_t.dat", "cs.xg"])
def plot_multi_vturb(sim_name, data, images_dir):

    global vturb_max_multi, vturb_shock_multi, vturb_pns_multi, mach_gain_multi

    cache = data["cache"]
    run_dir = data["sim_dir"]
    t_bounce = data.get("t_bounce", 0.0)

    vturb_blocks = cache.get_xg("v_turb.xg")
    rho_blocks = cache.get_xg("rho.xg")
    cs_blocks = cache.get_xg("cs.xg")

    rho_c_arr = cache.get_dat("rho_c_t.dat")
    shock_arr = cache.get_dat("shock_radius_t.dat")

    if not vturb_blocks or not rho_blocks or not cs_blocks or rho_c_arr is None or shock_arr is None:
        print(f"Missing data for {sim_name}")
        return

    times = get_times(os.path.join(run_dir, "v_turb.xg"))

    rho_c_t = rho_c_arr[:, 0]
    rho_c_val = rho_c_arr[:, 1]

    shock_t = shock_arr[:, 0]
    shock_r = shock_arr[:, 1]

    t_out = []
    v_max_out = []
    v_shock_out = []
    v_pns_out = []
    mach_gain_out = []

    for i, vt_block in enumerate(vturb_blocks):

        if i >= len(rho_blocks) or i >= len(cs_blocks) or i >= len(times):
            break

        t_sim = times[i]
        t = t_sim - t_bounce

        # --- only post-bounce turbulence ---
        if t < 0.02:
            continue

        r = vt_block[:, 0]
        vt = vt_block[:, 1]
        rho = rho_blocks[i][:, 1]
        cs = cs_blocks[i][:, 1]

        # ---------- MAX VTURB ----------
        v_max = np.max(vt)

        # ---------- SHOCK ----------
        r_shock = np.interp(t_sim, shock_t, shock_r)
        r_target_shock = 0.9 * r_shock
        idx_shock = np.argmin(np.abs(r - r_target_shock))
        v_shock = vt[idx_shock]
        # idx_shock = np.argmin(np.abs(r - r_shock))
        # v_shock = vt[idx_shock]

        # ---------- PNS ----------
        rho_c = np.interp(t_sim, rho_c_t, rho_c_val)
        idx_pns = np.argmin(np.abs(rho - rho_c))
        r_pns = r[idx_pns]
        r_target_pns = 1.2 * r_pns
        idx_pns_outer = np.argmin(np.abs(r - r_target_pns))
        v_pns = vt[idx_pns_outer]

        # ---------- MACH IN GAIN REGION ----------
        gain_mask = (r > r_pns) & (r < r_shock) & (cs > 0)

        if np.any(gain_mask):
            mach = vt[gain_mask] / cs[gain_mask]
            mach_gain = np.max(mach)
        else:
            mach_gain = 0.0

        # ---------- STORE ----------
        t_out.append(t * 1000.0)
        v_max_out.append(v_max / 1e5)
        v_shock_out.append(v_shock / 1e5)
        v_pns_out.append(v_pns / 1e5)
        mach_gain_out.append(mach_gain)

    if t_out:
        vturb_max_multi.append((sim_name, np.array(t_out), np.array(v_max_out)))
        vturb_shock_multi.append((sim_name, np.array(t_out), np.array(v_shock_out)))
        vturb_pns_multi.append((sim_name, np.array(t_out), np.array(v_pns_out)))
        mach_gain_multi.append((sim_name, np.array(t_out), np.array(mach_gain_out)))


def finalize_multi_vturb(data_dict, images_dir):

    if not vturb_max_multi:
        return

    os.makedirs(images_dir, exist_ok=True)

    # ---------- MAX VTURB ----------
    plt.figure()
    for sim, t, v in vturb_max_multi:
        plt.plot(t, v, label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("Max $v_{turb}$ [km s$^{-1}$]")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=20)

    plt.savefig(os.path.join(images_dir, "vturb_max_all_sims.png"), dpi=200)
    plt.close()

    # ---------- VTURB AT SHOCK ----------
    plt.figure()
    for sim, t, v in vturb_shock_multi:
        plt.plot(t, v, label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("$v_{turb}$ at Shock [km s$^{-1}$]")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=20)

    plt.savefig(os.path.join(images_dir, "vturb_shock_all_sims.png"), dpi=200)
    plt.close()

    # ---------- VTURB AT PNS ----------
    plt.figure()
    for sim, t, v in vturb_pns_multi:
        plt.plot(t, v, label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("$v_{turb}$ at PNS Surface [km s$^{-1}$]")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=20)

    plt.savefig(os.path.join(images_dir, "vturb_pns_all_sims.png"), dpi=200)
    plt.close()

    # ---------- MACH IN GAIN REGION ----------
    plt.figure()
    for sim, t, m in mach_gain_multi:
        plt.plot(t, m, label=sim)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("Max $\\mathcal{M}_{turb}$ (gain region)")
    plt.title("Maximum Turbulent Mach Number in Gain Region")
    plt.grid(True)
    plt.legend()
    plt.xlim(left=20)

    plt.savefig(os.path.join(images_dir, "mach_turb_gain_all_sims.png"), dpi=200)
    plt.close()


plot_multi_vturb.finalize = finalize_multi_vturb