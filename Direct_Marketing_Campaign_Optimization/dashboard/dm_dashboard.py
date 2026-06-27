from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Direct Marketing ROI Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
RAW_DATA_PATHS = [
    Path.cwd() / "data" / "bank-full.csv"
]


@st.cache_data
def load_campaign_data():
    for path in RAW_DATA_PATHS:
        if path.exists():
            return pd.read_csv(path, sep=";")

    st.error(
        "The dashboard could not find `bank-full.csv`. "
        "Confirm that the raw data file is included in the deployed Project 1 folder."
    )
    st.stop()


def add_notebook_features(data, contact_cost, value_per_response):
    df = data.copy()

    df["customer_id"] = np.arange(1, len(df) + 1)
    df["contacted_customer"] = 1
    df["contact_attempts"] = df["campaign"]
    df["response_flag"] = np.where(df["y"].eq("yes"), 1, 0)
    df["response_count"] = df["response_flag"]

    df["estimated_contact_cost"] = df["contact_attempts"] * contact_cost
    df["estimated_gross_profit"] = df["response_flag"] * value_per_response
    df["estimated_net_profit"] = (
        df["estimated_gross_profit"] - df["estimated_contact_cost"]
    )

    month_order = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]

    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 29, 39, 49, 59, 69, 120],
        labels=["18-29", "30-39", "40-49", "50-59", "60-69", "70+"],
    )
    df["balance_group"] = pd.cut(
        df["balance"],
        bins=[-np.inf, -1, 0, 999, 4999, np.inf],
        labels=["negative", "zero", "1-999", "1,000-4,999", "5,000+"],
    )
    df["campaign_contact_group"] = pd.cut(
        df["campaign"],
        bins=[0, 1, 2, 3, 5, np.inf],
        labels=["1", "2", "3", "4-5", "6+"],
    )
    df["previous_contact_flag"] = np.where(
        df["previous"].gt(0), "previously_contacted", "not_previously_contacted"
    )
    df["previous_contact_group"] = pd.cut(
        df["previous"],
        bins=[-1, 0, 1, 3, np.inf],
        labels=["0", "1", "2-3", "4+"],
    )
    df["pdays_status"] = np.where(
        df["pdays"].eq(-1), "not_previously_contacted", "previously_contacted"
    )
    df["loan_profile"] = np.select(
        [
            df["housing"].eq("yes") & df["loan"].eq("yes"),
            df["housing"].eq("yes") & df["loan"].eq("no"),
            df["housing"].eq("no") & df["loan"].eq("yes"),
            df["housing"].eq("no") & df["loan"].eq("no"),
        ],
        [
            "housing_and_personal_loan",
            "housing_loan_only",
            "personal_loan_only",
            "no_housing_or_personal_loan",
        ],
        default="unknown",
    )
    df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)
    return df


def build_overall_kpis(data):
    contacted = data["contacted_customer"].sum()
    attempts = data["contact_attempts"].sum()
    responses = data["response_count"].sum()
    contact_cost = data["estimated_contact_cost"].sum()
    gross_profit = data["estimated_gross_profit"].sum()
    net_profit = data["estimated_net_profit"].sum()

    return {
        "contacted_customers": contacted,
        "total_contact_attempts": attempts,
        "responses": responses,
        "response_rate": responses / contacted,
        "contact_attempts_per_customer": attempts / contacted,
        "estimated_contact_cost": contact_cost,
        "estimated_gross_profit": gross_profit,
        "estimated_net_profit": net_profit,
        "roi": net_profit / contact_cost,
        "cost_per_response": contact_cost / responses,
    }


