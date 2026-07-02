-- Build one job-level analytical table for the project.
-- The notebook replaces __RAW_DATA_DIR__ with the local raw data folder path.

WITH postings AS (
    SELECT  job_id,
            CAST(company_id AS BIGINT) AS company_id,
            company_name,
            title,
            description,
            formatted_experience_level,
            formatted_work_type,
            work_type,
            location,
            remote_allowed,
            views,
            applies,
            normalized_salary,
            min_salary AS posting_min_salary,
            max_salary AS posting_max_salary,
            med_salary AS posting_med_salary,
            pay_period AS posting_pay_period,
            currency AS posting_currency,
            sponsored,
            listed_time,
            expiry,
            job_posting_url
    FROM read_csv_auto('__RAW_DATA_DIR__/postings.csv', ignore_errors = true)
),

skills AS (
    SELECT  job_skills.job_id,
            string_agg(DISTINCT skills.skill_name, '; ' ORDER BY skills.skill_name) AS skill_text,
            count(DISTINCT skills.skill_name) AS skill_count
    FROM read_csv_auto('__RAW_DATA_DIR__/jobs/job_skills.csv') AS job_skills
    LEFT JOIN read_csv_auto('__RAW_DATA_DIR__/mappings/skills.csv') AS skills
        ON job_skills.skill_abr = skills.skill_abr
    GROUP BY 1
),

industries AS (
    SELECT  job_industries.job_id,
            string_agg(DISTINCT industries.industry_name, '; ' ORDER BY industries.industry_name) AS industry_text,
            count(DISTINCT industries.industry_name) AS industry_count
    FROM read_csv_auto('__RAW_DATA_DIR__/jobs/job_industries.csv') AS job_industries
    LEFT JOIN read_csv_auto('__RAW_DATA_DIR__/mappings/industries.csv') AS industries
        ON job_industries.industry_id = industries.industry_id
    GROUP BY 1
),

salaries AS (
    SELECT  job_id,
            1 AS salary_rows,
            min_salary AS salary_min,
            max_salary AS salary_max,
            med_salary AS salary_med,
            pay_period AS salary_pay_period,
            currency AS salary_currency,
            compensation_type AS salary_compensation_type
    FROM read_csv_auto('__RAW_DATA_DIR__/jobs/salaries.csv')
),

benefits AS (
    SELECT  job_id,
            string_agg(DISTINCT type, '; ' ORDER BY type) AS benefit_text,
            count(DISTINCT type) AS benefit_count
    FROM read_csv_auto('__RAW_DATA_DIR__/jobs/benefits.csv')
    GROUP BY 1
),

companies AS (
    SELECT  company_id,
            company_size,
            state AS company_state,
            country AS company_country
    FROM read_csv_auto('__RAW_DATA_DIR__/companies/companies.csv')
),

latest_employee_counts AS (
    SELECT  company_id,
            employee_count,
            follower_count
    FROM (
        SELECT
            *,
            row_number() OVER (
                PARTITION BY company_id
                ORDER BY time_recorded DESC
            ) AS employee_count_recency_rank
        FROM read_csv_auto('__RAW_DATA_DIR__/companies/employee_counts.csv')
    )
    WHERE employee_count_recency_rank = 1
)

SELECT  postings.job_id,
        postings.company_id,
        postings.company_name,
        postings.title,
        postings.description,
        postings.formatted_experience_level,
        postings.formatted_work_type,
        postings.work_type,
        postings.location,
        CASE WHEN postings.remote_allowed IS NOT NULL THEN 'Remote-Eligible' ELSE 'Remote-Not Eligible' END AS remote_status,
        CASE WHEN 
            postings.normalized_salary IS NOT NULL
            OR postings.posting_min_salary IS NOT NULL
            OR postings.posting_max_salary IS NOT NULL
            OR postings.posting_med_salary IS NOT NULL
            OR salaries.salary_min IS NOT NULL
            OR salaries.salary_max IS NOT NULL
            OR salaries.salary_med IS NOT NULL
            THEN TRUE
            ELSE FALSE
            END AS salary_present,
        postings.normalized_salary,
        postings.posting_min_salary,
        postings.posting_max_salary,
        postings.posting_med_salary,
        postings.posting_pay_period,
        postings.posting_currency,
        salaries.salary_min,
        salaries.salary_max,
        salaries.salary_med,
        salaries.salary_pay_period,
        salaries.salary_currency,
        salaries.salary_compensation_type,
        coalesce(skills.skill_text, '') AS skill_text,
        coalesce(skills.skill_count, 0) AS skill_count,
        coalesce(industries.industry_text, '') AS industry_text,
        coalesce(industries.industry_count, 0) AS industry_count,
        coalesce(benefits.benefit_text, '') AS benefit_text,
        coalesce(benefits.benefit_count, 0) AS benefit_count,
        companies.company_size,
        companies.company_state,
        companies.company_country,
        latest_employee_counts.employee_count,
        latest_employee_counts.follower_count,
        postings.views,
        postings.applies,
        postings.sponsored,
        postings.listed_time,
        postings.expiry,
        postings.job_posting_url
FROM postings
LEFT JOIN skills
    ON postings.job_id = skills.job_id
LEFT JOIN industries
    ON postings.job_id = industries.job_id
LEFT JOIN salaries
    ON postings.job_id = salaries.job_id
LEFT JOIN benefits
    ON postings.job_id = benefits.job_id
LEFT JOIN companies
    ON postings.company_id = companies.company_id
LEFT JOIN latest_employee_counts
    ON postings.company_id = latest_employee_counts.company_id;
