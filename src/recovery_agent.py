import joblib
import pandas as pd


# ============================================================
# REVIVEAI - RECOVERY DECISION AGENT
# ============================================================

MODEL_PATH = "models/recovery_prediction_model.pkl"

# Load trained ML model
model = joblib.load(MODEL_PATH)


# ============================================================
# BUSINESS GUARDRAILS
# ============================================================

MAX_RETRIES = 2

HIGH_VALUE_THRESHOLD = 50000


# ============================================================
# PRIORITY CALCULATION
# ============================================================

def calculate_priority(expected_recovery):

    if expected_recovery >= 10000:
        return "HIGH"

    elif expected_recovery >= 2500:
        return "MEDIUM"

    elif expected_recovery >= 500:
        return "LOW"

    else:
        return "VERY LOW"


# ============================================================
# RECOVERY DECISION
# ============================================================

def decide_recovery_action(transaction):

    # --------------------------------------------------------
    # 1. Prepare model input
    # --------------------------------------------------------

    input_data = pd.DataFrame([{
        "amount": transaction["amount"],
        "payment_method": transaction["payment_method"],
        "transaction_hour": transaction["transaction_hour"],
        "transaction_day": transaction["transaction_day"],
        "failure_reason": transaction["failure_reason"],
        "failure_category": transaction["failure_category"],
        "previous_transaction_count": transaction[
            "previous_transaction_count"
        ],
        "previous_success_count": transaction[
            "previous_success_count"
        ],
        "previous_failure_count": transaction[
            "previous_failure_count"
        ],
        "customer_success_rate": transaction[
            "customer_success_rate"
        ],
        "days_since_last_success": transaction[
            "days_since_last_success"
        ],
        "retry_count": transaction["retry_count"]
    }])

    # --------------------------------------------------------
    # 2. AI prediction
    # --------------------------------------------------------

    recovery_probability = model.predict_proba(
        input_data
    )[0][1]

    recovery_probability = float(recovery_probability)

    # --------------------------------------------------------
    # 3. Expected recoverable revenue
    # --------------------------------------------------------

    expected_recovery = (
        transaction["amount"] * recovery_probability
    )

    # --------------------------------------------------------
    # 4. Determine priority
    # --------------------------------------------------------

    priority = calculate_priority(
    expected_recovery
)

    # --------------------------------------------------------
    # 5. STOPPING RULE - MAX RETRIES
    # --------------------------------------------------------

    if transaction["retry_count"] >= MAX_RETRIES:

        return {
            "transaction_id": transaction["transaction_id"],
            "recovery_probability": round(
                recovery_probability, 3
            ),
            "expected_recovery": round(
                expected_recovery, 2
            ),
            "priority": priority,
            "action": "Stop Recovery",
            "reason": "Maximum retry limit reached",
            "retry_delay_minutes": 0
        }

    # --------------------------------------------------------
    # 6. VERY LOW RECOVERY POTENTIAL
    # --------------------------------------------------------

    if recovery_probability < 0.20:

        return {
            "transaction_id": transaction["transaction_id"],
            "recovery_probability": round(
                recovery_probability, 3
            ),
            "expected_recovery": round(
                expected_recovery, 2
            ),
            "priority": priority,
            "action": "Stop Recovery",
            "reason": "Recovery probability is too low",
            "retry_delay_minutes": 0
        }

    # --------------------------------------------------------
    # 7. TEMPORARY FAILURE
    # --------------------------------------------------------

    if transaction["failure_category"] == "Temporary":

        if recovery_probability >= 0.70:

            action = "Retry After Delay"
            delay = 10

            reason = (
                "Temporary failure with high recovery probability"
            )

        elif recovery_probability >= 0.50:

            action = "Retry"
            delay = 0

            reason = (
                "Temporary failure with moderate recovery probability"
            )

        else:

            action = "Send Payment Reminder"
            delay = 30

            reason = (
                "Temporary failure with limited recovery probability"
            )

    # --------------------------------------------------------
    # 8. CUSTOMER-RELATED FAILURE
    # --------------------------------------------------------

    elif transaction["failure_category"] == "Customer Related":

        if recovery_probability >= 0.70:

            action = "Suggest Alternate Payment Method"
            delay = 5

            reason = (
                "Customer-related failure with high recovery potential"
            )

        elif recovery_probability >= 0.40:

            action = "Send Payment Reminder"
            delay = 60

            reason = (
                "Customer action may be required"
            )

        else:

            action = "Stop Recovery"
            delay = 0

            reason = (
                "Low recovery potential for customer-related failure"
            )

    # --------------------------------------------------------
    # 9. TECHNICAL FAILURE
    # --------------------------------------------------------

    else:

        if recovery_probability >= 0.65:

            action = "Retry"
            delay = 0

            reason = (
                "Technical failure with high recovery potential"
            )

        elif recovery_probability >= 0.40:

            action = "Retry After Delay"
            delay = 15

            reason = (
                "Delayed retry may resolve the technical issue"
            )

        else:

            action = "Escalate"
            delay = 0

            reason = (
                "Low recovery probability requires investigation"
            )

    # --------------------------------------------------------
    # 10. HIGH-VALUE TRANSACTION GUARDRAIL
    # --------------------------------------------------------

    if (
        transaction["amount"] >= HIGH_VALUE_THRESHOLD
        and action == "Retry"
    ):

        action = "Escalate"

        reason = (
            "High-value transaction requires controlled escalation"
        )

    # --------------------------------------------------------
    # 11. RETURN DECISION
    # --------------------------------------------------------

    return {
        "transaction_id": transaction["transaction_id"],
        "recovery_probability": round(
            recovery_probability, 3
        ),
        "expected_recovery": round(
            expected_recovery, 2
        ),
        "priority": priority,
        "action": action,
        "reason": reason,
        "retry_delay_minutes": delay
    }


# ============================================================
# TEST AGENT
# ============================================================

if __name__ == "__main__":

    print("=" * 75)
    print("REVIVEAI RECOVERY DECISION AGENT")
    print("=" * 75)

    # Load transaction dataset
    df = pd.read_csv("data/transactions.csv")

    # Select first 10 transactions for testing
    test_transactions = df.head(10)

    print("\nAgent decisions:\n")

    for _, row in test_transactions.iterrows():

        transaction = row.to_dict()

        decision = decide_recovery_action(transaction)

        print("-" * 75)

        print(
            f"Transaction       : "
            f"{decision['transaction_id']}"
        )

        print(
            f"Amount            : "
            f"₹{transaction['amount']:,.2f}"
        )

        print(
            f"Failure           : "
            f"{transaction['failure_reason']}"
        )

        print(
            f"Recovery Prob.    : "
            f"{decision['recovery_probability'] * 100:.1f}%"
        )

        print(
            f"Expected Recovery : "
            f"₹{decision['expected_recovery']:,.2f}"
        )

        print(
            f"Priority          : "
            f"{decision['priority']}"
        )

        print(
            f"Recommended Action: "
            f"{decision['action']}"
        )

        print(
            f"Reason            : "
            f"{decision['reason']}"
        )

        print(
            f"Retry Delay       : "
            f"{decision['retry_delay_minutes']} minutes"
        )

    print("\n" + "=" * 75)
    print("AGENT TEST COMPLETE")
    print("=" * 75)