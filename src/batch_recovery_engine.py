import pandas as pd

from recovery_agent import decide_recovery_action


# ============================================================
# REVIVEAI - BATCH RECOVERY ENGINE
# ============================================================

INPUT_PATH = "data/transactions.csv"
OUTPUT_PATH = "data/agent_decisions.csv"


def run_batch_recovery(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    """
    Process a complete batch of failed payment transactions
    through the ReviveAI decision agent.
    """

    print("=" * 75)
    print("REVIVEAI - BATCH RECOVERY ENGINE")
    print("=" * 75)

    # --------------------------------------------------------
    # 1. LOAD TRANSACTIONS
    # --------------------------------------------------------

    df = pd.read_csv(input_path)

    print(f"\nTransactions loaded: {len(df):,}")

    # --------------------------------------------------------
    # 2. PROCESS EACH TRANSACTION
    # --------------------------------------------------------

    decisions = []

    for _, row in df.iterrows():

        transaction = row.to_dict()

        decision = decide_recovery_action(
            transaction
        )

        decisions.append(decision)

    results = pd.DataFrame(decisions)

    # --------------------------------------------------------
    # 3. ADD ORIGINAL TRANSACTION INFORMATION
    # --------------------------------------------------------

    original_columns = [
        "transaction_id",
        "amount",
        "payment_method",
        "failure_reason",
        "failure_category",
        "retry_count"
    ]

    original_data = df[original_columns]

    results = results.merge(
        original_data,
        on="transaction_id",
        how="left"
    )

    # --------------------------------------------------------
    # 4. ORDER COLUMNS
    # --------------------------------------------------------

    column_order = [
        "transaction_id",
        "amount",
        "payment_method",
        "failure_reason",
        "failure_category",
        "retry_count",
        "recovery_probability",
        "expected_recovery",
        "priority",
        "action",
        "reason",
        "retry_delay_minutes"
    ]

    results = results[column_order]

    # --------------------------------------------------------
    # 5. SAVE RESULTS
    # --------------------------------------------------------

    results.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nAgent decisions saved to: "
        f"{output_path}"
    )

    # --------------------------------------------------------
    # 6. SUMMARY
    # --------------------------------------------------------

    actionable = results[
        results["action"] != "Stop Recovery"
    ]

    stopped = results[
        results["action"] == "Stop Recovery"
    ]

    print("\n" + "=" * 75)
    print("BATCH RECOVERY SUMMARY")
    print("=" * 75)

    print(
        f"\nTotal transactions: "
        f"{len(results):,}"
    )

    print(
        f"Actionable transactions: "
        f"{len(actionable):,}"
    )

    print(
        f"Stopped transactions: "
        f"{len(stopped):,}"
    )

    print(
        f"\nTotal transaction value: "
        f"₹{results['amount'].sum():,.2f}"
    )

    print(
        f"Expected recoverable revenue: "
        f"₹{results['expected_recovery'].sum():,.2f}"
    )

    print(
        f"Actionable expected recovery: "
        f"₹{actionable['expected_recovery'].sum():,.2f}"
    )

    # --------------------------------------------------------
    # 7. ACTION DISTRIBUTION
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("RECOVERY ACTIONS")
    print("-" * 75)

    action_summary = (
        results["action"]
        .value_counts()
        .to_frame("Transactions")
    )

    action_summary["Percentage"] = (
        action_summary["Transactions"]
        / len(results)
        * 100
    )

    print(
        action_summary.round(2)
    )

    # --------------------------------------------------------
    # 8. PRIORITY DISTRIBUTION
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("PRIORITY DISTRIBUTION")
    print("-" * 75)

    priority_summary = (
        results["priority"]
        .value_counts()
        .to_frame("Transactions")
    )

    priority_summary["Percentage"] = (
        priority_summary["Transactions"]
        / len(results)
        * 100
    )

    print(
        priority_summary.round(2)
    )

    # --------------------------------------------------------
    # 9. EXPECTED RECOVERY BY ACTION
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("EXPECTED RECOVERY BY ACTION")
    print("-" * 75)

    action_revenue = (
        results
        .groupby("action")["expected_recovery"]
        .agg(
            Transactions="count",
            Expected_Recovery="sum"
        )
        .sort_values(
            "Expected_Recovery",
            ascending=False
        )
    )

    print(
        action_revenue.round(2)
    )

    # --------------------------------------------------------
    # 10. TOP RECOVERY OPPORTUNITIES
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("TOP 10 RECOVERY OPPORTUNITIES")
    print("-" * 75)

    top_opportunities = (
        actionable[
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
    )

    print(
        top_opportunities.to_string(
            index=False
        )
    )

    print("\n" + "=" * 75)
    print("BATCH RECOVERY ENGINE COMPLETE")
    print("=" * 75)

    return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_batch_recovery()