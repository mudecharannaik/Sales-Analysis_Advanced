# Superstore Sales Analysis - Final Report

*Generated: 2026-08-25 21:41:28*

## Executive Summary

- **Total Records:** 51,290
- **Date Range:** 2011-01-01 to 2014-12-12
- **Total Sales:** $12,642,501.91
- **Total Profit:** $1,467,457.29
- **Overall Margin:** 11.61%
- **Unique Customers:** 1,590
- **Unique Products:** 10,292
- **Unique Orders:** 25,035

## Data Quality

- **Exact Duplicates:** 0
- **Key Duplicates:** 35

### Integrity Checks

| Check | Passed | Detail |
|-------|--------|--------|
| Sales > 0 | True | 0 rows with Sales <= 0 |
| Profit not null | True | 0 null Profit values |
| Discount in [0,1] | True | 0 out-of-range discounts |
| Ship Date >= Order Date | True | 0 invalid date pairs |
| Quantity > 0 | True | 0 rows with Quantity <= 0 |

## Statistical Analysis

| Test | Statistic | P-Value | Conclusion |
|------|-----------|---------|------------|
| Welch t-test (Profit: Consumer vs Corporate) | -0.19 | 0.85 | fail to reject H0 (not significant) |
| One-way ANOVA (Sales across Category) | 2,990.28 | 0.00 | reject H0 (significant) |
| Chi-square (Segment x Market) | 20.35 | 0.06 | fail to reject H0 (not significant) |
| Pearson r (Discount vs Profit) | -0.32 | 0.00 | reject H0 (significant) |
| Mann-Whitney U (Profit: Discount<=0.2 vs >) | 425,784,699.50 | 0.00 | reject H0 (significant) |

## Customer Analytics

### Repeat Customer Analysis

- **Total Customers:** 1,590
- **Repeat Customers:** 1,580
- **One-Time Customers:** 10
- **Repeat Rate:** 99.37%
- **Repeat Revenue Share:** 99.97%

### RFM Segmentation

| Segment | Count |
|---------|-------|
| Champions | 373 |
| Potential Loyalist | 310 |
| Loyal | 263 |
| Lost | 261 |
| Promising | 179 |
| At Risk | 125 |
| Recent Customer | 40 |
| Hibernating | 39 |

### Top 10 Customers by Sales

| Customer ID   |   Sales |    Profit |   Order ID | Customer Name    |   Avg Order Value |
|:--------------|--------:|----------:|-----------:|:-----------------|------------------:|
| TA-21385      | 35668.1 |  6274.99  |         25 | Tom Ashbrook     |          1426.72  |
| GT-14710      | 34471.9 |  5164.85  |         30 | Greg Tran        |          1149.06  |
| TC-20980      | 34218.3 |  8787.47  |         28 | Tamara Chand     |          1222.08  |
| SM-20320      | 31125.3 | -1083.67  |         21 | Sean Miller      |          1482.16  |
| BW-11110      | 30613.6 |  3337.47  |         35 | Bart Watters     |           874.675 |
| HL-15040      | 29664.2 |  7657.5   |         20 | Hunter Lopez     |          1483.21  |
| SE-20110      | 29532.6 |  5863.62  |         36 | Sanjit Engle     |           820.351 |
| PS-19045      | 29252.3 |  4426.2   |         26 | Penelope Sewall  |          1125.09  |
| RB-19360      | 29197.6 |  8523.95  |         25 | Raymond Buch     |          1167.91  |
| ZC-21910      | 28472.8 |   452.503 |         37 | Zuschuss Carroll |           769.536 |

## Product Analytics

### Category Performance

| Category        |       Sales |   Profit |   Discount |   Shipping Cost |   Orders |   Unique Products |   Margin % |   Avg Discount |
|:----------------|------------:|---------:|-----------:|----------------:|---------:|------------------:|-----------:|---------------:|
| Technology      | 4.74456e+06 |   663779 |   0.135342 |         49.9999 |     8354 |              2375 |      13.99 |          13.53 |
| Furniture       | 4.11087e+06 |   285205 |   0.168087 |         44.5849 |     8195 |              2228 |       6.94 |          16.81 |
| Office Supplies | 3.78707e+06 |   518474 |   0.137409 |         12.9649 |    19003 |              5689 |      13.69 |          13.74 |

