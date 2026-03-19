#!/usr/bin/env python3
import os, sys, argparse, importlib
import numpy as np
import pandas as pd
from post_tasks import CALC_TASKS, PLOT_TASKS

# CONSTANTS 
G = 6.67430e-8
c = 2.99792458e10
Msun = 1.98847e33

#  DATA CACHE 
class DataCache:
    """Cache .xg and .dat files per simulation"""
    def __init__(self, run_dir):
        self.run_dir = run_dir
        self.cache = {}

    def get_xg(self, filename):
        if filename in self.cache:
            return self.cache[filename]

        path = os.path.join(self.run_dir, filename)
        if not os.path.isfile(path):
            self.cache[filename] = []
            return []

        blocks = []
        with open(path, "r") as f:
            lines = f.readlines()

        indices = [i for i,l in enumerate(lines) if "Time" in l]
        for idx in indices:
            tline = lines[idx]
            try:
                time = float(tline.split('=')[1].strip())
            except:
                time = 0.0
            start = idx + 1
            data_block = []
            while start < len(lines):
                parts = lines[start].split()
                if len(parts) != 2:
                    break
                try:
                    r = float(parts[0])
                    m = float(parts[1])
                    if r > 0:
                        data_block.append([r, m])
                except:
                    break
                start += 1
            if data_block:
                blocks.append(np.array(data_block))
        self.cache[filename] = blocks
        return blocks

    def get_dat(self, filename):
        if filename in self.cache:
            return self.cache[filename]
        path = os.path.join(self.run_dir, filename)
        if not os.path.isfile(path):
            self.cache[filename] = None
            return None
        arr = np.loadtxt(path)
        self.cache[filename] = arr
        return arr

# MAIN POST-PROCESS
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dirs", nargs="+", help="Simulation directories to process")
    parser.add_argument("--skip", nargs="+", default=["GR1D"], help="Simulation directories to skip")
    parser.add_argument("--skip-modules", nargs="+", default=[], help="Analysis modules (without .py) to skip")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    analysis_dir = os.path.join(base_dir, "analysis")

    sims_dir = os.path.join(base_dir, "sims")
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # Discover sim directories
    all_sims = sorted([d for d in os.listdir(sims_dir) if os.path.isdir(os.path.join(sims_dir,d))])
    sim_dirs = []
    if args.dirs:
        for d in args.dirs:
            # If it's a valid path, use it directly
            if os.path.isdir(d):
                sim_dirs.append(os.path.abspath(d))
            else:
                # Otherwise assume it's inside sims_dir
                candidate = os.path.join(sims_dir, d)
                if os.path.isdir(candidate):
                    sim_dirs.append(candidate)
                else:
                    print(f"Warning: directory not found -> {d}")
    else:
        sim_dirs = [
            os.path.join(sims_dir, d)
            for d in all_sims
            if d not in args.skip
    ]

# Import analysis scripts
    sys.path.insert(0, base_dir)
    for file in os.listdir(analysis_dir):
        if file.endswith(".py") and not file.startswith("_"):
            module_name = file[:-3]  # strip ".py"
            if module_name in args.skip_modules:
                print(f"Skipping analysis module: {module_name}")
                continue
            importlib.import_module(f"analysis.{module_name}")

    print("Registered calculation tasks:", [f.__name__ for f,_ in CALC_TASKS])
    print("Registered plot tasks:", [f.__name__ for f,_ in PLOT_TASKS])

    # RUN PIPELINE 
    calc_results = []
    pipeline_data = {}  # shared across sims for multi-sim plots

    for sim_path in sim_dirs:

        sim_name = os.path.basename(sim_path)

        run_candidate = os.path.join(sim_path, "run")
        if os.path.isdir(run_candidate):
            run_dir = run_candidate
        else:
            run_dir = sim_path
        cache = DataCache(run_dir)
        data_dict = {"cache": cache, "sim_dir": run_dir}
        # Load bounce time
        bounce_file = "mass_bary_at_bounce.xg"
        t_bounce = 0.0
        bounce_path = os.path.join(run_dir, bounce_file)
        if os.path.isfile(bounce_path):
            with open(bounce_path, "r") as f:
                for line in f:
                    if "Time" in line:
                        t_bounce = float(line.split('=')[1].strip())
                        break
        data_dict["t_bounce"] = t_bounce

        # Calculations
        sim_result = {"sim_directory": sim_name}
        for func, files in CALC_TASKS:
            res = func(sim_name, data_dict)
            if res is not None:
                sim_result.update(res)
        calc_results.append(sim_result)

        # Individual plots (call all plot functions per simulation)
        for func, files in PLOT_TASKS:
            func(sim_name, data_dict, images_dir)

        pipeline_data[sim_name] = data_dict

    # MULTI-SIM FINALIZERS
    for func, _ in PLOT_TASKS:
        finalize_func = getattr(func, "finalize", None)
        if callable(finalize_func):
            finalize_func(pipeline_data, images_dir)

    # Save calculation table
    if calc_results:
        df = pd.DataFrame(calc_results)
        latex_columns = {
        "sim_directory": r"$\mathrm{Simulation}$",
        "Omega_c": r"$\Omega_c$",
        "xi_1p75": r"$\xi_{1.75}$", 
        "xi_2p5": r"$\xi_{2.5}$",
        "t_disk": r"$t_{df}$",
        "M_disk": r"$M_{\circledot disk}",
        }
        df = df[list(latex_columns.keys())]
        df.rename(columns=latex_columns, inplace=True)  
        df = df.fillna("...")
        def format_numeric(x):
            try:
                return f"{float(x):.3f}"
            except (ValueError, TypeError):
                return x  # leave non-numeric as is (like "--" or NaN)
        # Apply to all columns
        for col in df.columns:
            df[col] = df[col].apply(format_numeric)

        csv_path = os.path.join(images_dir, "simulation_results.csv")
        df.to_latex(csv_path, index=False)
        #df.to_csv(csv_path, index=False, sep="&")
        print(f"Saved calculation table -> {csv_path}")

if __name__ == "__main__":
    main()