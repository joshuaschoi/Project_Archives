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

The final recommendation is to use a reduced-feature random forest response model to rank customers by predicted response probability and target the top 20% to 30% of customers for the next campaign.

## File Description

- `Raw/bank-full.csv`: Raw UCI Bank Marketing dataset used as the source data.

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

Run the dashboard locally from the top-level project directory:

```bash
streamlit run streamlit_app.py
```

The dashboard uses the Project 1 model output tables in `data/processed/` and recalculates financial metrics based on:

- Cost per contacted customer
- Value per successful response
- Selected targeting threshold

When deployed to Streamlit Community Cloud, use `streamlit_app.py` as the app entrypoint.




Important modeling note: `duration` is excluded from the predictive modeling dataset because call duration is only known after a customer has already been contacted. Including it would create target leakage for a pre-campaign targeting model.

## Target Variable

- `y`: Whether the customer subscribed to a term deposit.
- `response_flag`: Binary target created from `y`, where `1` means the customer subscribed and `0` means the customer did not subscribe.

The positive response rate is about `11.7%`, making this an imbalanced classification problem.

## Business Assumptions

The UCI dataset does not include actual campaign cost or profit data. To estimate ROI, this project uses simple assumptions:

- Each customer contact attempt costs `$2`.
- Each successful term deposit subscription creates `$100` in expected profit.

These assumptions are not actual bank financials. They are used to translate model scores into business-facing metrics such as estimated net profit, ROI, and cost per response.

## Methods

The notebook follows this workflow:

1. Load and inspect the raw campaign data.
2. Create the binary response target and business KPI fields.
3. Exclude leakage-sensitive fields before modeling.
4. Analyze campaign KPIs by contact count, prior outcome, channel, and month.
5. Analyze response and ROI by demographic and financial segments.
6. Build and compare logistic regression, full random forest, and reduced-feature random forest models.
7. Evaluate models with ROC AUC, PR AUC, F1, lift, and response capture.
8. Convert model scores into targeting thresholds.
9. Estimate ROI and cost per response by targeting threshold.
10. Translate the analysis into a campaign recommendation.

## Key Findings

Overall campaign performance under the project assumptions:

- Contacted customers: `45,211`
- Responses: `5,289`
- Response rate: `11.7%`
- Estimated contact cost: `$249,912`
- Estimated gross profit: `$528,900`
- Estimated net profit: `$278,988`
- Estimated ROI: `111.6%`

Strong response patterns:

- Prior campaign success: `64.7%` response rate
- March contacts: `52.0%` response rate
- Cellular contact: `14.9%` response rate
- One-contact customers: `14.6%` response rate
- Students: `28.7%` response rate
- Retired customers: `22.8%` response rate

Weak response patterns:

- Unknown contact channel: `4.1%` response rate
- Customers with 6+ contact attempts: `5.8%` response rate
- Negative balance customers: `5.6%` response rate
- Customers with both housing and personal loans: `6.1%` response rate

## Modeling Results

The reduced-feature random forest was selected because it produced the strongest ranking performance for campaign targeting:

- ROC AUC: `0.798`
- PR AUC: `0.439`
- Top-decile response rate: `50.1%`
- Top-decile lift: `4.28x`
- Top-20% response capture: `60.7%`

## Recommendation

Use the model to prioritize the top 20% to 30% of customers by predicted response probability.

| Targeting Threshold | Response Rate | Lift | Captured Responders | ROI | Cost per Response |
| --- | ---: | ---: | ---: | ---: | ---: |
| Top 10% | 50.1% | 4.28x | 42.8% | 24.0x | $4.00 |
| Top 20% | 35.5% | 3.03x | 60.7% | 16.7x | $5.64 |
| Top 30% | 27.4% | 2.34x | 70.2% | 12.7x | $7.30 |

The top 10% is best when contact capacity is highly constrained. The top 20% gives the best balance of efficiency and scale. The top 30% is useful when the business wants broader reach while still performing meaningfully above the campaign average. 

## Caveats

- ROI is based on synthetic assumptions and should be replaced with actual campaign economics before production use.
- The dataset is public and historical, so a production model would need validation on newer campaign data.
- The final targeting recommendation should ideally be tested in a future randomized campaign.
