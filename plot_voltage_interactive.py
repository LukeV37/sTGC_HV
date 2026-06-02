import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from pathlib import Path

# Automatically discover all .txt files in the data directory
FILES = sorted((Path(__file__).parent / "data").glob("*.txt"))

BAND_1SIGMA_COLOR = "rgba(0,   180,   0, 0.35)"   # green  — inner ±1σ band
BAND_2SIGMA_COLOR = "rgba(255, 215,   0, 0.35)"   # yellow — outer ±2σ band

def load_file(path):
    # Columns separated by one or more spaces with no header
    # Columns col1-col3 and col5 are unused fields present in the data format
    df = pd.read_csv(path, sep=r'\s+', header=None,
                     names=["col1","col2","col3","channel","col5","date","time","voltage"])

    # Fix millisecond separator: "HH:MM:SS:mmm" -> "HH:MM:SS.mmm"
    # rsplit with n=1 splits only on the rightmost colon, leaving HH:MM:SS intact
    df["time"] = df["time"].str.rsplit(":", n=1).str.join(".")

    # Format: day-month-year hours:minutes:seconds.milliseconds e.g. "01-06-2026 14:32:07.453"
    df["timestamp"] = pd.to_datetime(df["date"] + " " + df["time"], format="%d-%m-%Y %H:%M:%S.%f")
    return df["timestamp"], df["voltage"], df["channel"].iloc[0]

# Load all files upfront so callbacks are fast
data = [load_file(f) for f in FILES]
channel_to_idx = {channel: i for i, (_, _, channel) in enumerate(data)}

app = Dash(__name__)

app.layout = html.Div([
    html.H2("sTGC HV Preliminary Data", style={"textAlign": "center", "marginBottom": "10px"}),

    # Controls row
    html.Div([

        html.Div([
            html.Label("Channel", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="channel-dropdown",
                options=[{"label": channel, "value": channel} for _, _, channel in data],
                value=data[0][2],
                clearable=False,
            ),
        ], style={"width": "25%", "paddingRight": "30px"}),

        html.Div([
            html.Label("Display", style={"fontWeight": "bold"}),
            dcc.RadioItems(
                id="display-radio",
                options=[
                    {"label": " Raw data",        "value": "raw"},
                    {"label": " Running average",  "value": "avg"},
                    {"label": " Both",             "value": "both"},
                ],
                value="raw",
                labelStyle={"marginRight": "18px"},
                style={"marginTop": "6px"},
            ),
        ], style={"width": "40%", "paddingRight": "30px"}),

        html.Div([
            html.Label("Window size (points)", style={"fontWeight": "bold"}),
            dcc.Input(
                id="window-input",
                type="number",
                value=50,
                min=1,
                step=1,
                debounce=True,  # only fires callback on Enter or focus-out, not every keystroke
                style={"width": "90px", "marginTop": "6px", "display": "block"},
            ),
        ], style={"width": "20%"}),

    ], style={"display": "flex", "alignItems": "flex-start", "padding": "10px 30px 20px"}),

    dcc.Graph(id="voltage-graph", style={"height": "620px"}),

], style={"fontFamily": "sans-serif", "maxWidth": "1300px", "margin": "0 auto"})


@app.callback(
    Output("voltage-graph", "figure"),
    Input("channel-dropdown", "value"),
    Input("display-radio", "value"),
    Input("window-input", "value"),
)
def update_graph(channel, display_mode, window):
    idx = channel_to_idx[channel]
    times, voltages, _ = data[idx]

    # Guard against the input field being cleared
    window = max(1, int(window or 1))

    fig = go.Figure()

    if display_mode in ("avg", "both"):
        # center=False: trailing window — point n uses the previous W points only.
        # e.g. window=50 → past 50 points. Average lags raw data by ~W/2 points.
        # Use center=True for a symmetric window (past W/2 + future W/2 points),
        # which keeps the average time-aligned but uses future values.
        rolling_avg = voltages.rolling(window=window, center=False).mean()
        rolling_std = voltages.rolling(window=window, center=False).std()

        avg_color = "crimson"

        # Bands are drawn first so raw data and average line render on top of them.
        # Draw ±2σ (yellow) first, then ±1σ (green) on top — tonexty fills from the
        # current trace down to the previous one, so order matters here
        for (lower, upper, fill_color, label) in [
            (rolling_avg - 2 * rolling_std, rolling_avg + 2 * rolling_std, BAND_2SIGMA_COLOR, "±2σ band"),
            (rolling_avg - rolling_std,     rolling_avg + rolling_std,     BAND_1SIGMA_COLOR, "±1σ band"),
        ]:
            fig.add_trace(go.Scatter(
                x=times, y=lower,
                mode="lines", line=dict(width=0),
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=times, y=upper,
                mode="lines", line=dict(width=0),
                fill="tonexty", fillcolor=fill_color,
                name=label, hoverinfo="skip",
            ))

    if display_mode in ("raw", "both"):
        # Scattergl uses WebGL rendering — much faster than Scatter for large marker datasets
        fig.add_trace(go.Scattergl(
            x=times,
            y=voltages,
            mode="markers",
            name="Raw",
            marker=dict(color="black", size=3),
        ))

    if display_mode in ("avg", "both"):
        fig.add_trace(go.Scatter(
            x=times,
            y=rolling_avg,
            mode="lines",
            name=f"{window}-pt avg",
            line=dict(color=avg_color, width=2),
        ))

    fig.update_layout(
        title=dict(text=f"sTGC HV Preliminary Data — {channel}", font=dict(size=16)),
        xaxis_title="Time",
        yaxis_title="Voltage (V)",
        hovermode="x unified",
        xaxis=dict(
            rangeslider=dict(visible=True),  # scrub bar for zooming the time window
            type="date",
        ),
        legend=dict(x=0.01, y=0.99),
        margin=dict(t=60, b=40),
    )

    return fig


if __name__ == "__main__":
    # debug=True enables hot-reload when you edit this file
    app.run(debug=True)
