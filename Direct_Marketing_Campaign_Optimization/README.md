# Direct Marketing Campaign Response & ROI Optimization

## Project Description

This project uses the [UCI Bank Marketing dataset](https://archive.ics.uci.edu/dataset/222/bank+marketing) to build an end-to-end direct marketing targeting workflow. A financial institution ran a phone-based campaign to encourage customers to subscribe to a term deposit. The business problem is to decide which customers should be prioritized in future campaigns so the company can improve response rate, reduce low-value outreach, and protect campaign ROI.

The project connects exploratory analysis, business KPI design, classification modeling, lift analysis, and ROI-based targeting into one practical recommendation.

The campaign strategy is evaluated on these key metrics:

- Response rate
- Cost per response
- Estimated net profit
- ROI
- Lift
- Cumulative lift
- Response capture by targeting threshold

## Key Results

- The dataset has 45,211 customer contact records with an 11.7% response rate.
- Three models were compared on a held-out test set: logistic regression (baseline), random forest, and a reduced-feature random forest. The reduced-feature random forest was selected (ROC AUC 0.798, PR AUC 0.439).
- The top score decile responds at 50.1%, a 4.28x lift over the test-set average.
- The top 10% of scored customers captures 42.8% of responders, the top 20% captures 60.7%, and the top 30% captures 70.2%.
- Recommendation: target the top 20% to 30% of scored customers, or the top 10% when budget or capacity is tight.
- `duration` was excluded from modeling to prevent target leakage, because call length is only known after a customer is contacted.

ROI and profit figures in the notebook and dashboard use synthetic assumptions ($2 per contact attempt, $100 profit per response), not actual bank financials.

## File Description

- `project_notebook_dm_campaign_optimization.ipynb`: Main notebook covering data quality checks, feature engineering, EDA, modeling, lift analysis, and ROI by targeting threshold.
- `data/bank-full.csv`: Raw UCI Bank Marketing dataset used as the source data.
- `dashboard/dm_dashboard.py`: Streamlit dashboard for comparing ROI across targeting thresholds.
- `dashboard/final_lift_table.csv`, `dashboard/targeting_threshold_table.csv`: Model output tables from the notebook, used by the dashboard.
- `requirements.txt`: Dependencies for the notebook. `dashboard/requirements.txt` covers the dashboard only.

## Features

- `age`: Customer age.
- `job`: Customer occupation.
- `marital`: Marital status.
- `education`: Education level.
- `default`: Whether the customer has credit in default.
- `balance`: Average yearly account balance.
- `housing`: Whether the customer has a housing loan.
- `loan`: Whether the customer has a personal loan.
- `contact`: Contact communication type.
- `day`: Last contact day of the month.
- `month`: Last contact month of the year.
- `duration`: Last contact duration in seconds.
- `campaign`: Number of contacts during this campaign.
- `pdays`: Number of days since the customer was last contacted in a previous campaign.
- `previous`: Number of contacts before this campaign.
- `poutcome`: Outcome of the previous marketing campaign.

## Install

This project requires Python 3.x and the libraries listed in `requirements.txt`, including:

- NumPy
- pandas
- matplotlib
- seaborn
- scipy
- scikit-learn

## Interactive Dashboard

This project includes a [Streamlit dashboard](https://projectarchives-eqphssa3amgaktmwchckhp.streamlit.app/) that lets users adjust campaign assumptions and compare expected ROI across targeting thresholds.

The dashboard uses the notebook's model output tables and recalculates financial metrics based on:

- Cost per contacted customer
- Value per successful response
- Selected targeting threshold