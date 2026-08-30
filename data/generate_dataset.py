import numpy as np
import pandas as pd

# Reproducibility
np.random.seed(42)

# Number of transactions
N = 10000

# --------------------------------------------------
# 1. BASIC TRANSACTION INFORMATION
# --------------------------------------------------

transaction_id = [f"TXN{100000 + i}" for i in range(N)]
customer_id = [f"CUST{np.random.randint(1000, 3000)}" for _ in range(N)]
merchant_id = [f"MERCH{np.random.randint(100, 150)}" for _ in range(N)]

amount = np.round(
    np.random.lognormal(mean=7.2, sigma=0.8, size=N),
    2
)

amount = np.clip(amount, 100, 100000)

currency = np.array(["INR"] * N)

payment_method = np.random.choice(
    ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"],
    size=N,
    p=[0.45, 0.20, 0.15, 0.12, 0.08]
)

transaction_hour = np.random.randint(0, 24, N)

transaction_day = np.random.choice(
    ["Monday", "Tuesday", "Wednesday", "Thursday",
     "Friday", "Saturday", "Sunday"],
    size=N
)

# --------------------------------------------------
# 2. FAILURE INFORMATION
# --------------------------------------------------

failure_reason = np.random.choice(
    [
        "Network Timeout",
        "Bank Server Unavailable",
        "Gateway Timeout",
        "Insufficient Balance",
        "Payment Declined",
        "Incorrect Payment Details",
        "Authentication Failure",
        "Processing Error"
    ],
    size=N,
    p=[
        0.16,
        0.10,
        0.10,
        0.18,
        0.16,
        0.08,
        0.08,
        0.14
    ]
)

temporary_failures = [
    "Network Timeout",
    "Bank Server Unavailable",
    "Gateway Timeout"
]

customer_failures = [
    "Insufficient Balance",
    "Payment Declined",
    "Incorrect Payment Details"
]

technical_failures = [
    "Authentication Failure",
    "Processing Error"
]

def categorize_failure(reason):
    if reason in temporary_failures:
        return "Temporary"
    elif reason in customer_failures:
        return "Customer Related"
    else:
        return "Technical"

failure_category = [
    categorize_failure(reason)
    for reason in failure_reason
]

retry_count = np.random.choice(
    [0, 1, 2, 3],
    size=N,
    p=[0.55, 0.25, 0.15, 0.05]
)

# --------------------------------------------------
# 3. CUSTOMER HISTORY
# --------------------------------------------------

previous_transaction_count = np.random.randint(1, 51, N)

previous_success_count = np.array([
    np.random.randint(
        max(1, int(count * 0.5)),
        count + 1
    )
    for count in previous_transaction_count
])

previous_failure_count = (
    previous_transaction_count - previous_success_count
)

customer_success_rate = np.round(
    previous_success_count /
    previous_transaction_count,
    3
)

days_since_last_success = np.random.randint(1, 91, N)

# --------------------------------------------------
# 4. BASE RECOVERY PROBABILITY
# --------------------------------------------------

recovery_probability = np.full(N, 0.50)

# Temporary failures are generally easier to recover
for i in range(N):

    if failure_category[i] == "Temporary":
        recovery_probability[i] += 0.20

    elif failure_category[i] == "Customer Related":
        recovery_probability[i] -= 0.10

    elif failure_category[i] == "Technical":
        recovery_probability[i] -= 0.05

    # Strong customer history
    if customer_success_rate[i] >= 0.80:
        recovery_probability[i] += 0.15
    elif customer_success_rate[i] < 0.60:
        recovery_probability[i] -= 0.15

    # Too many retries reduce recovery chance
    recovery_probability[i] -= retry_count[i] * 0.07

    # Long gap since successful payment
    if days_since_last_success[i] > 60:
        recovery_probability[i] -= 0.05

    # High-value transactions slightly harder to recover
    if amount[i] > 50000:
        recovery_probability[i] -= 0.05

# Keep probabilities realistic
recovery_probability = np.clip(
    recovery_probability,
    0.05,
    0.95
)

recovery_probability = np.round(
    recovery_probability,
    3
)

# --------------------------------------------------
# 5. RECOVERY ACTION
# --------------------------------------------------

recovery_action = []

