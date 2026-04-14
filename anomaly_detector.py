import pandas as pd
from sklearn.ensemble import IsolationForest

# Load CSV data
df = pd.read_csv("node_activity.csv")

print("Data loaded:")
print(df.head())

# Features for anomaly detection
features = ["tx_count", "gas_used", "block_number"]

X = df[features]

# Create Isolation Forest model
model = IsolationForest(
    contamination=0.15,  # % of data expected to be anomalies
    random_state=42
)

# Train model
model.fit(X)

# Predict anomalies (-1 = anomaly, 1 = normal)
df["anomaly"] = model.predict(X)

# Show results
print("\nAnomaly detection results:")
print(df[["node", "tx_count", "gas_used", "block_number", "anomaly"]])

# Save output
df.to_csv("node_activity_with_anomalies.csv", index=False)
print("\nSaved results to node_activity_with_anomalies.csv")