def build_segment_kpis(data, group_col):
    summary = (
        data.groupby(group_col, dropna=False, observed=True)
        .agg(
            contacted_customers=("contacted_customer", "sum"),
            total_contact_attempts=("contact_attempts", "sum"),
            responses=("response_count", "sum"),
            estimated_contact_cost=("estimated_contact_cost", "sum"),
            estimated_gross_profit=("estimated_gross_profit", "sum"),
            estimated_net_profit=("estimated_net_profit", "sum"),
        )
        .reset_index()
    )
    summary["segment"] = summary[group_col].astype(str)
    summary["response_rate"] = summary["responses"] / summary["contacted_customers"]
    summary["contact_attempts_per_customer"] = (
        summary["total_contact_attempts"] / summary["contacted_customers"]
    )
    summary["roi"] = summary["estimated_net_profit"] / summary["estimated_contact_cost"]
    summary["cost_per_response"] = np.where(
        summary["responses"].gt(0),
        summary["estimated_contact_cost"] / summary["responses"],
        np.nan,
    )
    return summary


def reduced_rf_lift_table():
    return pd.DataFrame(
        {
            "score_tile": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "customers": [905, 904, 904, 904, 904, 905, 904, 904, 904, 905],
            "responses": [453, 189, 101, 78, 62, 53, 41, 29, 29, 23],
            "response_rate": [
                0.500552,
                0.209071,
                0.111726,
                0.086283,
                0.068584,
                0.058564,
                0.045354,
                0.032080,
                0.032080,
                0.025414,
            ],
            "lift": [
                4.278352,
                1.786982,
                0.954948,
                0.737485,
                0.586206,
                0.500558,
                0.387652,
                0.274193,
                0.274193,
                0.217223,
            ],
            "avg_predicted_probability": [
                0.789094,
                0.567066,
                0.449209,
                0.386571,
                0.337374,
                0.293458,
                0.254618,
                0.217870,
                0.178653,
                0.125157,
            ],
        }
    )


def build_targeting_table(lift_data, contact_cost, value_per_response):
    table = lift_data.copy()
    table["cumulative_customers"] = table["customers"].cumsum()
    table["cumulative_responses"] = table["responses"].cumsum()
    table["share_customers_targeted"] = (
        table["cumulative_customers"] / table["customers"].sum()
    )
    table["share_responses_captured"] = (
        table["cumulative_responses"] / table["responses"].sum()
    )
    table["targeted_response_rate"] = (
        table["cumulative_responses"] / table["cumulative_customers"]
    )
    baseline_response_rate = table["responses"].sum() / table["customers"].sum()
    table["targeted_lift"] = table["targeted_response_rate"] / baseline_response_rate
    table["targeting_strategy"] = (
        "Top "
        + (table["share_customers_targeted"] * 100).round(0).astype(int).astype(str)
        + "%"
    )
    table["customers_targeted"] = table["cumulative_customers"]
    table["responses_captured"] = table["cumulative_responses"]
    table["estimated_contact_cost"] = table["customers_targeted"] * contact_cost
    table["estimated_gross_profit"] = table["responses_captured"] * value_per_response
    table["estimated_net_profit"] = (
        table["estimated_gross_profit"] - table["estimated_contact_cost"]
    )
    table["roi"] = table["estimated_net_profit"] / table["estimated_contact_cost"]
    table["cost_per_response"] = (
        table["estimated_contact_cost"] / table["responses_captured"]
    )

    return table[
        [
            "targeting_strategy",
            "customers_targeted",
            "share_customers_targeted",
            "responses_captured",
            "share_responses_captured",
            "targeted_response_rate",
            "targeted_lift",
            "estimated_contact_cost",
            "estimated_gross_profit",
            "estimated_net_profit",
            "roi",
            "cost_per_response",
        ]
    ]


def money(value):
    return f"${value:,.0f}"


def money_two(value):
    return f"${value:,.2f}"


def percent(value):
    return f"{value:.1%}"


def multiple(value):
    return f"{value:.1f}x"


