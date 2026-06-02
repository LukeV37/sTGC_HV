import itertools
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Use seaborn
plt.style.use("seaborn-v0_8-whitegrid")
COLORS = ["steelblue", "darkorange", "seagreen"]

# Automatically discover all .txt files in the data directory
FILES = sorted((Path(__file__).parent / "data").glob("*.txt"))

# Load txt file into panda dataframe
def load_file(path):
    # Columns separated by one or more space with no header
    # Columns col1-col3 and col5 are unused fields present in the data format
    df = pd.read_csv(path, sep=r'\s+', header=None,
                     names=["col1","col2","col3","channel","col5","date","time","voltage"])
    # Fix millisecond separator: "HH:MM:SS:mmm" -> "HH:MM:SS.mmm"
    # rsplit with n=1 splits only on the rightmost colon, leaving HH:MM:SS intact, then join again with "."
    df["time"] = df["time"].str.rsplit(":", n=1).str.join(".")
    # Format: day-month-year hours:minutes:seconds.microseconds e.g. "01-06-2026 14:32:07.453"
    df["timestamp"] = pd.to_datetime(df["date"] + " " + df["time"], format="%d-%m-%Y %H:%M:%S.%f")
    # Return formated data
    return df["timestamp"], df["voltage"], df["channel"].iloc[0]

data = [load_file(f) for f in FILES]

# One subplot per file, stacked vertically
fig, axes = plt.subplots(len(FILES), 1, figsize=(12, 4 * len(FILES)), sharex=False)

# Single file edge case
if len(FILES) == 1:
    axes = [axes]

# Plot figure
fig.suptitle("sTGC HV Preliminary Data", fontsize=14, fontweight="bold")
for ax, (times, voltages, channel), color in zip(axes, data, itertools.cycle(COLORS)):
    ax.plot(times, voltages, linestyle='none', marker='.', markersize=2, color=color)
    ax.set_title(channel)
    ax.set_ylabel("Voltage (V)", fontsize=11)
    ax.set_xlabel("Time", fontsize=11)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d-%b"))
    ax.tick_params(axis='x', rotation=30)
    ax.grid(True, alpha=0.3)

# rect leaves room at the top for the shared suptitle
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("voltage_vs_time.png", dpi=150)
plt.show()
print("Saved voltage_vs_time.png")
