import os
import numpy as np
import matplotlib.pyplot as plt
from post_tasks import plot_task

# global storage
toverw_multi = []

@plot_task(files=["ToverW_edge.dat"])
def plot_multi_toverw(sim_name, data, images_dir):

    global toverw_multi

    cache = data["cache"]
    t_bounce = data.get("t_bounce", 0.0)

    arr = cache.get_dat("ToverW_edge.dat")

    if arr is None or arr.shape[1] < 2:
        print(f"No valid ToverW_edge.dat for {sim_name}")
        return

    times = arr[:,0]
    toverw = arr[:,1]

    # convert to post-bounce time
    t_post = times - t_bounce

    # keep only post-bounce
    mask = t_post >= 0
    t_post = t_post[mask] * 1000.0   # seconds → ms
    toverw = toverw[mask]

    if len(t_post) == 0:
        return

    toverw_multi.append((sim_name, t_post, toverw))


def finalize_multi_toverw(data_dict, images_dir):

    global toverw_multi

    if not toverw_multi:
        return

    plt.figure()

    for sim_name, t, tw in toverw_multi:
        plt.plot(t, tw, label=sim_name)

    plt.xlabel("t - t$_{bounce}$ [ms]")
    plt.ylabel("T / |W|")
    plt.title("Rotational Energy Ratio Evolution")
    plt.grid(True)
    plt.legend()

    plt.xlim(left=0)

    os.makedirs(images_dir, exist_ok=True)
    outfile = os.path.join(images_dir, "toverw_all_sims.png")

    plt.savefig(outfile, dpi=200)
    plt.close()

    print(f"Saved multi-simulation ToverW plot -> {outfile}")


plot_multi_toverw.finalize = finalize_multi_toverw