import streamlit as st
import pandas as pd


# ============================================================
# REVIVEAI - AI REVENUE RECOVERY CONTROL CENTER
# ============================================================

st.set_page_config(
    page_title="ReviveAI | Revenue Recovery",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL STYLING
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 44px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #9aa4b2;
        margin-top: 0px;
        margin-bottom: 10px;
    }

    .section-title {
        font-size: 27px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    section[data-testid="stSidebar"] {
        background-color: #10141d;
        border-right: 1px solid #293241;
    }

    .filter-header {
        padding: 9px 12px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 7px;
        font-weight: 700;
        font-size: 14px;
    }

    .priority-filter {
        background: rgba(37, 99, 235, 0.15);
        border-left: 4px solid #3b82f6;
        color: #60a5fa;
    }

    .failure-filter {
        background: rgba(245, 158, 11, 0.15);
        border-left: 4px solid #f59e0b;
        color: #fbbf24;
    }

    .action-filter {
        background: rgba(139, 92, 246, 0.15);
        border-left: 4px solid #8b5cf6;
        color: #a78bfa;
    }

    /* Transparent selected filter tags */
    div[data-baseweb="select"] span[data-baseweb="tag"] {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    div[data-baseweb="select"] span[data-baseweb="tag"] span {
        color: inherit !important;
    }

    .online {
        color: #22c55e;
        font-weight: 600;
    }

    .decision-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #172033;
        border: 1px solid #2d3b55;
        margin-bottom: 10px;
    }

    .decision-label {
        color: #9aa4b2;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .decision-value {
        font-size: 24px;
        font-weight: 700;
    }

    .footer-text {
        color: #727b89;
        font-size: 12px;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    decisions = pd.read_csv(
        "data/agent_decisions.csv",
        keep_default_na=False
    )

    recovery = pd.read_csv(
        "data/recovery_results.csv",
        keep_default_na=False
    )

    audit = pd.read_csv(
        "data/audit_log.csv",
        keep_default_na=False
    )

    transactions = pd.read_csv(
        "data/transactions.csv",
        keep_default_na=False
    )

    if "payment_method" not in audit.columns and "payment_method" in transactions.columns:
        payment_methods = transactions[
            ["transaction_id", "payment_method"]
        ].drop_duplicates("transaction_id")

        audit = audit.merge(
            payment_methods,
            on="transaction_id",
            how="left"
        )

    # --------------------------------------------------------
    # Boolean conversion
    # --------------------------------------------------------

    if "recovery_attempted" in recovery.columns:

        recovery["recovery_attempted"] = (
            recovery["recovery_attempted"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                "true": True,
                "false": False,
                "1": True,
                "0": False
            })
            .fillna(False)
        )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_recovery_columns = [
        "amount",
        "expected_recovery",
        "simulated_recovered_amount",
        "recovery_success_simulated"
    ]

    for column in numeric_recovery_columns:

        if column in recovery.columns:

            recovery[column] = pd.to_numeric(
                recovery[column],
                errors="coerce"
            ).fillna(0)

    numeric_audit_columns = [
        "amount",
        "recovery_probability",
        "expected_recovery",
        "recovered_amount",
        "retry_count",
        "retry_delay_minutes"
    ]

    for column in numeric_audit_columns:

        if column in audit.columns:

            audit[column] = pd.to_numeric(
                audit[column],
                errors="coerce"
            ).fillna(0)

    # --------------------------------------------------------
    # Guardrail cleanup
    # --------------------------------------------------------

    if "guardrail_triggered" in audit.columns:

        audit["guardrail_triggered"] = (
            audit["guardrail_triggered"]
            .fillna("None")
            .astype(str)
            .str.strip()
        )

        audit.loc[
            audit["guardrail_triggered"].str.lower().isin(
                ["", "nan", "none"]
            ),
            "guardrail_triggered"
        ] = "None"

    return decisions, recovery, audit


decisions, recovery, audit = load_data()


# ============================================================
# FILTER RESET STATE
# ============================================================

# Streamlit does not allow changing a widget's session_state value
# after that widget has already been instantiated. Instead of
# modifying the multiselect values directly, we create fresh widget
# keys whenever the user presses Reset All Filters.
if "filter_version" not in st.session_state:
    st.session_state["filter_version"] = 0


def reset_filters():
    st.session_state["filter_version"] += 1


filter_version = st.session_state["filter_version"]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# 💰 ReviveAI")

    st.caption(
        "AI Revenue Recovery Control Center"
    )

    st.divider()

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    st.markdown("### 🟢 System Status")

    st.markdown(
        '<span class="online">● ML Model</span> — Online',
        unsafe_allow_html=True
    )

    st.markdown(
        '<span class="online">● Decision Agent</span> — Online',
        unsafe_allow_html=True
    )

    st.markdown(
        '<span class="online">● Recovery Simulator</span> — Online',
        unsafe_allow_html=True
    )

    st.markdown(
        '<span class="online">● Audit Trail</span> — Active',
        unsafe_allow_html=True
    )

    st.divider()


    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.markdown("### 🎛️ Dashboard Filters")

    st.caption(
        "Filters update the dashboard analysis."
    )

    # Priority

    st.markdown(
        """
        <div class="filter-header priority-filter">
        🎯 PRIORITY
        </div>
        """,
        unsafe_allow_html=True
    )

    priority_options = sorted(
        recovery["priority"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_priorities = st.multiselect(
        "Priority",
        priority_options,
        default=[],
        key=f"priority_filter_{filter_version}",
        label_visibility="collapsed"
    )

    # Failure category

    st.markdown(
        """
        <div class="filter-header failure-filter">
        ⚠️ FAILURE CATEGORY
        </div>
        """,
        unsafe_allow_html=True
    )

    failure_options = sorted(
        recovery["failure_category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_failures = st.multiselect(
        "Failure Category",
        failure_options,
        default=[],
        key=f"failure_filter_{filter_version}",
        label_visibility="collapsed"
    )

    # Action

    st.markdown(
        """
        <div class="filter-header action-filter">
        🤖 RECOVERY ACTION
        </div>
        """,
        unsafe_allow_html=True
    )

    action_options = sorted(
        recovery["action"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_actions = st.multiselect(
        "Recovery Action",
        action_options,
        default=[],
        key=f"action_filter_{filter_version}",
        label_visibility="collapsed"
    )

    st.divider()

    # Reset button
    st.button(
        "🔄 Reset All Filters",
        on_click=reset_filters,
        use_container_width=True
    )

    st.divider()

    st.caption("ReviveAI Prototype")
    st.caption("Synthetic transaction data")


# ============================================================
# APPLY FILTERS
# ============================================================

# Empty filters mean "All" — users can select only the filters they need.
filtered_recovery = recovery.copy()

if selected_priorities:
    filtered_recovery = filtered_recovery[
        filtered_recovery["priority"].isin(selected_priorities)
    ]

if selected_failures:
    filtered_recovery = filtered_recovery[
        filtered_recovery["failure_category"].isin(selected_failures)
    ]

if selected_actions:
    filtered_recovery = filtered_recovery[
        filtered_recovery["action"].isin(selected_actions)
    ]

filtered_recovery = filtered_recovery.copy()


filtered_transaction_ids = set(
    filtered_recovery["transaction_id"]
)

filtered_audit = audit[
    audit["transaction_id"].isin(
        filtered_transaction_ids
    )
].copy()


# ============================================================
# METRICS
# ============================================================

total_transactions = len(
    filtered_recovery
)

actionable_transactions = int(
    filtered_recovery[
        "recovery_attempted"
    ].sum()
)

stopped_transactions = (
    total_transactions -
    actionable_transactions
)

successful_recoveries = int(
    filtered_recovery[
        "recovery_success_simulated"
    ].sum()
)

simulated_revenue = float(
    filtered_recovery[
        "simulated_recovered_amount"
    ].sum()
)

total_expected_recovery = float(
    filtered_recovery[
        "expected_recovery"
    ].sum()
)

actionable_expected_recovery = float(
    filtered_recovery.loc[
        filtered_recovery["recovery_attempted"],
        "expected_recovery"
    ].sum()
)

total_transaction_value = float(
    filtered_recovery[
        "amount"
    ].sum()
)

stopped_transaction_value = float(
    filtered_recovery.loc[
        ~filtered_recovery["recovery_attempted"],
        "amount"
    ].sum()
)

recovery_rate = (
    successful_recoveries /
    actionable_transactions
    if actionable_transactions > 0
    else 0
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💰 ReviveAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Revenue Recovery Control Center'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "ReviveAI predicts recovery potential, selects the "
    "best recovery action, applies business guardrails, "
    "and tracks simulated outcomes."
)

st.divider()


# ============================================================
# FILTER STATUS
# ============================================================

if len(filtered_recovery) == 0:

    st.error(
        "No transactions match the selected filters. "
        "Please adjust the filters."
    )

else:

    st.info(
        f"Showing **{len(filtered_recovery):,}** of "
        f"**{len(recovery):,}** transactions."
    )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Executive Overview'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Transactions",
        f"{total_transactions:,}"
    )

with col2:

    st.metric(
        "Actionable",
        f"{actionable_transactions:,}"
    )

with col3:

    st.metric(
        "Expected Recovery",
        f"₹{actionable_expected_recovery / 100000:.2f} L"
    )

with col4:

    st.metric(
        "Simulated Recovery",
        f"₹{simulated_revenue / 100000:.2f} L"
    )


st.write("")


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Recovery Rate",
        f"{recovery_rate * 100:.2f}%"
    )

with col2:

    st.metric(
        "Successful Recoveries",
        f"{successful_recoveries:,}"
    )

with col3:

    st.metric(
        "Stopped by Guardrails",
        f"{stopped_transactions:,}"
    )

with col4:

    st.metric(
        "Transaction Value",
        f"₹{total_transaction_value / 100000:.2f} L"
    )


# ============================================================
# TABS
# ============================================================

overview_tab, agent_tab, explorer_tab = st.tabs(
    [
        "📊 Recovery Overview",
        "🤖 Agent Intelligence",
        "🔎 Transaction Explorer"
    ]
)


# ============================================================
# RECOVERY OVERVIEW
# ============================================================

with overview_tab:

    st.markdown(
        '<div class="section-title">'
        '📊 Revenue Recovery Overview'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # ACTION RECOVERY
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "💰 Simulated Recovery by Action"
        )

        action_revenue = (
            filtered_recovery[
                filtered_recovery[
                    "recovery_attempted"
                ]
            ]
            .groupby("action")[
                "simulated_recovered_amount"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if len(action_revenue) > 0:

            st.bar_chart(
                action_revenue
            )

        else:

            st.info(
                "No recovery attempts."
            )

    # --------------------------------------------------------
    # PRIORITY RECOVERY
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "🎯 Expected Recovery by Priority"
        )

        priority_revenue = (
            filtered_recovery[
                filtered_recovery[
                    "recovery_attempted"
                ]
            ]
            .groupby("priority")[
                "expected_recovery"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if len(priority_revenue) > 0:

            st.bar_chart(
                priority_revenue
            )

        else:

            st.info(
                "No recovery data."
            )

    # --------------------------------------------------------
    # FAILURE CATEGORY
    # --------------------------------------------------------

    st.subheader(
        "⚠️ Recovery Opportunity by Failure Category"
    )

    category_data = (
        filtered_recovery[
            filtered_recovery[
                "recovery_attempted"
            ]
        ]
        .groupby("failure_category")
        .agg(
            transactions=(
                "transaction_id",
                "count"
            ),
            expected_recovery=(
                "expected_recovery",
                "sum"
            ),
            simulated_recovery=(
                "simulated_recovered_amount",
                "sum"
            )
        )
        .sort_values(
            "expected_recovery",
            ascending=False
        )
    )

    if len(category_data) > 0:

        st.dataframe(
            category_data.round(2),
            use_container_width=True
        )

    else:

        st.info(
            "No actionable transactions."
        )

    # --------------------------------------------------------
    # RECOVERY FUNNEL
    # --------------------------------------------------------

    st.subheader(
        "🔄 Recovery Funnel"
    )

    f1, f2, f3, f4 = st.columns(4)

    with f1:

        st.metric(
            "Failed Transactions",
            f"{total_transactions:,}"
        )

    with f2:

        st.metric(
            "Recovery Attempts",
            f"{actionable_transactions:,}"
        )

    with f3:

        st.metric(
            "Successful",
            f"{successful_recoveries:,}"
        )

    with f4:

        st.metric(
            "Revenue Recovered",
            f"₹{simulated_revenue / 100000:.2f} L"
        )

    # --------------------------------------------------------
    # REVENUE PROTECTION
    # --------------------------------------------------------

    st.subheader(
        "🛡️ Revenue Protection"
    )

    p1, p2 = st.columns(2)

    with p1:

        st.metric(
            "Stopped Transaction Value",
            f"₹{stopped_transaction_value / 100000:.2f} L"
        )

    with p2:

        st.metric(
            "AI Recovery Potential",
            f"₹{total_expected_recovery / 100000:.2f} L"
        )


# ============================================================
# AGENT INTELLIGENCE
# ============================================================

with agent_tab:

    st.markdown(
        '<div class="section-title">'
        '🤖 ReviveAI Decision Intelligence'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "The decision agent converts recovery probability "
        "into an actionable recovery strategy while "
        "respecting business guardrails."
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # ACTION DISTRIBUTION
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "⚡ Agent Action Distribution"
        )

        action_distribution = (
            filtered_recovery[
                "action"
            ]
            .value_counts()
        )

        if len(action_distribution) > 0:

            st.bar_chart(
                action_distribution
            )

        else:

            st.info(
                "No actions available."
            )

    # --------------------------------------------------------
    # GUARDRAIL DISTRIBUTION
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "🛡️ Guardrail Distribution"
        )

        guardrail_distribution = (
            filtered_audit[
                filtered_audit[
                    "guardrail_triggered"
                ] != "None"
            ][
                "guardrail_triggered"
            ]
            .value_counts()
        )

        if len(guardrail_distribution) > 0:

            st.bar_chart(
                guardrail_distribution
            )

        else:

            st.success(
                "No guardrails triggered."
            )

    # --------------------------------------------------------
    # ACTION PERFORMANCE
    # --------------------------------------------------------

    st.subheader(
        "📈 Recovery Action Performance"
    )

    action_performance = (
        filtered_recovery[
            filtered_recovery[
                "recovery_attempted"
            ]
        ]
        .groupby("action")
        .agg(
            transactions=(
                "transaction_id",
                "count"
            ),
            successful_recoveries=(
                "recovery_success_simulated",
                "sum"
            ),
            expected_recovery=(
                "expected_recovery",
                "sum"
            ),
            actual_recovered=(
                "simulated_recovered_amount",
                "sum"
            )
        )
    )

    if len(action_performance) > 0:

        action_performance[
            "recovery_rate"
        ] = (
            action_performance[
                "successful_recoveries"
            ]
            /
            action_performance[
                "transactions"
            ]
            * 100
        ).round(2)

        st.dataframe(
            action_performance.round(2),
            use_container_width=True
        )

    else:

        st.info(
            "No actionable transactions."
        )

    # --------------------------------------------------------
    # TOP OPPORTUNITIES
    # --------------------------------------------------------

    st.subheader(
        "💎 Top Recovery Opportunities"
    )

    top_opportunities = (
        filtered_recovery[
            filtered_recovery[
                "recovery_attempted"
            ]
        ][
            [
                "transaction_id",
                "amount",
                "failure_reason",
                "recovery_probability",
                "expected_recovery",
                "priority",
                "action"
            ]
        ]
        .sort_values(
            "expected_recovery",
            ascending=False
        )
        .head(10)
        .copy()
    )

    if len(top_opportunities) > 0:

        top_opportunities[
            "recovery_probability"
        ] = (
            top_opportunities[
                "recovery_probability"
            ] * 100
        ).round(1)

        st.dataframe(
            top_opportunities.round(2),
            use_container_width=True
        )

    else:

        st.info(
            "No recovery opportunities."
        )

    # --------------------------------------------------------
    # GUARDRAIL SUMMARY
    # --------------------------------------------------------

    st.subheader(
        "🛡️ Guardrail Analysis"
    )

    guardrail_summary = (
        filtered_audit[
            filtered_audit[
                "guardrail_triggered"
            ] != "None"
        ]
        .groupby(
            "guardrail_triggered"
        )
        .size()
        .reset_index(
            name="Transactions Stopped"
        )
        .sort_values(
            "Transactions Stopped",
            ascending=False
        )
    )

    if len(guardrail_summary) > 0:

        st.dataframe(
            guardrail_summary,
            hide_index=True,
            use_container_width=True
        )

    else:

        st.success(
            "No guardrails triggered."
        )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.subheader(
        "📥 Export"
    )

    csv_data = (
        filtered_recovery
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "⬇️ Download Filtered Transactions",
        data=csv_data,
        file_name="reviveai_filtered_transactions.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# TRANSACTION EXPLORER
# ============================================================

with explorer_tab:

    st.markdown(
        '<div class="section-title">'
        '🔎 Transaction-Level AI Explainability'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Search a transaction to understand exactly "
        "what ReviveAI predicted, decided, and simulated."
    )

    # --------------------------------------------------------
    # RANDOM TRANSACTION LOGIC
    #
    # IMPORTANT:
    # We handle the random button BEFORE creating
    # the text input widget. This prevents the
    # Streamlit session-state error.
    # --------------------------------------------------------

    if "selected_transaction" not in st.session_state:

        st.session_state[
            "selected_transaction"
        ] = ""

    random_col1, random_col2 = st.columns(
        [4, 1]
    )

    with random_col1:

        transaction_id = st.text_input(
            "Transaction ID",
            value=st.session_state[
                "selected_transaction"
            ],
            placeholder="Example: TXN103618"
        )

        st.session_state[
            "selected_transaction"
        ] = transaction_id

    with random_col2:

        st.write("")

        if st.button(
            "🎲 Random",
            use_container_width=True
        ):

            if len(filtered_recovery) > 0:

                random_transaction = (
                    filtered_recovery
                    .sample(1)
                    [
                        "transaction_id"
                    ]
                    .iloc[0]
                )

                st.session_state[
                    "selected_transaction"
                ] = random_transaction

                st.rerun()

            else:

                st.warning(
                    "No transactions available."
                )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    transaction_id = (
        str(
            st.session_state[
                "selected_transaction"
            ]
        )
        .strip()
        .upper()
    )

    if transaction_id:

        transaction = filtered_audit[
            filtered_audit[
                "transaction_id"
            ] == transaction_id
        ]

        # ----------------------------------------------------
        # NOT FOUND
        # ----------------------------------------------------

        if len(transaction) == 0:

            st.warning(
                "Transaction not found in the current "
                "filter selection."
            )

        else:

            row = transaction.iloc[0]

            st.divider()

            st.subheader(
                f"Transaction: {row['transaction_id']}"
            )

            # ------------------------------------------------
            # KPIs
            # ------------------------------------------------

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "Amount",
                    f"₹{float(row['amount']):,.2f}"
                )

            with c2:

                st.metric(
                    "Recovery Probability",
                    f"{float(row['recovery_probability']) * 100:.1f}%"
                )

            with c3:

                st.metric(
                    "Expected Recovery",
                    f"₹{float(row['expected_recovery']):,.2f}"
                )

            with c4:

                st.metric(
                    "Priority",
                    str(row["priority"])
                )

            # ------------------------------------------------
            # DETAILS
            # ------------------------------------------------

            st.subheader(
                "📋 Transaction Details"
            )

            d1, d2 = st.columns(2)

            with d1:

                st.write(
                    f"**Failure Reason:** "
                    f"{row['failure_reason']}"
                )

                st.write(
                    f"**Failure Category:** "
                    f"{row['failure_category']}"
                )

                st.write(
                    f"**Payment Method:** "
                    f"{row['payment_method']}"
                )

            with d2:

                st.write(
                    f"**Retry Count:** "
                    f"{row['retry_count']}"
                )

                st.write(
                    f"**Recovery Attempted:** "
                    f"{row['recovery_attempted']}"
                )

                st.write(
                    f"**Outcome:** "
                    f"{row['outcome']}"
                )

            # ------------------------------------------------
            # AI DECISION
            # ------------------------------------------------

            st.subheader(
                "🤖 AI Recovery Decision"
            )

            decision1, decision2 = st.columns(2)

            with decision1:

                st.markdown(
                    f"""
                    <div class="decision-box">

                    <div class="decision-label">
                    RECOMMENDED ACTION
                    </div>

                    <div class="decision-value">
                    {row['action']}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with decision2:

                guardrail = row[
                    "guardrail_triggered"
                ]

                if (
                    pd.isna(guardrail)
                    or
                    str(
                        guardrail
                    ).strip().lower()
                    in [
                        "",
                        "nan",
                        "none"
                    ]
                ):

                    guardrail = "None"

                st.markdown(
                    f"""
                    <div class="decision-box">

                    <div class="decision-label">
                    GUARDRAIL
                    </div>

                    <div class="decision-value">
                    {guardrail}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.write(
                f"**Decision Reason:** "
                f"{row['reason']}"
            )

            st.write(
                f"**Retry Delay:** "
                f"{row['retry_delay_minutes']} minutes"
            )

            # ------------------------------------------------
            # EXPLANATION
            # ------------------------------------------------

            st.subheader(
                "🧠 Why did ReviveAI make this decision?"
            )

            probability = (
                float(
                    row[
                        "recovery_probability"
                    ]
                ) * 100
            )

            explanation = (
                f"ReviveAI estimated a "
                f"{probability:.1f}% recovery probability. "
                f"The payment failure was classified as "
                f"'{row['failure_category']}'. "
                f"The transaction received "
                f"'{row['priority']}' priority. "
                f"Considering these signals and the "
                f"configured recovery rules, the agent "
                f"recommended '{row['action']}'."
            )

            st.info(
                explanation
            )

            # ------------------------------------------------
            # OUTCOME
            # ------------------------------------------------

            st.subheader(
                "📈 Recovery Outcome"
            )

            outcome = str(
                row["outcome"]
            )

            recovered_amount = float(
                row["recovered_amount"]
            )

            if outcome == "Recovered":

                st.success(
                    f"✅ Recovery succeeded in the simulation. "
                    f"Simulated recovered amount: "
                    f"₹{recovered_amount:,.2f}"
                )

            elif outcome == "Recovery Failed":

                st.error(
                    "❌ Recovery was attempted, "
                    "but the simulated recovery failed."
                )

            else:

                st.warning(
                    "🛡️ Recovery was intentionally not attempted "
                    "because ReviveAI stopped the transaction "
                    "using its decision logic or guardrails."
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer-text">

    <b>ReviveAI Prototype</b> |
    AI Revenue Recovery |
    Synthetic Transaction Dataset |

    Recovery outcomes are simulated and do not represent
    real payment recovery performance.

    </div>
    """,
    unsafe_allow_html=True
)