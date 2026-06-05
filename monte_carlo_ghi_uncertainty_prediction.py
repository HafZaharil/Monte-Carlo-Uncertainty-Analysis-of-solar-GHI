import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("MacOSX")
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

np.random.seed(42)

n_simulations = 10000

file_path = "../data/csv_24.453884_54.377344_fixed_0_0_PT60M.csv"
output_results_csv = "../results/MonteCarlo_GHI_Whole_2026.csv"

target_year = 2026
training_start_year = 2017
training_end_year = 2025

actual_col = "ghi"
clearsky_col = "clearsky_ghi"

os.makedirs("../results", exist_ok=True)


# ============================================================
# Load and prepare data
# ============================================================

df = pd.read_csv(file_path)

# Keep the timestamp hour exactly as written in the CSV.
# This avoids shifting the data because of timezone conversion.
df["time"] = (
    pd.to_datetime(df["period_end"])
    .dt.tz_localize(None)
)

df = df.set_index("time")
df = df.sort_index()

for col in [
    "dni", "clearsky_dni",
    "ghi", "clearsky_ghi",
    "dhi", "clearsky_dhi",
    "cloud_opacity", "relative_humidity",
    "air_temp", "wind_speed_10m",
    "precipitation_rate", "zenith"
]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[actual_col, clearsky_col]).copy()

df["year"] = df.index.year
df["month"] = df.index.month
df["day"] = df.index.day
df["hour"] = df.index.hour
df["date"] = df.index.date

print("\nFirst timestamp:")
print(df.index.min())

print("\nLast timestamp:")
print(df.index.max())

print("\nYears available:")
print(df["year"].value_counts().sort_index())


# ============================================================
# Calculate clear-sky factor
# ============================================================

# The clear-sky factor shows how much of the clear-sky GHI was actually received.
# A value near 1 means conditions were close to clear-sky.
# A lower value means solar radiation was reduced by weather or atmospheric effects.

df_day = df[df[clearsky_col] > 50].copy()

df_day["factor"] = df_day[actual_col] / df_day[clearsky_col]
df_day["factor"] = df_day["factor"].clip(0, 1)

print("\nClear-sky factor preview:")
print(
    df_day[[actual_col, clearsky_col, "factor"]]
    .head(30)
    .to_string()
)


# ============================================================
# Select training data
# ============================================================

train = df_day[
    (df_day["year"] >= training_start_year) &
    (df_day["year"] <= training_end_year)
].copy()

if train.empty:
    raise ValueError("Training data is empty. Check the selected year range.")

print("\nTraining range:")
print(train.index.min(), "to", train.index.max())


# ============================================================
# Historical same-hour statistics
# ============================================================

# This method uses previous years with the same month, day, and hour.
# If that exact match is unavailable, it falls back to month-hour and then hour-only statistics.

same_hour_factor_stats = (
    train
    .groupby(["month", "day", "hour"])["factor"]
    .agg(["mean", "std", "count"])
)

same_hour_factor_stats["std"] = same_hour_factor_stats["std"].fillna(0)

month_hour_factor_stats = (
    train
    .groupby(["month", "hour"])["factor"]
    .agg(["mean", "std", "count"])
)

month_hour_factor_stats["std"] = month_hour_factor_stats["std"].fillna(0)

hour_factor_stats = (
    train
    .groupby("hour")["factor"]
    .agg(["mean", "std", "count"])
)

hour_factor_stats["std"] = hour_factor_stats["std"].fillna(0)


def get_factor_stats(month, day, hour):
    key1 = (month, day, hour)
    key2 = (month, hour)

    if key1 in same_hour_factor_stats.index:
        return (
            same_hour_factor_stats.loc[key1, "mean"],
            same_hour_factor_stats.loc[key1, "std"],
            same_hour_factor_stats.loc[key1, "count"],
            "historical same month-day-hour"
        )

    elif key2 in month_hour_factor_stats.index:
        return (
            month_hour_factor_stats.loc[key2, "mean"],
            month_hour_factor_stats.loc[key2, "std"],
            month_hour_factor_stats.loc[key2, "count"],
            "historical same month-hour"
        )

    elif hour in hour_factor_stats.index:
        return (
            hour_factor_stats.loc[hour, "mean"],
            hour_factor_stats.loc[hour, "std"],
            hour_factor_stats.loc[hour, "count"],
            "historical same hour"
        )

    else:
        return 0, 0, 0, "missing"


