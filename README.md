# Monte Carlo-Based Solar Irradiance Uncertainty Analysis

This project applies Monte Carlo simulation to analyse hourly solar irradiance uncertainty using historical and recent solar radiation data.

The work focuses on Global Horizontal Irradiance (GHI) prediction uncertainty. Instead of predicting one exact future irradiance value, the method estimates a statistical range of possible GHI outcomes using historical clear-sky-normalised behaviour.

The Monte Carlo results are validated against unseen GHI data from **23, 24, and 25 May 2026**. The results shows that R^2 values for each of the 23, 24 and 25 of May 2026 amount to 

---

## Project Overview

This project uses Monte Carlo simulation to estimate short-term solar irradiance uncertainty by predicting a range of possible GHI outcomes using historical same-hour and recent 7-day rolling data.

For each hourly timestep, the model estimates:

- Mean GHI
- Median GHI
- 5th percentile GHI
- 95th percentile GHI

Two Monte Carlo approaches are compared:

1. Historical Same-Hour Method
2. Recent 7-Day Rolling Method

The results are then compared against unseen measured GHI data which are the data on the 23rd until 25th of May. 

---

## Data Source

The solar irradiance data were obtained from a time-series dataset for the Abu Dhabi region.

The main variables used in this project are:

- **GHI** — Global Horizontal Irradiance
- **Clear-sky GHI** — theoretical GHI under clear-sky conditions
- **Time** — hourly timestep

Night-time and very low solar input periods were excluded using:

```text
Clear-sky GHI > 50 W/m²```


## Data Preprocessing

The time-series data were cleaned and prepared before the Monte Carlo analysis.

The main preprocessing steps were:

* Load hourly GHI and clear-sky GHI data
* Keep the timestamp hour consistent with the source time-series file
* Remove invalid or missing values
* Remove night-time and near-zero solar hours
* Calculate the clear-sky factor for every valid hour

The clear-sky factor is defined as:
```Clear-sky factor = Actual GHI / Clear-sky GHI```