for i in range(N):

    probability = recovery_probability[i]
    category = failure_category[i]

    if probability < 0.30:
        action = "Stop Recovery"

    elif category == "Temporary":
        if probability >= 0.70:
            action = "Retry After Delay"
        else:
            action = "Retry"

    elif category == "Customer Related":
        if probability >= 0.70:
            action = "Suggest Alternate Payment Method"
        else:
            action = "Send Payment Reminder"

    else:
        if probability >= 0.65:
            action = "Retry"
        else:
            action = "Escalate"

    recovery_action.append(action)

# --------------------------------------------------
# 6. RETRY DELAY
# --------------------------------------------------

retry_delay_minutes = []

for action in recovery_action:

    if action == "Retry":
        delay = 0

    elif action == "Retry After Delay":
        delay = np.random.choice([5, 10, 15, 30])

    elif action == "Suggest Alternate Payment Method":
        delay = np.random.choice([5, 10, 15])

    elif action == "Send Payment Reminder":
        delay = np.random.choice([30, 60, 120])

    else:
        delay = 0

    retry_delay_minutes.append(delay)

# --------------------------------------------------
# 7. SIMULATE RECOVERY OUTCOME
# --------------------------------------------------

recovery_attempted = [
    action != "Stop Recovery"
    for action in recovery_action
]

recovery_success = []

for i in range(N):

    if not recovery_attempted[i]:
        recovery_success.append(0)

    else:
        success = np.random.random() < recovery_probability[i]
        recovery_success.append(int(success))

# --------------------------------------------------
# 8. RECOVERED AMOUNT
# --------------------------------------------------

recovered_amount = []

for i in range(N):

    if recovery_success[i] == 1:

        # Slight variation in recovered amount
        recovery = amount[i] * np.random.uniform(0.95, 1.00)

        recovered_amount.append(round(recovery, 2))

    else:
        recovered_amount.append(0.0)

# --------------------------------------------------
# 9. RECOVERY TIME
# --------------------------------------------------

recovery_time_minutes = []

for i in range(N):

    if recovery_success[i] == 1:

        base_time = retry_delay_minutes[i]

        recovery_time = base_time + np.random.randint(1, 16)

        recovery_time_minutes.append(recovery_time)

    else:
        recovery_time_minutes.append(0)

# --------------------------------------------------
# 10. REVENUE AT RISK
# --------------------------------------------------

revenue_at_risk = np.round(
    amount * recovery_probability,
    2
)

# --------------------------------------------------
# 11. CREATE DATAFRAME
# --------------------------------------------------

df = pd.DataFrame({

    "transaction_id": transaction_id,
    "customer_id": customer_id,
    "merchant_id": merchant_id,

    "amount": amount,
    "currency": currency,
    "payment_method": payment_method,

    "transaction_hour": transaction_hour,
    "transaction_day": transaction_day,

    "failure_reason": failure_reason,
    "failure_category": failure_category,

    "previous_transaction_count": previous_transaction_count,
    "previous_success_count": previous_success_count,
    "previous_failure_count": previous_failure_count,
    "customer_success_rate": customer_success_rate,
    "days_since_last_success": days_since_last_success,

    "retry_count": retry_count,

    "recovery_attempted": recovery_attempted,
    "recovery_action": recovery_action,
    "retry_delay_minutes": retry_delay_minutes,

    "recovery_success": recovery_success,
    "recovered_amount": recovered_amount,
    "recovery_time_minutes": recovery_time_minutes,

    "recovery_probability": recovery_probability,
    "revenue_at_risk": revenue_at_risk
})

# --------------------------------------------------
# 12. SAVE DATASET
# --------------------------------------------------

output_path = "transactions.csv"

df.to_csv(output_path, index=False)

print("=" * 60)
print("ReviveAI Dataset Generated Successfully!")
print("=" * 60)

print(f"\nTotal transactions: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\nDataset shape:")
print(df.shape)

print("\nRecovery success rate:")
print(f"{df['recovery_success'].mean() * 100:.2f}%")

print("\nTotal revenue:")
print(f"₹{df['amount'].sum():,.2f}")

print("\nTotal revenue at risk:")
print(f"₹{df['revenue_at_risk'].sum():,.2f}")

print("\nTotal revenue recovered:")
print(f"₹{df['recovered_amount'].sum():,.2f}")

print("\nFailure categories:")
print(df["failure_category"].value_counts())

print("\nRecovery actions:")
print(df["recovery_action"].value_counts())

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset saved as:")
print(output_path)