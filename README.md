# NSV_HVSR_AlpARRAY
Scripts to compute NSV and HVSR from AlpARRAY

For Near Surface Velocity (NSV)

(1) NSV_extract_values.py: Extract values from RF SAC headers, and compute NSV

(2) NSV_compute_average.sh: Compute average NSV at each seismic station

For Horizontal-to-Vertical Ratio (HVSR
(1) HVSR_download_data.py: Download 2 hour long miniseed files for 5 consecutive days
(2) HVSR_compute.py: Compute HVSR (using hvsrpy https://github.com/jpvantassel/hvsrpy)
(3) HVSR_extract_values: Extract peak amplification, fundamental frequency