### Sub-Category Deep Dive

| Sub-Category   |            Sales |   Profit |   Quantity |   Discount |   Orders |   Products |   Margin % |   Avg Order Value |   Profit per Unit |   Avg Discount % |
|:---------------|-----------------:|---------:|-----------:|-----------:|---------:|-----------:|-----------:|------------------:|------------------:|-----------------:|
| Phones         |      1.70682e+06 | 216717   |      11870 |   0.145847 |     3133 |        692 |      12.7  |            544.79 |             18.26 |            14.58 |
| Copiers        |      1.50944e+06 | 258568   |       7454 |   0.117147 |     2120 |        520 |      17.13 |            712    |             34.69 |            11.71 |
| Chairs         |      1.50168e+06 | 140396   |      12336 |   0.16311  |     3187 |        619 |       9.35 |            471.19 |             11.38 |            16.31 |
| Bookcases      |      1.46657e+06 | 161924   |       8310 |   0.153758 |     2284 |        559 |      11.04 |            642.11 |             19.49 |            15.38 |
| Storage        |      1.12709e+06 | 108461   |      16917 |   0.138464 |     4534 |        648 |       9.62 |            248.59 |              6.41 |            13.85 |
| Appliances     |      1.01106e+06 | 141681   |       6078 |   0.141709 |     1686 |        558 |      14.01 |            599.68 |             23.31 |            14.17 |
| Machines       | 779060           |  58867.9 |       4906 |   0.169583 |     1422 |        499 |       7.56 |            547.86 |             12    |            16.96 |
| Tables         | 757042           | -64083.4 |       3083 |   0.290732 |      836 |        366 |      -8.46 |            905.55 |            -20.79 |            29.07 |
| Accessories    | 749237           | 129626   |      10946 |   0.120481 |     2889 |        664 |      17.3  |            259.34 |             11.84 |            12.05 |
| Binders        | 461912           |  72449.8 |      21429 |   0.179207 |     5392 |        742 |      15.68 |             85.67 |              3.38 |            17.92 |
| Furnishings    | 385578           |  46967.4 |      11225 |   0.151066 |     2965 |        684 |      12.18 |            130.04 |              4.18 |            15.11 |
| Art            | 372092           |  57953.9 |      16301 |   0.117362 |     4366 |        673 |      15.58 |             85.22 |              3.56 |            11.74 |
| Paper          | 244292           |  59207.7 |      12822 |   0.109469 |     3234 |        781 |      24.24 |             75.54 |              4.62 |            10.95 |
| Supplies       | 243074           |  22583.3 |       8543 |   0.127918 |     2281 |        548 |       9.29 |            106.56 |              2.64 |            12.79 |
| Envelopes      | 170904           |  29601.1 |       8380 |   0.131749 |     2310 |        585 |      17.32 |             73.98 |              3.53 |            13.17 |
| Fasteners      |  83242.3         |  11525.4 |       8390 |   0.140595 |     2304 |        571 |      13.85 |             36.13 |              1.37 |            14.06 |
| Labels         |  73404           |  15010.5 |       9322 |   0.120449 |     2460 |        584 |      20.45 |             29.84 |              1.61 |            12.04 |

### Pareto Analysis

- Top 20% of products account for **70.11%** of total sales.

### Profitability Matrix

| Sub-Category   |            Sales |   Profit | Quadrant       |
|:---------------|-----------------:|---------:|:---------------|
| Accessories    | 749237           | 129626   | Stars          |
| Appliances     |      1.01106e+06 | 141681   | Stars          |
| Art            | 372092           |  57953.9 | Dogs           |
| Binders        | 461912           |  72449.8 | Cash Cows      |
| Bookcases      |      1.46657e+06 | 161924   | Stars          |
| Chairs         |      1.50168e+06 | 140396   | Stars          |
| Copiers        |      1.50944e+06 | 258568   | Stars          |
| Envelopes      | 170904           |  29601.1 | Dogs           |
| Fasteners      |  83242.3         |  11525.4 | Dogs           |
| Furnishings    | 385578           |  46967.4 | Dogs           |
| Labels         |  73404           |  15010.5 | Dogs           |
| Machines       | 779060           |  58867.9 | Question Marks |
| Paper          | 244292           |  59207.7 | Cash Cows      |
| Phones         |      1.70682e+06 | 216717   | Stars          |
| Storage        |      1.12709e+06 | 108461   | Stars          |
| Supplies       | 243074           |  22583.3 | Dogs           |
| Tables         | 757042           | -64083.4 | Question Marks |

