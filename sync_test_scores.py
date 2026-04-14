import os
import pandas as pd
from web3 import Web3
import json
import joblib
from datetime import datetime, timezone
import time

# ----------------------------
# Config
# ----------------------------
RPC_URL = os.getenv("GANACHE_RPC", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS",
    "0x206a41F32ecC5be2dF274f77887b52e4caf50dc1"
)
ABI_PATH = os.getenv("ABI_PATH", "TrustScore_abi.json")

MODEL_PATH = "fraud_model.pkl"
LOG_CSV = "trust_log.csv"

MAX_ITERATIONS = 3
SLEEP_TIME = 2

# ----------------------------
# Load ML model
# ----------------------------
model = joblib.load(MODEL_PATH)
model_features = model.feature_names_in_
print("ML model loaded ✅")

# ----------------------------
# Connect to Ganache
# ----------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise SystemExit("❌ Cannot connect to Ganache")

print("Connected to Ganache ✅")

with open(ABI_PATH, "r") as f:
    abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)

accounts = w3.eth.accounts
sender = accounts[0]

# ----------------------------
# Load Kaggle dataset
# ----------------------------
df = pd.read_csv("data/ethereum_fraud.csv")
df.columns = df.columns.str.strip()

# ----------------------------
# Helper functions
# ----------------------------
def fraud_prob_to_trust_score(prob):
    score = int((1 - prob) * 100)
    return max(0, min(score, 100))


def predict_trust(row_dict):
    row_df = pd.DataFrame([row_dict])
    row_df.columns = row_df.columns.str.strip()

    for col in model_features:
        if col not in row_df.columns:
            row_df[col] = 0

    row_df = row_df[model_features].fillna(0)
    fraud_prob = model.predict_proba(row_df)[0][1]
    return fraud_prob, fraud_prob_to_trust_score(fraud_prob)


def read_onchain_score(addr):
    try:
        return contract.functions.trustScores(
            Web3.to_checksum_address(addr)
        ).call()
    except Exception:
        return None


def update_onchain(addr, score):
    try:
        tx = contract.functions.updateTrust(
            Web3.to_checksum_address(addr),
            score
        ).transact({"from": sender})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        return tx.hex(), receipt.blockNumber
    except Exception:
        return None, None


def init_log():
    if not os.path.exists(LOG_CSV):
        pd.DataFrame(columns=[
            "timestamp",
            "node",
            "old_score",
            "new_score",
            "fraud_probability",
            "tx_hash",
            "block_number",
            "source"
        ]).to_csv(LOG_CSV, index=False)

# ----------------------------
# Main execution
# ----------------------------
def run():
    init_log()

    for iteration in range(MAX_ITERATIONS):
        print(f"\n--- Iteration {iteration + 1}/{MAX_ITERATIONS} ---")

        for _, row in df.iterrows():
            node_addr = row["Address"]

            fraud_prob, new_score = predict_trust(row.to_dict())
            old_score = read_onchain_score(node_addr)

            tx_hash, block_number = update_onchain(node_addr, new_score)

            timestamp = datetime.now(timezone.utc).isoformat()

            log_row = pd.DataFrame([{
                "timestamp": timestamp,
                "node": node_addr,
                "old_score": old_score,
                "new_score": new_score,
                "fraud_probability": fraud_prob,
                "tx_hash": tx_hash,
                "block_number": block_number,
                "source": "KAGGLE_ETHEREUM_DATASET"
            }])

            log_row.to_csv(LOG_CSV, mode="a", header=False, index=False)

            print(
                f"[{timestamp}] "
                f"{node_addr[:10]}... "
                f"old:{old_score} new:{new_score} "
                f"prob:{fraud_prob:.3f}"
            )

        time.sleep(SLEEP_TIME)


# ----------------------------
# Entry point
# ----------------------------
if __name__ == "__main__":
    run()
