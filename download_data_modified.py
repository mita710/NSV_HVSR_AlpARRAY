from obspy import UTCDateTime, read_inventory
from obspy.clients.fdsn import RoutingClient
import os

# -----------------------
# CONFIG
# -----------------------

# Glob pattern (or single path) pointing to your local StationXML file(s)
# defining the station list to download.
STATIONXML_PATH = "staxmlfiles/*.xml"

CHANNELS = ["HHE", "HHZ", "HHN"]

OUTPUT_DIR = "SDS_YT"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Length of each downloaded segment, in hours. HVSR just needs enough
# continuous, quiet data per window; 2h chunks keep file sizes manageable
# while giving consistent, comparable windows day to day.
CHUNK_HOURS = 2

# -----------------------
# 5 CONSECUTIVE DAYS
# -----------------------
# Option 1: Year + Julian Day
START_DATE = UTCDateTime(year=2020, julday=339)

# Option 2 (alternative): Calendar date
# START_DATE = UTCDateTime("2010-12-05T00:00:00")

N_DAYS = 5

days = [UTCDateTime((START_DATE + i * 86400).date) for i in range(N_DAYS)]

# -----------------------
# CLIENT
# -----------------------
client = RoutingClient("eida-routing")

# -----------------------
# READ STATION LIST
# -----------------------
print(f"Reading station inventory from {STATIONXML_PATH} ...")
inventory = read_inventory(STATIONXML_PATH)

# -----------------------
# LOOP: stations -> days -> chunks -> channels
# -----------------------
for net in inventory:
    for sta in net:

        net_code = net.code
        sta_code = sta.code

        print(f"\nProcessing {net_code}.{sta_code}")

        for day_start in days:
            day_end = day_start + 7200

            print(f"  Day: {day_start.date}")

            t = day_start
            while t < day_end:
                t_next = min(t + CHUNK_HOURS * 3600, day_end)

                for channel in CHANNELS:

                    filename = (
                        f"{net_code}.{sta_code}.{t.year}.{t.julday:03d}."
                        f"{t.hour:02d}.{channel}.SAC"
                    )
                    filepath = os.path.join(OUTPUT_DIR, filename)

                    if os.path.exists(filepath):
                        continue

                    try:
                        print(f"    Downloading {filename}")

                        st = client.get_waveforms(
                            network=net_code,
                            station=sta_code,
                            location="*",
                            channel=channel,
                            starttime=t,
                            endtime=t_next,
                        )

                        if len(st) == 0:
                            print("      No data")
                            continue

                        st.write(filepath, format="SAC")
                        print(f"      Saved: {filename}")

                    except Exception as e:
                        print(f"      Failed: {e}")

                t = t_next
