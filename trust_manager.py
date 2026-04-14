import pandas as pd

input_file = "node_activity_with_anomalies.csv"
output_file = "trust_scores.csv"

df = pd.read_csv(input_file)

df["trust_score"] = df["anomaly"].apply(lambda a: 100 if a == 1 else 20)

df.to_csv(output_file, index=False)

print("Trust scores saved to trust_scores.csv")
