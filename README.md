# Monte Carlo-Based Solar Irradiance Uncertainty Analysis

This project applies Monte Carlo simulation to analyse and predict hourly solar irradiance uncertainty using historical and recent solar radiation data.

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

# 1. Methodology

## 1.1 Data Source

The solar irradiance data were obtained from a time-series dataset for the Abu Dhabi region from solcast.

The main variables used in this project are:

- **GHI** — Global Horizontal Irradiance
- **Clear-sky GHI** — theoretical GHI under clear-sky conditions
- **Time** — hourly timestep

Night-time and very low solar input periods were excluded using:

```text
Clear-sky GHI > 50 W/m²
```


## 1.2 Data Preprocessing

The time-series data were cleaned and prepared before the Monte Carlo analysis.

The main preprocessing steps were:

* Load hourly GHI and clear-sky GHI data
* Keep the timestamp hour consistent with the source time-series file
* Remove invalid or missing values
* Remove night-time and near-zero solar hours
* Calculate the clear-sky factor for every valid hour

The clear-sky factor is defined as:
```Clear-sky factor = Actual GHI / Clear-sky GHI```

where the clear-sky factor is in the range of 0 ≤ Clear-sky factor ≤ 1
This factor represents the reduction in solar radiation caused by atmospheric conditions such as cloud cover and opacity, haze, dust, and general weather variability.
that reduces the GHI relative its to theoretical maximum (Clear Sky)


## 1.3 Monte Carlo Methods

Two different data-driven Monte Carlo methods were used.

### Method 1: Historical Same-Hour Method

The Historical Same-Hour Method uses long-term historical behaviour.

For each target hour, historical clear-sky factors were selected using the same:

```
Month
Day
Hour
```

from previous years.

This method represents long-term solar behaviour for a specific calendar date and hour.

### Method 2: Recent 7-Day Rolling Method

The Recent 7-Day Rolling Method uses short-term recent behaviour.

For each target hour, clear-sky factors from the previous 7 available days at the same hour were used.

The selected recent factors were then used to calculate:

* Mean factor
* Standard deviation factor
* Sample count

This method captures recent weather persistence and short-term atmospheric behaviour.

## 1.4 Monte Carlo Simulation Procedure

For each target hour, 10,000 Monte Carlo samples were generated.

The clear-sky factor was sampled using:
```Factor ~ Normal(mean factor, standard deviation factor)```

The sampled factors were then limited to:
```0 ≤ Factor ≤ 1```

The simulated GHI was calculated as:
```Simulated GHI = Factor × Clear-sky GHI```

From the 10,000 simulated values, the following statistical outputs were extracted:

* Mean
* Median
* 5th percentile
* 95th percentile

The 5th and 95th percentiles represent the lower and upper uncertainty boundaries.

## 1.5 Unseen Validation Data

The Monte Carlo outputs were evaluated using unseen GHI measurements from:
```
23 May 2026
24 May 2026
25 May 2026
```
These dates were used only for validation and comparison.

The purpose of the validation was to assess how well the Monte Carlo statistical outputs match the actual observed GHI pattern.


## 1.6 Evaluation Metric

The main evaluation metric used in this project is:

```R²```

The R² value was calculated between the actual GHI and each Monte Carlo prediction case.

The analysis focuses on R² because the main objective is to assess how well the predicted GHI trend follows the actual measured GHI.

---

# 2.0 Results and Disucssion

## R² Results

| Date | Historical same-hour mean | Historical same-hour median | Historical same-hour 5th percentile | Historical same-hour 95th percentile | Recent 7-day rolling mean | Recent 7-day rolling median | Recent 7-day rolling 5th percentile | Recent 7-day rolling 95th percentile |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 23 May 2026 | 0.946 | 0.951 | 0.895 | 0.963 | 0.960 | 0.961 | 0.950 | 0.963 |
| 24 May 2026 | 0.927 | 0.939 | 0.774 | 0.971 | 0.965 | 0.966 | 0.950 | 0.971 |
| 25 May 2026 | 0.937 | 0.952 | 0.708 | 0.983 | 0.977 | 0.978 | 0.963 | 0.983 |


## Discussion
The results above show that there is strong correlation for all methods againts unseen data of the three days, wit hthe exception of the the 5th percentile, proving that the historical data tend to be bias upward. It can be seen that the recent 7-day rolling method tend to show better fit relative to the historical same-hour method, but the difference is small, proving that both methods is quite suitable to be used to predict GHI with resonable accuracy. 

The figures below shows the visualisation of the comparisons between the two examined monte carlo methods agaisnt real data of the three days from 23rd to 25th of May 2026.

23rd May
<img width="7040" height="3436" alt="2026_05_23_figure_1_mean_median" src="https://github.com/user-attachments/assets/ad7f18b4-ced0-48ce-a372-30c78b9487fe" />
<img width="7040" height="3436" alt="2026_05_23_figure_2_percentile_lines" src="https://github.com/user-attachments/assets/849774ec-a87c-4957-8c2d-64659a9f8650" />

24th May
<img width="7040" height="3436" alt="2026_05_24_figure_1_mean_median" src="https://github.com/user-attachments/assets/aa607155-c4c2-46ec-a7b5-8d7e5de692ca" />
<img width="7040" height="3436" alt="2026_05_24_figure_2_percentile_lines" src="https://github.com/user-attachments/assets/8cd262d3-6bdd-422e-b90c-6ac79ee582dd" />

25th May
<img width="7040" height="3436" alt="2026_05_25_figure_1_mean_median" src="https://github.com/user-attachments/assets/c31f5d4c-ef3d-4b2b-abab-396e3b2df274" />
<img width="7040" height="3436" alt="2026_05_25_figure_2_percentile_lines" src="https://github.com/user-attachments/assets/59889b9d-1aee-4684-8c18-cbce32995e56" />


