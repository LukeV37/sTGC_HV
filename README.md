# sTGC HV Data Viewer

Visualization tools for sTGC (small-strip Thin Gap Chamber) high-voltage monitoring data. Supports both a static multi-panel plot and an interactive web app with a rolling average and uncertainty bands.

---

## Quick Start

```bash
cd HV_data
source setup.sh
```

Static plot (saves `voltage_vs_time.png`):
```bash
python plot_voltage_static.py
```

Interactive web app (open `http://127.0.0.1:8050`):
```bash
python plot_voltage_interactive.py
```

---

## Data Files

Place raw HV data files in the `data/` subdirectory. Each file is whitespace-delimited with no header. The scripts expect these specific files:

```
data/
├── EIZ1R1C07L2_iMon_2026.txt
├── EIZ4R3A03L2_iMon_2026.txt
└── EIZ4R3A03L3_iMon_2026.txt
```

To add or swap channels, edit the `FILES` list at the top of either script.

---

## Scripts

### `plot_voltage_static.py`
Renders one subplot per channel, stacked vertically. Each panel shows raw voltage as small dots. Output is saved as `voltage_vs_time.png` and displayed interactively.

### `plot_voltage_interactive.py`
A Dash web app with per-channel controls:

| Control | Description |
|---|---|
| **Channel** | Select which HV channel to display |
| **Display** | Raw data, running average, or both |
| **Window size** | Number of points for the rolling average |

When the running average is shown, uncertainty bands are overlaid:
- **±1σ** — green inner band
- **±2σ** — yellow outer band

The rolling window is trailing (not centred), so the average uses only past data points and lags the raw signal by roughly half the window size.

The raw data trace uses WebGL rendering (`go.Scattergl`) for fast browser performance on large datasets.

---

## Dependencies

```
pandas      # data loading and rolling statistics
matplotlib  # static plot
plotly      # interactive traces
dash        # web app framework
```

All managed by `setup.sh` via `requirements.txt`.