def metric_card(label, value, caption):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_table(table):
    formatted = table.copy()
    formatters = {
        "Customers": lambda x: f"{x:,.0f}",
        "Responders": lambda x: f"{x:,.0f}",
        "Response Rate": percent,
        "Lift": multiple,
        "Captured Responders": percent,
        "Contact Cost": money,
        "Gross Profit": money,
        "Net Profit": money,
        "ROI": multiple,
        "Cost / Response": money_two,
    }
    for col, formatter in formatters.items():
        if col in formatted.columns:
            formatted[col] = formatted[col].map(formatter)
    return formatted


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .metric-card {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem;
        background: #FFFFFF;
        min-height: 118px;
    }
    .metric-label {
        color: #6B7280;
        font-size: 0.80rem;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        color: #111827;
        font-size: 1.45rem;
        font-weight: 750;
        line-height: 1.2;
    }
    .metric-caption {
        color: #6B7280;
        font-size: 0.78rem;
        line-height: 1.35;
        margin-top: 0.45rem;
    }
    .note {
        color: #4B5563;
        font-size: 0.96rem;
        line-height: 1.55;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Direct Marketing Campaign ROI Dashboard")
st.markdown(
    """
    <div class="note">
    This dashboard is based on the organized Project 1 notebook. It turns the
    reduced-feature random forest targeting results into a business-facing
    planning tool: adjust campaign economics, compare targeting thresholds, and
    review which customer segments deserve closer attention before launch.
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Scenario Controls")
contact_cost = st.sidebar.slider(
    "Cost per planned customer contact",
    min_value=0.50,
    max_value=20.00,
    value=2.00,
    step=0.50,
)
value_per_response = st.sidebar.slider(
    "Expected profit per successful response",
    min_value=10,
    max_value=500,
    value=100,
    step=10,
)

segment_options = {
    "Prior campaign outcome": "poutcome",
    "Contact channel": "contact",
    "Campaign month": "month",
    "Contact count group": "campaign_contact_group",
    "Age group": "age_group",
    "Job": "job",
    "Balance group": "balance_group",
    "Loan profile": "loan_profile",
    "Default status": "default",
}
segment_label = st.sidebar.selectbox(
    "Segment view",
    options=list(segment_options.keys()),
    index=0,
)
segment_metric = st.sidebar.selectbox(
    "Rank segments by",
    options=["ROI", "Response Rate", "Net Profit"],
    index=0,
)

raw_df = load_campaign_data()
campaign_df = add_notebook_features(raw_df, contact_cost, value_per_response)
overall = build_overall_kpis(campaign_df)
lift_df = reduced_rf_lift_table()
targeting_df = build_targeting_table(lift_df, contact_cost, value_per_response)

strategy_options = targeting_df["targeting_strategy"].tolist()
default_strategy_index = strategy_options.index("Top 20%")
selected_strategy = st.sidebar.selectbox(
    "Targeting threshold",
    options=strategy_options,
    index=default_strategy_index,
)
selected_row = targeting_df.loc[
    targeting_df["targeting_strategy"].eq(selected_strategy)
].iloc[0]
top_10 = targeting_df.loc[targeting_df["targeting_strategy"].eq("Top 10%")].iloc[0]
top_20 = targeting_df.loc[targeting_df["targeting_strategy"].eq("Top 20%")].iloc[0]
top_30 = targeting_df.loc[targeting_df["targeting_strategy"].eq("Top 30%")].iloc[0]
best_roi_row = targeting_df.loc[targeting_df["roi"].idxmax()]
best_profit_row = targeting_df.loc[targeting_df["estimated_net_profit"].idxmax()]

st.sidebar.divider()
st.sidebar.caption(
    "Historical campaign KPIs use observed contact attempts. Targeting scenarios "
    "use one planned contact per selected customer, matching the notebook's final ROI table."
)

st.subheader("Campaign Baseline")
baseline_cols = st.columns(5)
with baseline_cols[0]:
    metric_card(
        "Contacted Customers",
        f"{overall['contacted_customers']:,.0f}",
        "Rows in the UCI Bank Marketing dataset",
    )
with baseline_cols[1]:
    metric_card(
        "Responses",
        f"{overall['responses']:,.0f}",
        f"{percent(overall['response_rate'])} historical response rate",
    )
with baseline_cols[2]:
    metric_card(
        "Contact Attempts",
        f"{overall['total_contact_attempts']:,.0f}",
        f"{overall['contact_attempts_per_customer']:.2f} attempts per customer",
    )
with baseline_cols[3]:
    metric_card(
        "Historical Net Profit",
        money(overall["estimated_net_profit"]),
        f"Uses {money_two(contact_cost)} cost and {money(value_per_response)} value assumptions",
    )
with baseline_cols[4]:
    metric_card(
        "Historical ROI",
        multiple(overall["roi"]),
        f"{money_two(overall['cost_per_response'])} cost per response",
    )

st.subheader("Selected Targeting Scenario")
scenario_cols = st.columns(5)
with scenario_cols[0]:
    metric_card(
        "Customers Targeted",
        f"{selected_row['customers_targeted']:,.0f}",
        f"{percent(selected_row['share_customers_targeted'])} of scored test customers",
    )
with scenario_cols[1]:
    metric_card(
        "Responders Captured",
        f"{selected_row['responses_captured']:,.0f}",
        f"{percent(selected_row['share_responses_captured'])} of test responders",
    )
with scenario_cols[2]:
    metric_card(
        "Response Rate",
        percent(selected_row["targeted_response_rate"]),
        f"{multiple(selected_row['targeted_lift'])} lift vs test baseline",
    )
with scenario_cols[3]:
    metric_card(
        "Estimated Net Profit",
        money(selected_row["estimated_net_profit"]),
        f"{money(selected_row['estimated_gross_profit'])} gross - {money(selected_row['estimated_contact_cost'])} cost",
    )
with scenario_cols[4]:
    metric_card(
        "ROI",
        multiple(selected_row["roi"]),
        f"{money_two(selected_row['cost_per_response'])} cost per response",
    )

st.info(
    f"The notebook's practical recommendation is **Top 20% to Top 30%**. "
    f"At the current assumptions, Top 20% captures {percent(top_20['share_responses_captured'])} "
    f"of responders at {multiple(top_20['targeted_lift'])} lift, while Top 30% captures "
    f"{percent(top_30['share_responses_captured'])} at {multiple(top_30['targeted_lift'])} lift. "
    f"Top 10% remains the efficiency option with {multiple(top_10['roi'])} ROI."
)

tab_targeting, tab_segments, tab_notes = st.tabs(
    ["Targeting Tradeoffs", "Segment Review", "Assumptions and Risks"]
)

with tab_targeting:
    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        st.markdown("#### ROI by Targeting Threshold")
        st.bar_chart(
            targeting_df[["targeting_strategy", "roi"]].rename(
                columns={"targeting_strategy": "Threshold", "roi": "ROI Multiple"}
            ),
            x="Threshold",
            y="ROI Multiple",
            height=320,
            color="#2563EB",
        )
        st.caption(
            f"Highest ROI: {best_roi_row['targeting_strategy']} at {multiple(best_roi_row['roi'])}."
        )
    with chart_col_2:
        st.markdown("#### Net Profit by Targeting Threshold")
        st.line_chart(
            targeting_df[["targeting_strategy", "estimated_net_profit"]].rename(
                columns={
                    "targeting_strategy": "Threshold",
                    "estimated_net_profit": "Estimated Net Profit",
                }
            ),
            x="Threshold",
            y="Estimated Net Profit",
            height=320,
            color="#059669",
        )
        st.caption(
            f"Highest modeled net profit: {best_profit_row['targeting_strategy']} at {money(best_profit_row['estimated_net_profit'])}."
        )

    lift_col_1, lift_col_2 = st.columns(2)
    with lift_col_1:
        st.markdown("#### Response Rate by Model Score Tile")
        st.bar_chart(
            lift_df[["score_tile", "response_rate"]].rename(
                columns={"score_tile": "Score Tile", "response_rate": "Response Rate"}
            ),
            x="Score Tile",
            y="Response Rate",
            height=320,
            color="#7C3AED",
        )
        st.caption(
            "Tile 1 contains the highest predicted response probabilities. The notebook's selected model reaches 50.1% response rate in this tile."
        )
    with lift_col_2:
        st.markdown("#### Response Capture Curve")
        capture_chart = targeting_df[
            ["share_customers_targeted", "share_responses_captured"]
        ].copy()
        capture_chart["random_targeting"] = capture_chart["share_customers_targeted"]
        capture_chart = capture_chart.rename(
            columns={
                "share_customers_targeted": "Share of Customers Targeted",
                "share_responses_captured": "Model Targeting",
                "random_targeting": "Random Targeting",
            }
        )
        st.line_chart(
            capture_chart,
            x="Share of Customers Targeted",
            y=["Model Targeting", "Random Targeting"],
            height=320,
            color=["#DC2626", "#9CA3AF"],
        )
        st.caption(
            "The model captures responders faster than random outreach, especially in the top 10-30% of customers."
        )

    threshold_table = targeting_df[
        [
            "targeting_strategy",
            "customers_targeted",
            "responses_captured",
            "targeted_response_rate",
            "targeted_lift",
            "share_responses_captured",
            "estimated_contact_cost",
            "estimated_gross_profit",
            "estimated_net_profit",
            "roi",
            "cost_per_response",
        ]
    ].rename(
        columns={
            "targeting_strategy": "Threshold",
            "customers_targeted": "Customers",
            "responses_captured": "Responders",
            "targeted_response_rate": "Response Rate",
            "targeted_lift": "Lift",
            "share_responses_captured": "Captured Responders",
            "estimated_contact_cost": "Contact Cost",
            "estimated_gross_profit": "Gross Profit",
            "estimated_net_profit": "Net Profit",
            "roi": "ROI",
            "cost_per_response": "Cost / Response",
        }
    )
    st.markdown("#### Threshold Detail")
    st.table(format_table(threshold_table))

with tab_segments:
    selected_group = segment_options[segment_label]
    segment_kpis = build_segment_kpis(campaign_df, selected_group)
    metric_map = {
        "ROI": "roi",
        "Response Rate": "response_rate",
        "Net Profit": "estimated_net_profit",
    }
    selected_metric = metric_map[segment_metric]
    segment_kpis = segment_kpis.sort_values(selected_metric, ascending=False)
    top_segments = segment_kpis.head(12).copy()

    st.markdown(f"#### {segment_label}: Top Segments by {segment_metric}")
    chart_data = top_segments[["segment", selected_metric]].rename(
        columns={"segment": "Segment", selected_metric: segment_metric}
    )
    st.bar_chart(
        chart_data,
        x="Segment",
        y=segment_metric,
        height=360,
        color="#0F766E",
    )

    segment_table = top_segments[
        [
            "segment",
            "contacted_customers",
            "responses",
            "response_rate",
            "estimated_net_profit",
            "roi",
            "cost_per_response",
        ]
    ].rename(
        columns={
            "segment": "Segment",
            "contacted_customers": "Customers",
            "responses": "Responders",
            "response_rate": "Response Rate",
            "estimated_net_profit": "Net Profit",
            "roi": "ROI",
            "cost_per_response": "Cost / Response",
        }
    )
    st.table(format_table(segment_table))
    st.caption(
        "Segment metrics are descriptive, not causal. They help identify where the business should investigate targeting, timing, and contact strategy."
    )

with tab_notes:
    st.markdown("#### How to Read This Dashboard")
    st.markdown(
        """
        - The baseline campaign KPIs are rebuilt from the organized notebook's raw
          UCI Bank Marketing file.
        - The targeting threshold table uses the reduced-feature random forest
          lift results reported in the notebook.
        - `duration` is intentionally excluded from the modeling story because it
          is only known after a customer has already been contacted.
        - ROI assumptions are synthetic. They make the business tradeoff visible,
          but actual campaign economics could change the best threshold.
        """
    )

    st.markdown("#### Notebook-Aligned Decision Rules")
    st.markdown(
        """
        - **Maximize ROI:** choose Top 10%.
        - **Balance scale and efficiency:** choose Top 20% to Top 30%.
        - **Maximize modeled net profit under the synthetic assumptions:** Top 100%.
        - **Production next step:** validate the strategy in a future randomized campaign
          and monitor customer fatigue, opt-outs, complaints, and long-term value.
        """
    )

st.caption(
    "Source: Project 1 organized notebook, UCI Bank Marketing dataset, and reduced-feature random forest lift results."
)
