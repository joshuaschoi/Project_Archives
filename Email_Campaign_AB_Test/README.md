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

## File Description

- `data/project2_hillstrom/hillstrom_email_marketing.csv`: Raw MineThatData email experiment dataset.

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