from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Direct Marketing ROI Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
THRESHOLD_PATH = BASE_DIR / "data" / "processed" / "project1_targeting_threshold_table.csv"
LIFT_PATH = BASE_DIR / "data" / "processed" / "project1_final_lift_table.csv"


@st.cache_data
def load_project_data():
    threshold_data = pd.read_csv(THRESHOLD_PATH)
    lift_data = pd.read_csv(LIFT_PATH)
    return threshold_data, lift_data


threshold_df, lift_df = load_project_data()

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    .metric-card {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem 1rem 0.85rem 1rem;
        background: #FFFFFF;
        min-height: 118px;
    }
    .metric-label {
        color: #6B7280;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        color: #111827;
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.15;
    }
    .metric-caption {
        color: #6B7280;
        font-size: 0.78rem;
        margin-top: 0.4rem;
    }
    .section-note {
        color: #4B5563;
        font-size: 0.95rem;
        line-height: 1.55;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Direct Marketing ROI Simulator")
st.markdown(
    """
    <div class="section-note">
    This dashboard turns the Project 1 response model into a campaign planning tool.
    Adjust the business assumptions, choose a targeting threshold, and compare how
    expected ROI changes across model-ranked customer groups.
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Business Assumptions")
contact_cost = st.sidebar.slider(
    "Cost per contacted customer",
    min_value=0.50,
    max_value=20.00,
    value=2.00,
    step=0.50,
    help="Estimated cost to contact one customer in the campaign.",
)
value_per_response = st.sidebar.slider(
    "Value per successful response",
    min_value=10,
    max_value=500,
    value=100,
    step=10,
    help="Estimated value or margin from one successful term deposit response.",
)

threshold_options = threshold_df["targeting_strategy"].tolist()
default_index = threshold_options.index("Top 20%") if "Top 20%" in threshold_options else 0
selected_strategy = st.sidebar.selectbox(
    "Targeting threshold",
    options=threshold_options,
    index=default_index,
    help="Customers are ranked by predicted response probability. Lower percentages target fewer, higher-scoring customers.",
)

st.sidebar.divider()
st.sidebar.caption(
    "The model output comes from Project 1's reduced-feature random forest. "
    "Cost and value assumptions are adjustable planning inputs."
)

scenario_df = threshold_df.copy()
scenario_df["estimated_contact_cost"] = scenario_df["customers_targeted"] * contact_cost
scenario_df["estimated_gross_value"] = scenario_df["responses_captured"] * value_per_response
scenario_df["estimated_net_profit"] = (
    scenario_df["estimated_gross_value"] - scenario_df["estimated_contact_cost"]
)
scenario_df["roi"] = scenario_df["estimated_net_profit"] / scenario_df["estimated_contact_cost"]
scenario_df["cost_per_response"] = (
    scenario_df["estimated_contact_cost"] / scenario_df["responses_captured"]
)

selected_row = scenario_df.loc[
    scenario_df["targeting_strategy"].eq(selected_strategy)
].iloc[0]

best_roi_row = scenario_df.loc[scenario_df["roi"].idxmax()]
best_profit_row = scenario_df.loc[scenario_df["estimated_net_profit"].idxmax()]


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


st.subheader("Selected Targeting Scenario")
metric_cols = st.columns(5)
with metric_cols[0]:
    metric_card(
        "Customers Contacted",
        f"{selected_row['customers_targeted']:,.0f}",
        f"{percent(selected_row['share_customers_targeted'])} of scored customers",
    )
with metric_cols[1]:
    metric_card(
        "Expected Responders",
        f"{selected_row['responses_captured']:,.0f}",
        f"{percent(selected_row['share_responses_captured'])} of known responders",
    )
with metric_cols[2]:
    metric_card(
        "Response Rate",
        percent(selected_row["targeted_response_rate"]),
        f"{multiple(selected_row['targeted_lift'])} lift vs average",
    )
with metric_cols[3]:
    metric_card(
        "Estimated Net Profit",
        money(selected_row["estimated_net_profit"]),
        f"{money(selected_row['estimated_gross_value'])} value - {money(selected_row['estimated_contact_cost'])} cost",
    )
with metric_cols[4]:
    metric_card(
        "ROI",
        multiple(selected_row["roi"]),
        f"{money_two(selected_row['cost_per_response'])} cost per response",
    )

st.markdown("")
st.info(
    f"Under the current assumptions, **{selected_strategy}** produces "
    f"**{money(selected_row['estimated_net_profit'])}** in estimated net profit "
    f"and **{multiple(selected_row['roi'])} ROI**. The highest-ROI option is "
    f"**{best_roi_row['targeting_strategy']}**, while the highest estimated net profit option is "
    f"**{best_profit_row['targeting_strategy']}**."
)

chart_col_1, chart_col_2 = st.columns(2)

with chart_col_1:
    st.subheader("ROI by Targeting Threshold")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    colors = [
        "#2563EB" if value == selected_strategy else "#CBD5E1"
        for value in scenario_df["targeting_strategy"]
    ]
    ax.bar(scenario_df["targeting_strategy"], scenario_df["roi"], color=colors)
    ax.axhline(0, color="#374151", linewidth=1)
    ax.set_ylabel("ROI multiple")
    ax.set_xlabel("")
    ax.set_title("")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    for index, value in enumerate(scenario_df["roi"]):
        ax.text(index, value, f"{value:.1f}x", ha="center", va="bottom", fontsize=8)
    st.pyplot(fig, clear_figure=True)

with chart_col_2:
    st.subheader("Net Profit by Targeting Threshold")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(
        scenario_df["targeting_strategy"],
        scenario_df["estimated_net_profit"],
        color="#059669",
        marker="o",
        linewidth=2.5,
    )
    selected_index = scenario_df.index[
        scenario_df["targeting_strategy"].eq(selected_strategy)
    ][0]
    ax.scatter(
        [selected_strategy],
        [selected_row["estimated_net_profit"]],
        color="#111827",
        s=70,
        zorder=5,
    )
    ax.set_ylabel("Estimated net profit")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.set_major_formatter(lambda x, pos: f"${x/1000:,.0f}K")
    ax.annotate(
        selected_strategy,
        xy=(selected_index, selected_row["estimated_net_profit"]),
        xytext=(selected_index, selected_row["estimated_net_profit"] * 1.05),
        ha="center",
        fontsize=8,
    )
    st.pyplot(fig, clear_figure=True)

st.subheader("Model Lift and Response Capture")
lift_col_1, lift_col_2 = st.columns(2)

with lift_col_1:
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.bar(lift_df["score_Tile"].astype(str), lift_df["response_rate"], color="#7C3AED")
    ax.set_xlabel("Model score decile")
    ax.set_ylabel("Response rate")
    ax.yaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig, clear_figure=True)
    st.caption(
        "Decile 1 contains the highest-scoring customers. A steep drop-off shows the model is useful for prioritizing outreach."
    )

with lift_col_2:
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.plot(
        scenario_df["share_customers_targeted"],
        scenario_df["share_responses_captured"],
        color="#DC2626",
        marker="o",
        linewidth=2.5,
    )
    ax.plot([0, 1], [0, 1], color="#9CA3AF", linestyle="--", linewidth=1)
    ax.scatter(
        [selected_row["share_customers_targeted"]],
        [selected_row["share_responses_captured"]],
        color="#111827",
        s=70,
        zorder=5,
    )
    ax.set_xlabel("Share of customers contacted")
    ax.set_ylabel("Share of responders captured")
    ax.xaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    ax.yaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    ax.grid(color="#E5E7EB", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig, clear_figure=True)
    st.caption(
        "The curve compares model-based targeting against random outreach. Points above the diagonal capture responders faster than random selection."
    )

st.subheader("Threshold Detail")
detail_df = scenario_df[
    [
        "targeting_strategy",
        "customers_targeted",
        "responses_captured",
        "targeted_response_rate",
        "targeted_lift",
        "estimated_contact_cost",
        "estimated_gross_value",
        "estimated_net_profit",
        "roi",
        "cost_per_response",
    ]
].copy()
detail_df.columns = [
    "Threshold",
    "Customers",
    "Responders",
    "Response Rate",
    "Lift",
    "Contact Cost",
    "Gross Value",
    "Net Profit",
    "ROI",
    "Cost / Response",
]
formatted_detail = detail_df.copy()
formatted_detail["Customers"] = formatted_detail["Customers"].map(lambda x: f"{x:,.0f}")
formatted_detail["Responders"] = formatted_detail["Responders"].map(lambda x: f"{x:,.0f}")
formatted_detail["Response Rate"] = formatted_detail["Response Rate"].map(percent)
formatted_detail["Lift"] = formatted_detail["Lift"].map(multiple)
formatted_detail["Contact Cost"] = formatted_detail["Contact Cost"].map(money)
formatted_detail["Gross Value"] = formatted_detail["Gross Value"].map(money)
formatted_detail["Net Profit"] = formatted_detail["Net Profit"].map(money)
formatted_detail["ROI"] = formatted_detail["ROI"].map(multiple)
formatted_detail["Cost / Response"] = formatted_detail["Cost / Response"].map(money_two)
st.table(formatted_detail)

st.caption(
    "Source: Project 1 UCI Bank Marketing response model outputs. The dashboard recalculates financial metrics from the selected cost and value assumptions."
)
