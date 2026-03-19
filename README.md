```
# Post-Processing Pipeline for GR1D Simulations

## Overview

This repository provides a modular post-processing pipeline for analyzing **1D core-collapse supernova (CCSN) simulations** (e.g., GR1D outputs). It is designed to:

- Automate extraction of physical quantities from simulation outputs  
- Generate publication-quality plots  
- Compute derived physical diagnostics  
- Support both **single-simulation** and **multi-simulation (comparative)** analysis  

The pipeline is extensible: new calculations and plots can be added simply by defining new modules.

---

## Directory Structure

```
project_root/
│
├── post_process.py
├── post_tasks.py
├── analysis/
│   ├── plot_shock.py
│   ├── plot_multi_shock.py
│   ├── plot_multi_neutrinos.py
│   ├── plot_multi_pns_mass.py
│   ├── plot_multi_toverw.py
│   ├── plot_multi_vturb.py
│   ├── plot_multi_vphi_flattening.py
│   ├── calc_disk_properties.py
│   └── ...
│
├── sims/
│   ├── sim1/
│   │   └── run/
│   ├── sim2/
│   │   └── run/
│   └── ...
│
└── images/
```

---

## Core Functionality

### `post_process.py`

This is the main driver script. It:

1. Discovers simulation directories  
2. Loads data using a caching system  
3. Registers analysis modules dynamically  
4. Runs:
   - Calculation tasks → outputs CSV table  
   - Plot tasks → generates figures  
5. Executes multi-simulation finalizers  

---

## Data Handling

A `DataCache` class:
- Efficiently loads `.xg` and `.dat` files  
- Avoids repeated disk reads  
- Provides structured access to time-series and profile data  

---

## Analysis Features

### 1. Shock Evolution
- Shock radius vs time 
- Multi-simulation overlay comparison

---

### 2. Neutrino Diagnostics

From:
- `M1_flux_lum.dat`
- `M1_flux_rmsenergy_lab.dat`

Produces:
- Luminosity vs time (νₑ, ν̄ₑ, νₓ)
- RMS energy vs time (νₑ, ν̄ₑ, νₓ)
- Multi-simulation overlays

---

### 3. Proto-Neutron Star (PNS) Properties

#### PNS Mass
- Computed using density matching:
  - PNS surface defined where ρ(r) = ρ_c(t)

Outputs:
- Baryonic mass vs time  
- Gravitational mass vs time  

---

### 4. Rotation and Turbulence

#### v_turb Analysis
- Max turbulent velocity vs time  
- Turbulence at:
  - Shock  
  - PNS surface (Doesn't work currently)
- Turbulent Mach number  

---



### 5. Additional Plots

- Shock velocity vs time (Work in Progress)   
- PNS radius vs time  
- Net neutrino heating vs time  
- Heating efficiency vs time  
- $T/|W|$ vs time  

---

## Output

### Plots
Saved to:
```
images/
```

### Data Table

A CSV file is generated:
```
images/simulation_results.csv
```

Includes:
- Simulation name  
- Compactness  
- Disk properties  
- Other derived quantities  

---

## How to Use

### Run on All Simulations
```
python post_process.py
```

### Run Specific Simulations
```
python post_process.py --dirs sim1 sim2
```

### Run External Directories
```
python post_process.py --dirs ../sim1 ../sim2
```

### Skip Simulations
```
python post_process.py --skip sim_to_ignore
```
### Modules Simulations
```
python post_process.py --skip-modules modules_to_ignore
```

---

## Adding New Analysis

### Add a Calculation
```python
from post_tasks import calc_task

@calc_task(files=["file.dat"])
def my_calc(sim_name, data):
    return {"value": 42}
```

### Add a Plot
```python
from post_tasks import plot_task

@plot_task(files=["file.dat"])
def my_plot(sim_name, data, images_dir):
    pass
```

### Multi-Simulation Plot
```python
def finalize(data_dict, images_dir):
    pass

my_plot.finalize = finalize
```

---

## Notes

- All time-based plots are aligned to **bounce time**  
- Many plots are restricted to **post-bounce evolution**  
- Gain-region analysis is used where physically appropriate  

---

## Summary

This pipeline provides a flexible and extensible framework for:

- CCSN simulation analysis  
- Multi-model comparison  
- Publication-quality visualization  
- Extraction of physically meaningful diagnostics  

It is designed to scale easily as new physics or analysis needs are added.
```