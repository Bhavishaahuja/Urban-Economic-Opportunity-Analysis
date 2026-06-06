# Urban Economic Opportunity Analysis

**Course:** CS 418: Data Science | University of Illinois Chicago | Spring 2025  
**Author:** Bhavisha Ahuja (+ team: Muhammad, Filip, Rohit, Dima)

---

## Overview

Analyzes socioeconomic disparities across 4,406 census tracts in Chicago, New York City, Dallas, and Oklahoma City using ACS 5-Year Estimates (2019–2023). The project builds an end-to-end data pipeline — from automated Census API retrieval to predictive modeling — to identify which factors most effectively predict neighborhood-level poverty.

**Key finding:** Household income and city-level effects are the dominant drivers of poverty rate. Ensemble models (Random Forest R²=0.61) outperform linear regression (R²=0.56), suggesting poverty is shaped by non-linear interactions between income, education, and geography.

---

## Pipeline

Census Bureau ACS API → acs\_data\_retrieval.py → urban\_economic\_opportunity\_data.csv → EDA.ipynb → Prediction\_Model.ipynb

---

## Dataset

Data retrieved via U.S. Census Bureau ACS 5-Year API. Custom Python script automates collection and derives key indicators across all census tracts in 4 metro areas.

| Variable | Description |
| :---- | :---- |
| `GEOID` | Unique 11-digit census tract identifier |
| `City` | Metro area (Chicago, NYC, Dallas, Oklahoma City) |
| `Poverty_Rate` | % of population below federal poverty threshold |
| `Unemployment_Rate` | % of civilian labor force unemployed |
| `Bachelors_Plus_Rate` | % of adults 25+ with bachelor's degree or higher |
| `Median_Household_Income` | Midpoint household income for the tract |
| `Mean_Travel_Time_Minutes` | Average one-way commute time (minutes) |

---

## Models Compared

| Model | Test R² | MAE | CV Score |
| :---- | :---- | :---- | :---- |
| Multiple Linear Regression (baseline) | 0.5618 | 5.69 pp | 0.5674 ± 0.027 |
| XGBoost Regressor | 0.5927 | 5.14 pp | 0.6190 ± 0.026 |
| Gradient Boosting Regressor | 0.5870 | 5.14 pp | 0.6235 ± 0.028 |
| **Random Forest Regressor (best)** | **0.6065** | **5.22 pp** | **0.6096 ± 0.024** |

All models evaluated with train/test split \+ 5-fold cross-validation. Random Forest achieved the highest test R²; Gradient Boosting showed the strongest CV consistency.

---

## Key Findings

- **Income is the strongest predictor** — log-transformed household income showed the largest negative relationship with poverty rate across all models  
- **City effects matter** — even after controlling for income and education, poverty rates varied significantly across metro areas  
- **Education is a secondary driver** — higher Bachelor's+ rates correspond to lower poverty, but the relationship is weaker than income  
- **Commute time has minimal predictive power** — weak relationship with poverty after controlling for other factors  
- **NYC and Chicago vs. Dallas and Oklahoma City** — "Blue" cities show higher educational attainment at equivalent income levels

---

## EDA Highlights

- Right-skewed income distribution consistent with national U.S. patterns  
- Extreme poverty concentration at the low end of the income distribution (confirmed via hexbin density plot)  
- Strong negative correlation between income and poverty rate (-0.77), moderate negative correlation with education (-0.49)  
- Commute time correlation with poverty is weak (-0.19)

---

## My Contributions

- Correlation analysis and feature refinement — built the full correlation matrix, removed low-signal predictors, finalized the feature set  
- Expanded modeling section — implemented Random Forest and Gradient Boosting beyond the course-required linear regression baseline  
- Rewrote analytical interpretation — justified target variable switch (unemployment → poverty rate), comparative model discussion, key predictor interpretation  
- Visualization updates — model performance comparison chart, MLR coefficient plot, residual plots  
- Drafted final presentation slides and "Possible Improvements" section

---

## Files

| File | Description |
| :---- | :---- |
| `acs_data_retrieval.py` | Automated ACS API data collection script |
| `EDA.ipynb` | Exploratory data analysis with visualizations |
| `Prediction_Model.ipynb` | Model training, evaluation, and comparison |
| `urban_economic_opportunity_data.csv` | Cleaned dataset (4,406 census tracts) |
| `CS 418 Final Report - Bhavisha Ahuja.pdf` | Full written report |
| `CS418 project proposal.pdf` | Original project proposal |

---

## Tech Stack

Python · pandas · scikit-learn · XGBoost · matplotlib · seaborn · U.S. Census Bureau ACS API · Jupyter Notebook  