# ============================================================
# Historical clear-sky GHI statistics
# ============================================================

# For future 2026 hours where clear-sky GHI is not available in the CSV,
# the code uses the historical median clear-sky GHI from the same time pattern.

same_hour_clearsky_stats = (
    train
    .groupby(["month", "day", "hour"])[clearsky_col]
    .agg(["median", "mean", "count"])
)

month_hour_clearsky_stats = (
    train
    .groupby(["month", "hour"])[clearsky_col]
    .agg(["median", "mean", "count"])
)

hour_clearsky_stats = (
    train
    .groupby("hour")[clearsky_col]
    .agg(["median", "mean", "count"])
)


def get_historical_clearsky(month, day, hour):
    key1 = (month, day, hour)
    key2 = (month, hour)

    if key1 in same_hour_clearsky_stats.index:
        return (
            same_hour_clearsky_stats.loc[key1, "median"],
            same_hour_clearsky_stats.loc[key1, "count"],
            "historical same month-day-hour clear-sky"
        )

    elif key2 in month_hour_clearsky_stats.index:
        return (
            month_hour_clearsky_stats.loc[key2, "median"],
            month_hour_clearsky_stats.loc[key2, "count"],
            "historical same month-hour clear-sky"
        )

    elif hour in hour_clearsky_stats.index:
        return (
            hour_clearsky_stats.loc[hour, "median"],
            hour_clearsky_stats.loc[hour, "count"],
            "historical same-hour clear-sky"
        )

    else:
        return 0, 0, "missing clear-sky"


# ============================================================
# Monte Carlo simulation
# ============================================================

def monte_carlo_single_hour(clear_sky_value, mean_factor, std_factor, n_simulations):
    factors = np.random.normal(
        loc=mean_factor,
        scale=std_factor,
        size=n_simulations
    )

    factors = np.clip(factors, 0, 1)

    simulated = clear_sky_value * factors

    return {
        "mean": np.mean(simulated),
        "median": np.median(simulated),
        "std": np.std(simulated),
        "var": np.var(simulated),
        "p05": np.percentile(simulated, 5),
        "p95": np.percentile(simulated, 95)
    }


# ============================================================
# Build the full 2026 hourly table
# ============================================================

full_2026_times = pd.date_range(
    f"{target_year}-01-01 00:00",
    f"{target_year}-12-31 23:00",
    freq="h"
)

full_2026 = pd.DataFrame(index=full_2026_times)

full_2026["year"] = full_2026.index.year
full_2026["month"] = full_2026.index.month
full_2026["day"] = full_2026.index.day
full_2026["hour"] = full_2026.index.hour
full_2026["date"] = full_2026.index.date


# ============================================================
# Add known 2026 values where available
# ============================================================

csv_2026 = df[df["year"] == target_year][
    [actual_col, clearsky_col]
].copy()

csv_2026 = csv_2026.rename(columns={
    actual_col: "Actual GHI if available (W/m²)",
    clearsky_col: "CSV Clear-sky GHI if available (W/m²)"
})

full_2026 = full_2026.join(csv_2026, how="left")


# ============================================================
# Recent 7-day rolling statistics
# ============================================================

# The rolling method uses the most recent 7 available days at the same hour.
# If actual 2026 data is not available for future hours, the predicted median
# factor is added to the rolling history for later forecasts.

rolling_factor_history = df_day[["factor"]].copy()


