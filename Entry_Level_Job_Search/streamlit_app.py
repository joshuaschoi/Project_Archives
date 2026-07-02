from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
APP_DATA_PATH = PROJECT_DIR / "data" / "streamlit" / "app_dataset.csv"

st.set_page_config(
    page_title="Entry-Level Job Finder",
    layout="wide",
)

@st.cache_data(show_spinner="Loading dashboard-ready job postings...")
def load_scored_jobs() -> pd.DataFrame:
    """Load the compact pre-scored dataset exported by the project notebook."""
    jobs = pd.read_csv(APP_DATA_PATH)

    text_columns = [
        "title_clean",
        "title",
        "company_name",
        "location",
        "industry_text",
        "skill_text",
        "formatted_work_type",
        "remote_status",
        "listed_date",
        "predicted_seniority",
        "salary_display",
        "warning_reasons",
        "job_posting_url",
    ]
    for column in text_columns:
        jobs[column] = jobs[column].fillna("").astype(str)

    jobs["true_entry_level_score"] = pd.to_numeric(
        jobs["true_entry_level_score"],
        errors="coerce",
    ).fillna(0)
    jobs["views"] = pd.to_numeric(jobs["views"], errors="coerce").fillna(0)
    jobs["salary_present"] = jobs["salary_present"].astype(str).str.lower().isin(["true", "1", "yes"])
    return jobs


def filter_jobs(scored_jobs: pd.DataFrame) -> pd.DataFrame:
    """Apply sidebar filters selected by the job seeker."""
    filtered = scored_jobs.copy()

    with st.sidebar:
        st.header("Search Filters")

        title_keyword = st.text_input("Job Title", placeholder="analyst, engineer, research")

        work_type_options = sorted(scored_jobs["formatted_work_type"].dropna().astype(str).unique())
        selected_work_types = st.multiselect(
            "Work Type",
            work_type_options,
            default=work_type_options,
        )

        remote_options = sorted(scored_jobs["remote_status"].dropna().astype(str).unique())
        selected_remote = st.multiselect(
            "Remote Status",
            remote_options,
            default=remote_options,
        )

        location_keyword = st.text_input("Location", placeholder="New York, United States")
        industry_keyword = st.text_input("Industry", placeholder="Technology, Finance")
        skill_keyword = st.text_input("Skill", placeholder="SQL, Python, Excel")
        salary_only = st.checkbox("Only postings with salary info")
        min_score = st.slider("Minimum true-entry score", 0.0, 1.0, 0.50, 0.05)

    if title_keyword:
        filtered = filtered[
            filtered["title_clean"].str.contains(re.escape(title_keyword.lower()), na=False)
        ]
    if selected_work_types:
        filtered = filtered[filtered["formatted_work_type"].isin(selected_work_types)]
    if selected_remote:
        filtered = filtered[filtered["remote_status"].isin(selected_remote)]
    if location_keyword:
        filtered = filtered[
            filtered["location"].fillna("").str.contains(location_keyword, case=False, regex=False)
        ]
    if industry_keyword:
        filtered = filtered[
            filtered["industry_text"].fillna("").str.contains(industry_keyword, case=False, regex=False)
        ]
    if skill_keyword:
        filtered = filtered[
            filtered["skill_text"].fillna("").str.contains(skill_keyword, case=False, regex=False)
        ]
    if salary_only:
        filtered = filtered[filtered["salary_present"].astype(bool)]

    filtered = filtered[filtered["true_entry_level_score"].ge(min_score)]
    return filtered.sort_values(["true_entry_level_score", "views"], ascending=False)


def main() -> None:
    st.title("Entry-Level Job Finder")
    st.caption(
        "Ranks LinkedIn postings labeled as entry-level by how strongly the model thinks "
        "they read like realistic entry-level roles."
    )

    if not APP_DATA_PATH.exists():
        st.error(
            f"Missing dashboard dataset: {APP_DATA_PATH}. "
            "Rerun the final notebook export cell to create it."
        )
        st.stop()

    scored_jobs = load_scored_jobs()
    filtered_jobs = filter_jobs(scored_jobs)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total Entry-level Postings", f"{len(scored_jobs):,}")
    metric_cols[1].metric("Filtered Postings", f"{len(filtered_jobs):,}")
    average_score = filtered_jobs["true_entry_level_score"].mean() if not filtered_jobs.empty else 0
    metric_cols[2].metric("Average True entry-level Score", f"{average_score:.0%}")
    high_score_count = filtered_jobs["true_entry_level_score"].ge(0.85).sum()
    metric_cols[3].metric("Strong Matches", f"{high_score_count:,}")

    st.subheader("Recommended Postings")
    if filtered_jobs.empty:
        st.warning("No postings match the current filters. Try lowering the score threshold.")
        return

    display_columns = [
        "title",
        "company_name",
        "location",
        "industry_text",
        "formatted_work_type",
        "remote_status",
        "listed_date",
        "true_entry_level_score",
        "predicted_seniority",
        "salary_display",
        "warning_reasons",
        "job_posting_url",
    ]
    display_jobs = filtered_jobs[display_columns].rename(
        columns={
            "title": "Title",
            "company_name": "Company",
            "location": "Location",
            "industry_text": "Industry",
            "formatted_work_type": "Work type",
            "remote_status": "Remote status",
            "listed_date": "Listed date",
            "true_entry_level_score": "True entry-level score",
            "predicted_seniority": "Model prediction",
            "salary_display": "Salary",
            "warning_reasons": "Model notes",
            "job_posting_url": "Posting link",
        }
    )
    display_jobs["True entry-level score"] = display_jobs["True entry-level score"] * 100

    st.dataframe(
        display_jobs,
        hide_index=True,
        width="stretch",
        column_config={
            "True entry-level score": st.column_config.ProgressColumn(
                "True entry-level score",
                format="%.0f%%",
                min_value=0,
                max_value=100,
            ),
            "Posting link": st.column_config.LinkColumn("Posting link"),
        },
    )

    csv_data = display_jobs.to_csv(index=False).encode("utf-8")
    _, download_col = st.columns([0.72, 0.28])
    with download_col:
        st.download_button(
            "Download Filtered Results CSV",
            data=csv_data,
            file_name="filtered_entry_level_jobs.csv",
            mime="text/csv",
            width="stretch",
        )

if __name__ == "__main__":
    main()