## Geographic Analysis

### Distribution Summary

- **total_countries:** 147
- **total_states:** 1094
- **total_cities:** 3636
- **total_postal_codes:** 14138
- **total_regions:** 13
- **total_markets:** 7
- **top_country_by_sales:** United States
- **top_state_by_sales:** England
- **top_city_by_sales:** New York City

### Market Performance

| Market   |            Sales |   Profit |   Orders |   Customers |   Margin % |   Avg Order Value |
|:---------|-----------------:|---------:|---------:|------------:|-----------:|------------------:|
| APAC     |      3.58574e+06 | 436000   |     5437 |         796 |      12.16 |            659.51 |
| EU       |      2.93809e+06 | 372830   |     4593 |         795 |      12.69 |            639.69 |
| US       |      2.2972e+06  | 286397   |     5009 |         793 |      12.47 |            458.61 |
| LATAM    |      2.16461e+06 | 221643   |     5138 |         794 |      10.24 |            421.29 |
| EMEA     | 806161           |  43898   |     2462 |         760 |       5.45 |            327.44 |
| Africa   | 783773           |  88871.6 |     2232 |         754 |      11.34 |            351.15 |
| Canada   |  66928.2         |  17817.4 |      201 |         181 |      26.62 |            332.98 |

### Regional Comparison

| Region         |            Sales |   Profit |   Orders |   Customers |   Margin % |   Sales Share % |
|:---------------|-----------------:|---------:|---------:|------------:|-----------:|----------------:|
| Central        |      2.8223e+06  | 311404   |     5249 |         795 |      11.03 |           22.32 |
| South          |      1.60091e+06 | 140356   |     3270 |         776 |       8.77 |           12.66 |
| North          |      1.24817e+06 | 194598   |     2356 |         763 |      15.59 |            9.87 |
| Oceania        |      1.10018e+06 | 120089   |     1744 |         705 |      10.92 |            8.7  |
| Southeast Asia | 884423           |  17852.3 |     1517 |         672 |       2.02 |            7    |
| North Asia     | 848310           | 165578   |     1150 |         617 |      19.52 |            6.71 |
| EMEA           | 806161           |  43898   |     2462 |         760 |       5.45 |            6.38 |
| Africa         | 783773           |  88871.6 |     2232 |         754 |      11.34 |            6.2  |
| Central Asia   | 752827           | 132480   |     1026 |         570 |      17.6  |            5.95 |
| West           | 725458           | 108418   |     1611 |         686 |      14.94 |            5.74 |
| East           | 678781           |  91522.8 |     1401 |         674 |      13.48 |            5.37 |
| Caribbean      | 324281           |  34571.3 |      855 |         524 |      10.66 |            2.57 |
| Canada         |  66928.2         |  17817.4 |      201 |         181 |      26.62 |            0.53 |

## Time Series Analysis

- **Anomalies Detected:** 0
- **ARIMA Forecast Steps:** 12

## Predictive Modelling

### Random Forest Performance

- **MAE:** 34.78
- **RMSE:** 100.78
- **R2:** 0.66

### XGBoost Performance

- **MAE:** 35.70
- **RMSE:** 104.36
- **R2:** 0.63

### Top 10 Feature Importances

| Feature               |   Importance |
|:----------------------|-------------:|
| Sales                 |   0.561715   |
| Discount              |   0.283471   |
| Shipping Cost         |   0.0375339  |
| Quantity              |   0.0205802  |
| Sub-Category_Copiers  |   0.00633674 |
| Sub-Category_Machines |   0.00605258 |
| Sub-Category_Binders  |   0.00596336 |
| Sub-Category_Supplies |   0.0049061  |
| Region_South          |   0.00478772 |
| Segment_Corporate     |   0.0044823  |

## Conclusion

This report summarises the complete analysis of the Superstore dataset. All outputs (charts, SQL database, Excel workbook) are available in the project output directories.
