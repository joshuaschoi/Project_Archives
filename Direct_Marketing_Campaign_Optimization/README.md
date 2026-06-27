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

## File Description

- `data/bank-full.csv`: Raw UCI Bank Marketing dataset used as the source data.

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

This project includes a Streamlit dashboard that lets users adjust campaign assumptions and compare expected ROI across targeting thresholds.

The dashboard uses the Project 1 model output tables and recalculates financial metrics based on:

- Cost per contacted customer
- Value per successful response
- Selected targeting threshold