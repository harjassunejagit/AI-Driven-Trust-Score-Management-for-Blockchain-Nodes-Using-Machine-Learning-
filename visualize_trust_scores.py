# validate_trust_scores.py
import pandas as pd
import matplotlib.pyplot as plt

def plot_trust_scores(trust_csv="trust_log.csv"):
    df = pd.read_csv(trust_csv)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    nodes = df["node"].unique()

    plt.figure(figsize=(14, 7))
    for node in nodes:
        node_df = df[df["node"] == node]
        plt.plot(node_df["timestamp"], node_df["new_score"], marker='o', label=node[:10] + "...")

    plt.title("Node Trust Score Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Trust Score")
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend(title="Nodes")
    plt.tight_layout()
    plt.show()
