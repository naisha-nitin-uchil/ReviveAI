import pandas as pd
from recovery_agent import decide_recovery_action


# ============================================================
# REVIVEAI - BATCH AGENT VALIDATION
# ============================================================

INPUT_PATH = "data/transactions.csv"
OUTPUT_PATH = "data/agent_decisions.csv"


print("=" * 75)
print("REVIVEAI - 10,000 TRANSACTION AGENT VALIDATION")
print("=" * 75)


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_PATH)

print(f"\nTransactions loaded: {len(df):,}")


# ============================================================
# 2. RUN AGENT ON ALL TRANSACTIONS
# ============================================================

decisions = []

for _, row in df.iterrows():

    transaction = row.to_dict()

    decision = decide_recovery_action(transaction)

    decisions.append(decision)


results = pd.DataFrame(decisions)


# ============================================================
# 3. COMBINE ORIGINAL DATA + AGENT DECISIONS
# ============================================================

results = results.merge(
    df[
        [
            "transaction_id",
            "amount",
            "failure_reason",
            "failure_category",
            "retry_count",
            "recovery_success",
            "recovered_amount"
        ]
    ],
    on="transaction_id",
    how="left"
)


# ============================================================
# 4. SAVE RESULTS
# ============================================================

results.to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"\nAgent results saved to: {OUTPUT_PATH}")


# ============================================================
# 5. BASIC VALIDATION
# ============================================================

print("\n" + "=" * 75)
print("AGENT VALIDATION RESULTS")
print("=" * 75)

print(f"\nTotal transactions processed: {len(results):,}")

print(
    f"Transactions with decisions: "
    f"{results['action'].notna().sum():,}"
)


# ============================================================
# 6. RECOVERY PROBABILITY
# ============================================================

print("\n" + "-" * 75)
print("RECOVERY PROBABILITY")
print("-" * 75)

print(
    results["recovery_probability"]
    .describe()
    .round(3)
)


# ============================================================
# 7. PRIORITY DISTRIBUTION
# ============================================================

print("\n" + "-" * 75)
print("PRIORITY DISTRIBUTION")
print("-" * 75)

priority_counts = (
    results["priority"]
    .value_counts()
)

priority_percent = (
    results["priority"]
    .value_counts(normalize=True) * 100
)

priority_table = pd.DataFrame({
    "Count": priority_counts,
    "Percentage": priority_percent.round(2)
})

print(priority_table)


# ============================================================
# 8. ACTION DISTRIBUTION
# ============================================================

print("\n" + "-" * 75)
print("RECOVERY ACTION DISTRIBUTION")
print("-" * 75)

action_counts = (
    results["action"]
    .value_counts()
)

action_percent = (
    results["action"]
    .value_counts(normalize=True) * 100
)

action_table = pd.DataFrame({
    "Count": action_counts,
    "Percentage": action_percent.round(2)
})

print(action_table)


# ============================================================
# 9. FAILURE CATEGORY VS ACTION
# ============================================================

print("\n" + "-" * 75)
print("FAILURE CATEGORY VS AGENT ACTION")
print("-" * 75)

category_action = pd.crosstab(
    results["failure_category"],
    results["action"]
)

print(category_action)


# ============================================================
# 10. EXPECTED RECOVERABLE REVENUE
# ============================================================

total_expected_recovery = (
    results["expected_recovery"].sum()
)

total_transaction_value = (
    results["amount"].sum()
)

print("\n" + "-" * 75)
print("REVENUE ANALYSIS")
print("-" * 75)

print(
    f"Total transaction value: "
    f"₹{total_transaction_value:,.2f}"
)

print(
    f"Expected recoverable revenue: "
    f"₹{total_expected_recovery:,.2f}"
)


# ============================================================
# 11. PRIORITY REVENUE ANALYSIS
# ============================================================

priority_revenue = (
    results
    .groupby("priority")["expected_recovery"]
    .agg(["count", "sum"])
    .sort_values("sum", ascending=False)
)

priority_revenue.columns = [
    "Transactions",
    "Expected Recovery"
]

print("\n" + "-" * 75)
print("EXPECTED RECOVERY BY PRIORITY")
print("-" * 75)

print(priority_revenue.round(2))


# ============================================================
# 12. GUARDRAIL ANALYSIS
# ============================================================

max_retry_stops = (
    results["reason"]
    .eq("Maximum retry limit reached")
    .sum()
)

low_probability_stops = (
    results["reason"]
    .eq("Recovery probability is too low")
    .sum()
)

customer_low_recovery_stops = (
    results["reason"]
    .eq(
        "Low recovery potential for customer-related failure"
    )
    .sum()
)

print("\n" + "-" * 75)
print("GUARDRAIL ANALYSIS")
print("-" * 75)

print(
    f"Stopped: Maximum retry limit: "
    f"{max_retry_stops:,}"
)

print(
    f"Stopped: Low recovery probability: "
    f"{low_probability_stops:,}"
)

print(
    f"Stopped: Customer-related low potential: "
    f"{customer_low_recovery_stops:,}"
)


# ============================================================
# 13. TOP 10 TRANSACTIONS BY EXPECTED RECOVERY
# ============================================================

print("\n" + "-" * 75)
print("TOP 10 TRANSACTIONS BY EXPECTED RECOVERY")
print("-" * 75)

top_transactions = (
    results[
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
    top_transactions.to_string(
        index=False
    )
)


# ============================================================
# 14. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 75)
print("10,000 TRANSACTION VALIDATION COMPLETE")
print("=" * 75)