#!/usr/bin/env python
# coding: utf-8

import pathlib
import time
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import hvsrpy

plt.style.use(hvsrpy.HVSRPY_MPL_STYLE)

# -------------------------------------------------------
# Directory containing MiniSEED files
# -------------------------------------------------------
data_dir = pathlib.Path("AlpARRAY/SDS_YT")

# -------------------------------------------------------
# Group HHE, HHN and HHZ belonging to the same recording
# -------------------------------------------------------
groups = defaultdict(dict)

for f in sorted(data_dir.glob("*.MSEED")):

    # Example filename:
    # Z3.A369A.2020.343.00.HHE.MSEED

    parts = f.stem.split(".")
    # ['Z3','A369A','2020','343','00','HHE']

    key = ".".join(parts[:-1])   # Z3.A369A.2020.343.00
    channel = parts[-1]          # HHE

    groups[key][channel] = str(f)

# Build hvsrpy input
fnames = []
measurement_names = []

for key in sorted(groups):

    channels = groups[key]

    if {"HHE", "HHN", "HHZ"} <= channels.keys():

        fnames.append([[
            channels["HHE"],
            channels["HHN"],
            channels["HHZ"],
        ]])

        measurement_names.append(key)

    else:
        print(f"Skipping {key}: missing component(s)")

print(f"\nFound {len(fnames)} complete three-component recordings.\n")

for idx, files in enumerate(fnames, start=1):
    print(f"Measurement {idx}:")
    for f in files[0]:
        print("   ", pathlib.Path(f).name)

# -------------------------------------------------------
# Preprocessing settings
# -------------------------------------------------------
preprocessing_settings = hvsrpy.settings.HvsrPreProcessingSettings()
preprocessing_settings.detrend = "linear"
preprocessing_settings.window_length_in_seconds = 60
preprocessing_settings.orient_to_degrees_from_north = 0.0
preprocessing_settings.filter_corner_frequencies_in_hz = (None, None)
preprocessing_settings.ignore_dissimilar_time_step_warning = False

print("\nPreprocessing Summary")
print("-" * 60)
preprocessing_settings.psummary()

# -------------------------------------------------------
# Processing settings
# -------------------------------------------------------
processing_settings = hvsrpy.settings.HvsrTraditionalProcessingSettings()
processing_settings.window_type_and_width = ("tukey", 0.2)

processing_settings.smoothing = dict(
    operator="konno_and_ohmachi",
    bandwidth=40,
    center_frequencies_in_hz=np.geomspace(0.2, 25, 300),
)

processing_settings.method_to_combine_horizontals = "geometric_mean"
processing_settings.handle_dissimilar_time_steps_by = (
    "frequency_domain_resampling"
)

print("\nProcessing Summary")
print("-" * 60)
processing_settings.psummary()

# -------------------------------------------------------
# Compute HVSR
# -------------------------------------------------------
hvsrs = []

for idx, files in enumerate(fnames, start=1):

    print(f"\nMeasurement {idx}: {measurement_names[idx-1]}")

    start = time.perf_counter()

    srecords = hvsrpy.read(files)

    srecords = hvsrpy.preprocess(
        srecords,
        preprocessing_settings,
    )

    hvsr = hvsrpy.process(
        srecords,
        processing_settings,
    )

    # Cox et al. (2020)
    hvsrpy.frequency_domain_window_rejection(
        hvsr,
        n=2,
        search_range_in_hz=(None, None),
    )

    hvsrs.append(hvsr)

    end = time.perf_counter()

    print(f"Completed in {end-start:.1f} seconds.")

# -------------------------------------------------------
# Output directory
# -------------------------------------------------------
output_dir = pathlib.Path("HVSR_Output")
output_dir.mkdir(exist_ok=True)

# -------------------------------------------------------
# Save figures and results
# -------------------------------------------------------
for idx, hvsr in enumerate(hvsrs, start=1):

    print(f"\nResults for {measurement_names[idx-1]}")

    print("\nStatistical Summary")
    print("-" * 30)
    hvsrpy.summarize_hvsr_statistics(hvsr)

    fig, ax = hvsrpy.plot_single_panel_hvsr_curves(hvsr)

    if ax.get_legend() is not None:
        ax.get_legend().remove()

    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    basename = measurement_names[idx-1]

    figure_name = output_dir / f"{basename}.png"
    csv_name = output_dir / f"{basename}.csv"

    fig.savefig(figure_name, dpi=300, bbox_inches="tight")
    plt.close(fig)

    hvsrpy.object_io.write_hvsr_object_to_file(
        hvsr,
        str(csv_name),
    )

    print(f"Saved figure : {figure_name}")
    print(f"Saved results: {csv_name}")

print("\nDone.")
