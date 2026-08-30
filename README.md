🤖 AI Decision System

ReviveAI uses a machine learning model to estimate the probability that a failed payment can be successfully recovered.

The recovery probability is then passed to the decision agent.

The agent evaluates:

Recovery probability
Failure category
Failure reason
Transaction characteristics
Retry count
Business recovery rules

Based on these signals, ReviveAI selects an appropriate recovery action.

Available Recovery Actions
Retry
Retry After Delay
Send Payment Reminder
Escalate
Suggest Alternate Payment Method
Stop Recovery

This allows the system to avoid blindly retrying every failed transaction.

🛡️ Business Guardrails

ReviveAI uses business guardrails to ensure that recovery attempts remain controlled and bounded.

The system can stop recovery when:

Maximum retry limit is reached
Recovery probability is too low
Customer recovery potential is too low

Guardrail decisions are recorded in the audit trail.

This helps prevent unnecessary retries and provides a clear explanation for why a transaction was stopped.

💰 Recovery Simulation

ReviveAI includes a recovery simulator that evaluates the outcome of the selected recovery action.

The simulator records:

Whether recovery was attempted
Whether recovery succeeded
Simulated recovered amount
Recovery outcome

The simulation allows the complete revenue recovery workflow to be demonstrated without processing real payments.

📊 Interactive Dashboard

The ReviveAI dashboard is built using Streamlit and provides an interactive control center for analyzing the recovery system.

The dashboard contains three major sections.

📈 Recovery Overview

The Recovery Overview provides a high-level view of revenue recovery performance.

It includes:

Total transactions
Actionable transactions
Expected recovery
Simulated recovery
Recovery rate
Successful recoveries
Transactions stopped by guardrails
Total transaction value
AI recovery potential
Recovery by action
Expected recovery by priority
Recovery opportunity by failure category
Recovery funnel
Revenue protection

The dashboard also provides filters for priority, failure category, and recovery action.

🤖 Agent Intelligence

The Agent Intelligence section provides insight into how the recovery decision system behaves.

It includes:

Agent action distribution
Guardrail distribution
Recovery action performance
Top recovery opportunities
Guardrail analysis

This helps users understand how ReviveAI converts recovery predictions into business actions.

🔍 Transaction Explorer

The Transaction Explorer provides transaction-level AI explainability.

Users can search for a transaction using its Transaction ID.

For each transaction, the dashboard displays:

Transaction amount
Recovery probability
Expected recovery
Priority
Failure reason
Failure category
Payment method
Retry count
Recovery attempt status
AI recommended action
Decision reason
Retry delay
Guardrail
Recovery outcome

The dashboard also provides an explanation of why ReviveAI selected a particular recovery decision.

📈 Project Results

ReviveAI was tested using a synthetic dataset containing 10,000 failed payment transactions.

Overall Results
Metric	Result
Transactions Analyzed	10,000
Actionable Transactions	5,811
Successful Recoveries	3,397
Recovery Rate	58.46%
Expected Recoverable Revenue	₹83.24 L
Simulated Recovered Revenue	₹63.87 L
Total Transaction Value	₹185.57 L
⚡ Recovery Action Distribution
Recovery Action	Transactions
Stop Recovery	4,189
Retry After Delay	2,515
Send Payment Reminder	1,837
Retry	1,131
Escalate	321
Suggest Alternate Payment Method	7
🛡️ Guardrail Results
Guardrail	Transactions Stopped
Maximum Retry Limit	1,991
Low Recovery Probability	1,292
Low Customer Recovery Potential	906

These guardrails demonstrate that ReviveAI does not attempt recovery without considering operational limits and recovery potential.

🧠 Machine Learning

ReviveAI uses a machine learning model for recovery-probability prediction.

The model analyzes transaction-level characteristics and produces a recovery probability between 0 and 1.

The trained model is stored at:

models/recovery_prediction_model.pkl

Model comparison information is stored at:

models/model_comparison.csv

The predicted recovery probability is used by the decision agent to select the next recovery action.

🔄 End-to-End Workflow
Failed Payment
      ↓
Transaction Analysis
      ↓
Recovery Probability Prediction
      ↓
AI Decision Agent
      ↓
Business Guardrail Check
      ↓
Recovery Action
      ↓
Recovery Simulation
      ↓
Audit Logging
      ↓
Dashboard Analytics

This creates a complete closed-loop revenue recovery workflow.

🗂️ Project Structure
ReviveAI/
│
├── README.md
├── .gitignore
│
├── dashboards/
│   └── app.py
│
├── data/
│   ├── transactions.csv
│   ├── agent_decisions.csv
│   ├── recovery_results.csv
│   ├── audit_log.csv
│   └── generate_dataset.py
│
├── models/
│   ├── recovery_prediction_model.pkl
│   └── model_comparison.csv
│
├── src/
│   ├── recovery_agent.py
│   ├── recovery_simulator.py
│   ├── batch_recovery_engine.py
│   ├── audit_logger.py
│   ├── train_recovery_model.py
│   └── test_agent_batch.py
│
├── tests/
│   └── capture_dashboard.py
│
└── docs/
    ├── dashboard_overview.png
    ├── agent_intelligence.png
    └── transaction_explorer.png
🖥️ Dashboard Screenshots
Recovery Overview

Agent Intelligence

Transaction Explorer

⚙️ Technology Stack
Python — Core development
Pandas — Data processing
NumPy — Numerical processing
Scikit-learn — Machine learning
Streamlit — Interactive dashboard
SQLite — Transaction and audit storage
Git — Version control
GitHub — Repository and project hosting
🚀 Running the Project

Clone the repository:

git clone https://github.com/naisha-nitin-uchil/ReviveAI.git
cd ReviveAI

Install the required Python packages:

pip install streamlit pandas numpy scikit-learn

Run the dashboard:

streamlit run dashboards/app.py

The ReviveAI dashboard will open in your browser.

🔎 Example Transaction Analysis

A failed transaction enters ReviveAI.

The system analyzes the transaction and predicts its recovery probability.

The decision agent evaluates the prediction together with the failure category, retry history, and configured business rules.

The guardrail layer determines whether recovery should continue.

If recovery is allowed, the agent selects an appropriate action such as:

Retry
Retry After Delay
Send Payment Reminder
Escalate
Suggest Alternate Payment Method

If recovery should not continue:

Stop Recovery

The recovery simulator then records the simulated outcome.

Finally, the decision and outcome are stored in the audit trail and displayed through the dashboard.

🔐 Safety and Control

ReviveAI is designed around controlled and explainable recovery.

The system uses:

Retry limits
Recovery probability thresholds
Customer recovery-potential checks
Explicit stop decisions
Audit logging
Simulated recovery execution

These controls help demonstrate how AI can be used for revenue recovery while keeping automated actions bounded.

📌 Project Status

ReviveAI currently includes:

Transaction analysis
ML recovery-probability prediction
AI recovery decision agent
Recovery simulation
Business guardrails
Audit logging
Batch recovery processing
Interactive Streamlit dashboard
Dashboard filtering
Transaction-level AI explainability
Recovery analytics
Dashboard screenshots
GitHub repository
⚠️ Disclaimer

ReviveAI is a prototype built using synthetic transaction data.

Recovery outcomes are simulated and do not represent real payment recovery performance.

No real payment transactions are processed by this prototype.

👩‍💻 Project

ReviveAI

Track 3 — AI Revenue Recovery

Built as an AI-powered revenue recovery prototype for the Razorpay AI Builder Internship 2026.