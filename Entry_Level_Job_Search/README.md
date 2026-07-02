# Entry-Level Job Search Reality Check in the Current Job Market

## Project Description

This project uses a [LinkedIn job posting dataset](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) to build an end-to-end workflow for identifying entry-level-labeled job postings that may not actually read like realistic entry-level roles. Many recent graduates and career changers search for entry-level jobs, but some postings labeled `Entry level` still ask for years of experience, leadership responsibility, advanced degrees, or senior-level skills.

The goal is to help job seekers prioritize postings that are more likely to match their experience level and avoid spending too much time on misleading or overly demanding entry-level listings.

The project connects exploratory analysis, feature engineering, classification modeling, model comparison, and Streamlit dashboard deployment into practical job-search recommendation tool.

The model and dashboard are evaluated using these key outputs:

- Seniority classification performance
- Entry-level precision, recall, and F1 score
- Weighted F1 and macro F1
- Confusion matrix review
- True entry-level score
- Warning signals for potentially demanding postings
- Filtered job recommendations for job seekers

## File Description

- `project_notebook.ipynb`: Main portfolio notebook covering data loading, EDA, feature engineering, modeling, evaluation, and deployment preparation.
- `streamlit_app.py`: Streamlit dashboard for searching and ranking realistic entry-level postings.
- `data/streamlit/entry_level_dashboard_jobs.csv`: Reduced dashboard-ready dataset used by the Streamlit app.
- `models/final_model.pkl`: Saved final calibrated LinearSVC model from the notebook.
- `sql/build_final_table.sql`: SQL script used to join and prepare the original raw LinkedIn job posting data.
- `requirements.txt`: Minimal dependencies required to deploy the Streamlit dashboard.
- `requirements_notebook.txt`: Full notebook/training environment dependencies.

## Features

- `title`: Job posting title.
- `company_name`: Company associated with the job posting.
- `location`: Job location.
- `industry_text`: Aggregated industry labels for the posting.
- `skill_text`: Aggregated skills associated with the posting.
- `formatted_work_type`: Work type, such as full-time, part-time, contract, or internship.
- `remote_status`: Whether the role is remote eligible or not remote eligible.
- `salary_present`: Whether salary information is available.
- `description_word_count`: Length of the job description.
- `mentions_3plus_years`: Whether the description mentions at least 3 years of experience.
- `mentions_5plus_years`: Whether the description mentions at least 5 years of experience.
- `mentions_advanced_degree`: Whether the description mentions advanced degree language.
- `mentions_leadership_language`: Whether the description includes leadership, ownership, or management language.
- `title_sounds_senior`: Whether the title contains senior-level wording.
- `title_sounds_junior`: Whether the title contains junior or early-career wording.
- `true_entry_level_score`: Model-estimated probability that the posting reads like a true entry-level role.
- `predicted_seniority`: Seniority label predicted by the final model.

## Install

This project requires Python 3.x and the libraries listed in `requirements.txt` for dashboard deployment, including:

- pandas
- Streamlit

For full notebook training and experimentation, use `requirements_notebook.txt`, which includes additional modeling and notebook dependencies.

## Interactive Dashboard

This project includes a Streamlit dashboard that helps job seekers search for realistic entry-level postings.

The dashboard uses a reduced, pre-scored dataset and allows users to filter jobs by:

- Job title keyword
- Work type
- Remote status
- Location
- Industry
- Skill
- Salary availability
- Minimum true entry-level score

For each matching job posting, the dashboard shows the model’s true entry-level score, predicted seniority, industry, salary visibility, listed date, warning notes, and posting link.

Users can also export the filtered results as a CSV file so they can continue tracking and prioritizing applications outside the dashboard.