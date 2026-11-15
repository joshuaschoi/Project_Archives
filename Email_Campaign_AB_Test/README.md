# Email Campaign A/B Test: Measuring Incremental Customer Spend

## Project Description

This project analyzes a real randomized retail email experiment from the [MineThatData E-Mail Analytics and Data Mining Challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html). Customers were randomly assigned to one of three groups: receive a Mens merchandise email, receive a Womens merchandise email, or receive no email.

The business question is intentionally direct:

> Did sending a promotional email increase customer spend within two weeks compared with sending no email?

This project focuses on the core A/B testing workflow: define treatment and control, validate the experiment setup, choose success and guardrail metrics, run statistical tests, interpret uncertainty, and make a business recommendation.

The experiment is evaluated on one primary success metric:

- Spend per customer

Supporting metrics include:

- Visit rate
- Conversion rate
- Spend per buyer
- Incremental spend per customer

## Key Results

- 64,000 customers were split evenly across three groups, and pre-campaign attributes were balanced across them.
- Spend per customer was $1.42 for the Mens email and $1.08 for the Womens email, versus $0.65 with no email.
- Incremental spend per customer versus control: $0.77 for the Mens email (95% bootstrap CI $0.48 to $1.05) and $0.42 for the Womens email ($0.17 to $0.69). Both are significant under a one-sided Welch's t-test.
- The Mens email raised visit rate from 10.62% to 18.28% and conversion rate from 0.57% to 1.25%.
- Spend per buyer showed no quality drop ($114 control, $114 Mens, $122 Womens), so the lift came from more visits and purchases, not lower-value orders.
- Recommendation: use the Mens email as the benchmark creative for a follow-up test of personalized product-category messaging.

## File Description

- `project_notebook_Email_Campaign_AB_Test.ipynb`: Main notebook covering experiment setup, data checks, primary metric testing, guardrail and tracking metrics, and the recommendation.
- `data/hillstrom_email_marketing.csv`: Raw MineThatData email experiment dataset.
- `requirements.txt`: Dependencies for the notebook.

## Install

This project requires Python 3.x and the libraries listed in `requirements.txt`, including:

- NumPy
- pandas
- matplotlib
- seaborn
- scipy
- Jupyter

## Features

- `recency`: Months since the customer's last purchase.
- `history_segment`: Customer purchase history group.
- `history`: Dollar value of prior customer purchase history.
- `mens`: Whether the customer historically purchased mens merchandise.
- `womens`: Whether the customer historically purchased womens merchandise.
- `zip_code`: Customer zip-code category.
- `newbie`: Whether the customer is a newer customer.
- `channel`: Prior customer purchase channel.
- `segment`: Randomized experiment group.
- `visit`: Whether the customer visited the website during the outcome window.
- `conversion`: Whether the customer purchased during the outcome window.
- `spend`: Customer spend during the outcome window.

## Treatment and Control

Treatment groups:

- `Mens E-Mail`: Customer received a promotional email featuring mens merchandise.
- `Womens E-Mail`: Customer received a promotional email featuring womens merchandise.

Control group:

- `No E-Mail`: Customer did not receive a promotional email.

Randomization unit:

- Customer

## Hypothesis

Primary hypothesis:

- Promotional email increases spend per customer compared with no email.

Statistical framing:

- Null hypothesis: Mean spend per customer is the same between email and no-email groups.
- Alternative hypothesis: Mean spend per customer is higher for customers who received an email.