import os
import time
import csv
from datetime import datetime, timezone
from web3 import Web3
import json
import pandas as pd
import joblib

# ----------------------------
# Config
# ----------------------------
RPC_URL = os.getenv("GANACHE_RPC", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x206a41F32ecC5be2dF274f77887b52e4caf50dc1")
ABI_PATH = os.getenv("ABI_PATH", "TrustScore_abi.json")
LOG_CSV = "trust_log.csv"
LOOP_INTERVAL = 10
MAX_LOOPS = 3
RETRIES = 3
RETRY_DELAY = 2

# ----------------------------
# Load ML model
# ----------------------------
model = joblib.load("fraud_model.pkl")
print("ML model loaded ✅")

# Load Kaggle dataset to get feature template
template_df = pd.read_csv("data/ethereum_fraud.csv")
template_df.columns = template_df.columns.str.strip()

# Features used during training
feature_cols = [c for c in template_df.columns if c not in
                ["Unnamed: 0", "Index", "Address",
                 "ERC20 most sent token type", "ERC20_most_rec_token_type"]]

# ----------------------------
# Connect to Ganache
# ----------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise SystemExit(f"Cannot connect to Ganache at {RPC_URL}")

with open(ABI_PATH, "r") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
accounts = w3.eth.accounts
if len(accounts) == 0:
    raise SystemExit("No accounts found from Ganache provider")
sender = accounts[0]

# ----------------------------
# Helpers
# ----------------------------
def safe_call(func, *args, retries=RETRIES, delay=RETRY_DELAY, default=None, **kwargs):
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception:
            time.sleep(delay)
    return default

def fraud_prob_to_trust_score(fraud_prob):
    score = int((1 - fraud_prob) * 100)
    return max(0, min(score, 100))

def predict_trust_for_node(node_data):
    # Convert input to DataFrame
    if not isinstance(node_data, pd.DataFrame):
        node_df = pd.DataFrame([node_data])
    else:
        node_df = node_data.copy()

    # Strip column names
    node_df.columns = node_df.columns.str.strip()

    # Drop irrelevant columns
    features_to_drop = [
        "FLAG",
        "Unnamed: 0",
        "Index",
        "Address",
        "ERC20 most sent token type",
        "ERC20_most_rec_token_type"
    ]
    node_df = node_df.drop(features_to_drop, axis=1, errors='ignore')

    # Fill missing values
    node_df = node_df.fillna(0)

    # Reorder columns to match training
    trained_columns = model.feature_names_in_
    node_df = node_df.reindex(columns=trained_columns, fill_value=0)

    # Predict fraud probability
    fraud_prob = model.predict_proba(node_df)[0][1]

    # Convert to trust score
    trust_score = fraud_prob_to_trust_score(fraud_prob)
    return trust_score

def update_on_chain(node_addr, new_score):
    def _update():
        return contract.functions.updateTrust(node_addr, new_score).transact({'from': sender})
    tx_hash = safe_call(_update, default=None)
    if tx_hash:
        receipt = safe_call(lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120), default=None)
        blk = receipt.blockNumber if receipt else None
        return tx_hash.hex(), blk
    return None, None

def read_contract_score(node_addr):
    return safe_call(lambda: contract.functions.trustScores(Web3.to_checksum_address(node_addr)).call(), default=None)

def init_csv():
    if not os.path.exists(LOG_CSV):
        with open(LOG_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "node", "old_score", "new_score",
                "tx_hash", "block_number", "note"
            ])

# ----------------------------
# Main loop
# ----------------------------
def run_loop():
    init_csv()
    for loop_count in range(MAX_LOOPS):
        for node in accounts:
            # Build node data dict (replace with real collector metrics if available)
            node_data = template_df.sample(1).to_dict(orient="records")[0]
            node_data["Address"] = node
  # dummy placeholder
            new_score = predict_trust_for_node(node_data)
            old_score = read_contract_score(node)
            tx_hash, block_number = update_on_chain(node, new_score)
            note = "" if tx_hash else "tx_failed"
            timestamp = datetime.now(timezone.utc).isoformat()

            # Log to CSV
            row = [timestamp, node, old_score, new_score, tx_hash, block_number, note]
            with open(LOG_CSV, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row)

            print(f"[{timestamp}] Node {node[:10]}... old:{old_score} new:{new_score} "
                  f"tx:{(tx_hash[:10]+'...') if tx_hash else 'N/A'} blk:{block_number}")

        print(f"Loop {loop_count+1}/{MAX_LOOPS} | sleeping {LOOP_INTERVAL}s\n")
        time.sleep(LOOP_INTERVAL)

    print("✅ Finished all loops. Script stopped.")

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    run_loop()
