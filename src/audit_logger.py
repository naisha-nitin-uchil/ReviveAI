import pandas as pd
from datetime import datetime


# ============================================================
# REVIVEAI - AUDIT LOGGER
# ============================================================

DECISIONS_PATH = "data/agent_decisions.csv"
RECOVERY_RESULTS_PATH = "data/recovery_results.csv"
AUDIT_PATH = "data/audit_log.csv"


def create_audit_log():
    """
    Combine agent decisions and recovery outcomes
    into a complete audit trail.
    """

    print("=" * 75)
    print("REVIVEAI - AUDIT LOGGER")
    print("=" * 75)

    # --------------------------------------------------------
    # 1. LOAD AGENT DECISIONS
    # --------------------------------------------------------

    decisions = pd.read_csv(DECISIONS_PATH)

    print(
        f"\nAgent decisions loaded: "
        f"{len(decisions):,}"
    )

    # --------------------------------------------------------
    # 2. LOAD RECOVERY RESULTS
    # --------------------------------------------------------

    recovery = pd.read_csv(
        RECOVERY_RESULTS_PATH
    )

    print(
        f"Recovery results loaded: "
        f"{len(recovery):,}"
    )

    # --------------------------------------------------------
    # 3. SELECT RECOVERY OUTCOME FIELDS
    # --------------------------------------------------------

    recovery_columns = [
        "transaction_id",
        "recovery_attempted",
        "recovery_success_simulated",
        "simulated_recovered_amount"
    ]

    recovery_data = recovery[
        recovery_columns
    ]

    # --------------------------------------------------------
    # 4. MERGE DECISIONS + OUTCOMES
    # --------------------------------------------------------

    audit = decisions.merge(
        recovery_data,
        on="transaction_id",
        how="left"
    )

    # --------------------------------------------------------
    # 5. ADD TIMESTAMP
    # --------------------------------------------------------

    audit["decision_timestamp"] = (
        datetime.now().isoformat(
            timespec="seconds"
        )
    )

    # --------------------------------------------------------
    # 6. DETERMINE GUARDRAIL STATUS
    # --------------------------------------------------------

    def get_guardrail(row):

        reason = row["reason"]
        action = row["action"]

    # Actual stopping guardrail
        if action == "Stop Recovery":

            if "Maximum retry" in reason:
                return "Maximum Retry Limit"

            elif "probability is too low" in reason:
                return "Low Recovery Probability"

            elif "customer-related" in reason:
                return "Low Customer Recovery Potential"

        # High-value escalation is a guardrail
        if "High-value transaction" in reason:
            return "High Value Transaction"

        return "None"

    audit["guardrail_triggered"] = audit.apply(
        get_guardrail,
        axis=1
)

    # --------------------------------------------------------
    # 7. CREATE HUMAN-READABLE OUTCOME
    # --------------------------------------------------------

    def get_outcome(row):

        if not row["recovery_attempted"]:
            return "Recovery Not Attempted"

        if row["recovery_success_simulated"] == 1:
            return "Recovered"

        return "Recovery Failed"

    audit["outcome"] = audit.apply(
        get_outcome,
        axis=1
    )

    # --------------------------------------------------------
# 8. USE SIMULATED RECOVERED AMOUNT
# --------------------------------------------------------

    audit["recovered_amount"] = audit[
        "simulated_recovered_amount"
    ]

    audit = audit.drop(
        columns=["simulated_recovered_amount"]
    )

    # --------------------------------------------------------
    # 9. SELECT FINAL AUDIT FIELDS
    # --------------------------------------------------------

    audit_columns = [
        "decision_timestamp",
        "transaction_id",
        "amount",
        "failure_reason",
        "failure_category",
        "retry_count",
        "recovery_probability",
        "expected_recovery",
        "priority",
        "action",
        "reason",
        "retry_delay_minutes",
        "guardrail_triggered",
        "recovery_attempted",
        "outcome",
        "recovered_amount"
    ]

    audit = audit[
        audit_columns
    ]

    # --------------------------------------------------------
    # 10. SAVE AUDIT LOG
    # --------------------------------------------------------

    audit.to_csv(
        AUDIT_PATH,
        index=False
    )

    print(
        f"\nAudit log saved to: "
        f"{AUDIT_PATH}"
    )

    # --------------------------------------------------------
    # 11. AUDIT SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("AUDIT TRAIL SUMMARY")
    print("=" * 75)

    print(
        f"\nTotal audit records: "
        f"{len(audit):,}"
    )

    print("\nOutcomes:")

    print(
        audit["outcome"]
        .value_counts()
    )

    print("\nGuardrails triggered:")

    print(
        audit["guardrail_triggered"]
        .value_counts()
    )

    # --------------------------------------------------------
    # 12. RECOVERED REVENUE
    # --------------------------------------------------------

    total_recovered = (
        audit["recovered_amount"].sum()
    )

    print(
        f"\nTotal simulated revenue recovered: "
        f"₹{total_recovered:,.2f}"
    )

    # --------------------------------------------------------
    # 13. SAMPLE AUDIT RECORDS
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("SAMPLE AUDIT RECORDS")
    print("-" * 75)

    print(
        audit.head(10).to_string(
            index=False
        )
    )

    print("\n" + "=" * 75)
    print("AUDIT LOGGING COMPLETE")
    print("=" * 75)

    return audit


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_audit_log()