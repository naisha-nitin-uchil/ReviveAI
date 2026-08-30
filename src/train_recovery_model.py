import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)

import joblib


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATA_PATH = "data/transactions.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("REVIVEAI - RECOVERY PREDICTION MODEL")
print("=" * 70)

print(f"\nDataset loaded successfully: {df.shape}")


# ============================================================
# 2. DEFINE FEATURES AND TARGET
# ============================================================

target = "recovery_success"

# These columns are available BEFORE recovery.
features = [
    "amount",
    "payment_method",
    "transaction_hour",
    "transaction_day",
    "failure_reason",
    "failure_category",
    "previous_transaction_count",
    "previous_success_count",
    "previous_failure_count",
    "customer_success_rate",
    "days_since_last_success",
    "retry_count"
]

X = df[features]
y = df[target]


# ============================================================
# 3. CHECK TARGET DISTRIBUTION
# ============================================================

print("\nTarget distribution:")
print(y.value_counts())

print("\nTarget percentage:")
print((y.value_counts(normalize=True) * 100).round(2))


# ============================================================
# 4. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 5. IDENTIFY FEATURE TYPES
# ============================================================

categorical_features = [
    "payment_method",
    "transaction_day",
    "failure_reason",
    "failure_category"
]

numerical_features = [
    "amount",
    "transaction_hour",
    "previous_transaction_count",
    "previous_success_count",
    "previous_failure_count",
    "customer_success_rate",
    "days_since_last_success",
    "retry_count"
]


# ============================================================
# 6. PREPROCESSING
# ============================================================

numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numerical_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)


# ============================================================
# 7. DEFINE MODELS
# ============================================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.08,
        max_depth=3,
        random_state=42
    )
}


# ============================================================
# 8. TRAIN AND EVALUATE MODELS
# ============================================================

results = []

trained_pipelines = {}

for model_name, model in models.items():

    print("\n" + "-" * 70)
    print(f"Training: {model_name}")
    print("-" * 70)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC-AUC": roc_auc
    })

    trained_pipelines[model_name] = pipeline

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")


# ============================================================
# 9. COMPARE MODELS
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="ROC-AUC",
    ascending=False
)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 10. SELECT BEST MODEL
# ============================================================

best_model_name = results_df.iloc[0]["Model"]

best_pipeline = trained_pipelines[best_model_name]

print("\n" + "=" * 70)
print(f"BEST MODEL: {best_model_name}")
print("=" * 70)


# ============================================================
# 11. DETAILED EVALUATION
# ============================================================

best_predictions = best_pipeline.predict(X_test)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        best_predictions,
        target_names=[
            "Not Recovered",
            "Recovered"
        ],
        zero_division=0
    )
)


# ============================================================
# 12. SAVE BEST MODEL
# ============================================================

os.makedirs("models", exist_ok=True)

model_path = "models/recovery_prediction_model.pkl"

joblib.dump(
    best_pipeline,
    model_path
)

print("\nBest model saved successfully:")
print(model_path)


# ============================================================
# 13. SAVE MODEL COMPARISON
# ============================================================

results_path = "models/model_comparison.csv"

results_df.to_csv(
    results_path,
    index=False
)

print("\nModel comparison saved:")
print(results_path)

print("\n" + "=" * 70)
print("REVIVEAI MODEL TRAINING COMPLETE")
print("=" * 70)