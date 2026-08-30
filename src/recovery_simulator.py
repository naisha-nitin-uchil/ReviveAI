import numpy as np
import pandas as pd


# ============================================================
# REVIVEAI - RECOVERY SIMULATOR
# ============================================================

INPUT_PATH = "data/agent_decisions.csv"
OUTPUT_PATH = "data/recovery_results.csv"

# Reproducibility
np.random.seed(42)


# ============================================================
# 1. LOAD AGENT DECISIONS
# ============================================================

df = pd.read_csv(INPUT_PATH)

print("=" * 75)
print("REVIVEAI - RECOVERY SIMULATION")
print("=" * 75)

print(f"\nTransactions loaded: {len(df):,}")


# ============================================================
# 2. DETERMINE WHETHER RECOVERY IS ATTEMPTED
# ============================================================

df["recovery_attempted"] = (
    df["action"] != "Stop Recovery"
)


# ============================================================
# 3. SIMULATE RECOVERY OUTCOME
# ============================================================

def simulate_recovery(row):

    # No recovery attempt
    if not row["recovery_attempted"]:
        return 0

    probability = row["recovery_probability"]

    action = row["action"]

    # --------------------------------------------------------
    # Action-specific adjustment
    # --------------------------------------------------------

    if action == "Retry After Delay":
        action_factor = 1.05

    elif action == "Retry":
        action_factor = 0.95

    elif action == "Send Payment Reminder":
        action_factor = 0.85

    elif action == "Suggest Alternate Payment Method":
        action_factor = 1.00

    elif action == "Escalate":
        action_factor = 0.75

    else:
        action_factor = 0.00

    effective_probability = (
        probability * action_factor
    )

    effective_probability = min(
        effective_probability,
        0.95
    )

    return int(
        np.random.random() < effective_probability
    )


df["recovery_success_simulated"] = df.apply(
    simulate_recovery,
    axis=1
)


# ============================================================
# 4. CALCULATE RECOVERED REVENUE
# ============================================================

df["simulated_recovered_amount"] = np.where(
    df["recovery_success_simulated"] == 1,
    df["amount"],
    0
)


# ============================================================
# 5. CALCULATE RECOVERY RATE
# ============================================================

attempted_count = df["recovery_attempted"].sum()

successful_count = (
    df["recovery_success_simulated"].sum()
)

if attempted_count > 0:
    recovery_rate = (
        successful_count / attempted_count
    )
else:
    recovery_rate = 0


# ============================================================
# 6. FINANCIAL METRICS
# ============================================================

total_transaction_value = df["amount"].sum()

total_expected_recovery = (
    df["expected_recovery"].sum()
)

actionable_expected_recovery = (
    df.loc[
        df["recovery_attempted"],
        "expected_recovery"
    ].sum()
)

actual_simulated_recovery = (
    df["simulated_recovered_amount"].sum()
)

stopped_revenue = (
    df.loc[
        ~df["recovery_attempted"],
        "amount"
    ].sum()
)

# Difference between AI expectation and simulated result
expected_vs_actual_difference = (
    actual_simulated_recovery
    - actionable_expected_recovery
)


# ============================================================
# 7. SAVE RESULTS
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    f"\nSimulation results saved to: "
    f"{OUTPUT_PATH}"
)


# ============================================================
# 8. OVERALL RESULTS
# ============================================================

print("\n" + "=" * 75)
print("SIMULATION RESULTS")
print("=" * 75)

print(
    f"\nTotal transaction value: "
    f"₹{total_transaction_value:,.2f}"
)

print(
    f"Total AI-estimated recovery: "
    f"₹{total_expected_recovery:,.2f}"
)

print(
    f"Actionable expected recovery: "
    f"₹{actionable_expected_recovery:,.2f}"
)

print(
    f"Recovery attempts: "
    f"{attempted_count:,}"
)

print(
    f"Successful recoveries: "
    f"{successful_count:,}"
)

print(
    f"Recovery rate: "
    f"{recovery_rate * 100:.2f}%"
)

print(
    f"Simulated revenue recovered: "
    f"₹{actual_simulated_recovery:,.2f}"
)

print(
    f"Expected vs actual difference: "
    f"₹{expected_vs_actual_difference:,.2f}"
)

print(
    f"Revenue from stopped transactions: "
    f"₹{stopped_revenue:,.2f}"
)


# ============================================================
# 9. RESULTS BY ACTION
# ============================================================

print("\n" + "-" * 75)
print("RECOVERY RESULTS BY ACTION")
print("-" * 75)

action_results = (
    df[df["recovery_attempted"]]
    .groupby("action")
    .agg(
        transactions=("transaction_id", "count"),
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

action_results["recovery_rate"] = (
    action_results["successful_recoveries"]
    / action_results["transactions"]
)

print(
    action_results
    .sort_values(
        "actual_recovered",
        ascending=False
    )
    .round(2)
)


# ============================================================
# 10. RESULTS BY PRIORITY
# ============================================================

print("\n" + "-" * 75)
print("RECOVERY RESULTS BY PRIORITY")
print("-" * 75)

priority_results = (
    df[df["recovery_attempted"]]
    .groupby("priority")
    .agg(
        transactions=("transaction_id", "count"),
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

priority_results["recovery_rate"] = (
    priority_results["successful_recoveries"]
    / priority_results["transactions"]
)

print(
    priority_results
    .sort_values(
        "actual_recovered",
        ascending=False
    )
    .round(2)
)


# ============================================================
# 11. TOP RECOVERIES
# ============================================================

print("\n" + "-" * 75)
print("TOP 10 SIMULATED RECOVERIES")
print("-" * 75)

top_recoveries = (
    df[
        df["recovery_success_simulated"] == 1
    ][
        [
            "transaction_id",
            "amount",
            "failure_reason",
            "recovery_probability",
            "expected_recovery",
            "priority",
            "action",
            "simulated_recovered_amount"
        ]
    ]
    .sort_values(
        "simulated_recovered_amount",
        ascending=False
    )
    .head(10)
)

print(
    top_recoveries.to_string(
        index=False
    )
)


# ============================================================
# 12. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 75)
print("REVIVEAI RECOVERY SIMULATION COMPLETE")
print("=" * 75)