def get_rolling_7_day_stats(timestamp, hour):
    start_time = timestamp - pd.Timedelta(days=7)

    recent = rolling_factor_history[
        (rolling_factor_history.index >= start_time) &
        (rolling_factor_history.index < timestamp) &
        (rolling_factor_history.index.hour == hour)
    ].copy()

    if recent.empty:
        mean_factor, std_factor, count_factor, source = get_factor_stats(
            timestamp.month,
            timestamp.day,
            timestamp.hour
        )

        return mean_factor, std_factor, count_factor, "fallback to " + source

    mean_factor = recent["factor"].mean()
    std_factor = recent["factor"].std()

    if pd.isna(std_factor):
        std_factor = 0

    return mean_factor, std_factor, len(recent), "recent 7-day rolling"


# ============================================================
# Run the 2026 Monte Carlo forecast
# ============================================================

records = []

for timestamp, row in full_2026.iterrows():

    month = row["month"]
    day = row["day"]
    hour = row["hour"]

    actual_value = row["Actual GHI if available (W/m²)"]
    csv_clear_sky_value = row["CSV Clear-sky GHI if available (W/m²)"]

    if pd.notna(csv_clear_sky_value):
        clear_sky_value = csv_clear_sky_value
        clear_sky_count = 1
        clear_sky_source = "CSV 2026 clear-sky GHI"
    else:
        clear_sky_value, clear_sky_count, clear_sky_source = get_historical_clearsky(
            month,
            day,
            hour
        )

    if clear_sky_value <= 50:
        continue

    mean_1, std_1, count_1, source_1 = get_factor_stats(
        month,
        day,
        hour
    )

    mc1 = monte_carlo_single_hour(
        clear_sky_value,
        mean_1,
        std_1,
        n_simulations
    )

    mean_2, std_2, count_2, source_2 = get_rolling_7_day_stats(
        timestamp,
        hour
    )

    mc2 = monte_carlo_single_hour(
        clear_sky_value,
        mean_2,
        std_2,
        n_simulations
    )

    if pd.isna(actual_value):
        rolling_factor_history.loc[timestamp, "factor"] = (
            mc2["median"] / clear_sky_value
        )

    records.append({
        "Time": timestamp,
        "Date": timestamp.date(),
        "Hour": hour,

        "Actual GHI if available (W/m²)": actual_value,
        "Clear-sky GHI used (W/m²)": clear_sky_value,
        "Clear-sky source": clear_sky_source,
        "Clear-sky count": clear_sky_count,

        "Historical same-hour stats source": source_1,
        "Historical same-hour factor mean": mean_1,
        "Historical same-hour factor std": std_1,
        "Historical same-hour factor count": count_1,
        "Historical same-hour MC mean GHI (W/m²)": mc1["mean"],
        "Historical same-hour MC median GHI (W/m²)": mc1["median"],
        "Historical same-hour MC std GHI (W/m²)": mc1["std"],
        "Historical same-hour MC variance GHI (W/m²)²": mc1["var"],
        "Historical same-hour MC 5th percentile GHI (W/m²)": mc1["p05"],
        "Historical same-hour MC 95th percentile GHI (W/m²)": mc1["p95"],

        "Recent 7-day rolling stats source": source_2,
        "Recent 7-day rolling factor mean": mean_2,
        "Recent 7-day rolling factor std": std_2,
        "Recent 7-day rolling factor count": count_2,
        "Recent 7-day rolling MC mean GHI (W/m²)": mc2["mean"],
        "Recent 7-day rolling MC median GHI (W/m²)": mc2["median"],
        "Recent 7-day rolling MC std GHI (W/m²)": mc2["std"],
        "Recent 7-day rolling MC variance GHI (W/m²)²": mc2["var"],
        "Recent 7-day rolling MC 5th percentile GHI (W/m²)": mc2["p05"],
        "Recent 7-day rolling MC 95th percentile GHI (W/m²)": mc2["p95"],
    })

results = pd.DataFrame(records)

print("\nForecast results preview:")
print(results.head(50).to_string(index=False))


# ============================================================
# Export results
# ============================================================

results.to_csv(output_results_csv, index=False)

print(f"\nMonte Carlo results exported to:\n{output_results_csv}")
