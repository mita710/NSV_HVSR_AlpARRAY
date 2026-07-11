import os
import glob
import numpy as np
import pandas as pd

# --------------------------------------------------
# Auto-detect all station files:
# values_<station>.txt  OR values-<station>.txt
# --------------------------------------------------

base_dir = os.getcwd()

# Find matching files
files = glob.glob("values_*.txt") + glob.glob("values-*.txt")

print(f"Found {len(files)} station files")

# --------------------------------------------------
# Process each file automatically
# --------------------------------------------------

for filepath in files:

    filename = os.path.basename(filepath)

    # Extract station name
    # values_Z3.A434A.txt -> Z3.A434A
    # values-Z3.A434A.txt -> Z3.A434A
    sta = filename.replace("values_", "").replace("values-", "").replace(".txt", "")

    try:
        # Read numeric columns only (skip first string column)
        data = np.loadtxt(filepath, usecols=(1, 2, 3, 4))

        # If file has only one row, reshape
        if data.ndim == 1:
            data = data.reshape(1, -1)

        lat = data[:, 0]
        lon = data[:, 1]
        p   = data[:, 2]
        a   = data[:, 3]

        # ------------------------------------------
        # Calculations
        # ------------------------------------------
        pi  = p / 111.19
        ah  = a / 3.99
        tn  = np.degrees(np.arctan(ah))
        tnd = tn * 0.5
        sn  = np.sin(np.radians(tnd))
        vsf = sn / pi

        # ------------------------------------------
        # Save outputs
        # ------------------------------------------
        df = pd.DataFrame({
            'lat': lat,
            'lon': lon,
            'p': p,
            'a': a,
            'tn': tn,
            'tnd': tnd,
            'sn': sn,
            'vsf': vsf
        })

        csv_out = f"derived_{sta}.csv"
        txt_out = f"derived_{sta}.txt"

        df.to_csv(csv_out, index=False)
        np.savetxt(txt_out, df.values, fmt="%.6f", delimiter=" ")

        print(f"Processed {sta}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")
