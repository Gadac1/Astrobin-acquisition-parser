import os
import re
import csv
import sys
from datetime import datetime, timedelta
from collections import defaultdict

# =====================================================
# CONFIGURATION
# =====================================================

GAIN = 100.0
BINNING = 0
F_NUMBER = 5.60
TEMPERATURE = -10

DARKS = 30
FLATS = 20
BIAS = 60

BORTLE = 8
MEAN_SQM = 17.80

# AstroBin filter definitions
FILTERS = {
    "H": {
        "id": 29144,
        "name": "ToupTek H-alpha 3.5nm 36 mm"
    },
    "O": {
        "id": 29472,
        "name": "ToupTek OIII 4nm 36 mm"
    },
    "S": {
        "id": 29471,
        "name": "ToupTek SII 4nm 36 mm"
    }
}

# =====================================================
# ROOT DIRECTORY = LOCATION OF SCRIPT
# =====================================================

if getattr(sys, "frozen", False):
    ROOT_DIRECTORY = os.path.dirname(sys.executable)
else:
    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

print(f"Root directory: {ROOT_DIRECTORY}")

# =====================================================
# FILENAME FORMAT
#
# Example:
# 2026-05-26_02-01-12_H_-5.00_300.00s_1.83_4.12_0004.fit
# =====================================================

pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})_"
    r"\d{2}-\d{2}-\d{2}_"
    r"(?P<filter>[HOS])_"
    r"(?P<temp>-?\d+\.\d+)_"
    r"(?P<duration>\d+\.\d+)s",
    re.IGNORECASE
)

# Key:
# (date, filter, temp, duration)
exposure_data = defaultdict(int)

# =====================================================
# SEARCH FOR LIGHTS FOLDERS
# =====================================================

for root, dirs, files in os.walk(ROOT_DIRECTORY):

    if os.path.basename(root).lower() != "lights":
        continue

    print(f"Processing lights folder: {root}")

    for filename in files:

        match = pattern.search(filename)

        if not match:
            continue

        # Shift date back one day to represent
        # the beginning of the astronomical night
        original_date = match.group("date")

        shifted_date = (
            datetime.strptime(original_date, "%Y-%m-%d")
            - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        filter_code = match.group("filter").upper()
        temperature = TEMPERATURE
        duration = int(round(float(match.group("duration"))))

        key = (
            shifted_date,
            filter_code,
            temperature,
            duration
        )

        exposure_data[key] += 1

# =====================================================
# WRITE CSV
# =====================================================

output_csv = os.path.join(
    ROOT_DIRECTORY,
    "astrobin_acquisition.csv"
)

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "date",
        "filter",
        "filterName",
        "number",
        "duration",
        "binning",
        "gain",
        "sensorCooling",
        "fNumber",
        "darks",
        "flats",
        "bias",
        "bortle",
        "meanSqm"
    ])

    for (
        date,
        filter_code,
        temperature,
        duration
    ), count in sorted(exposure_data.items()):

        filter_info = FILTERS[filter_code]

        writer.writerow([
            date,
            filter_info["id"],
            filter_info["name"],
            count,
            duration,
            BINNING,
            f"{GAIN:.2f}",
            TEMPERATURE,
            f"{F_NUMBER:.2f}",
            DARKS,
            FLATS,
            BIAS,
            BORTLE,
            f"{MEAN_SQM:.2f}"
        ])

print()
print(f"CSV written successfully:")
print(output_csv)
print()
print(f"Rows written: {len(exposure_data)}")
