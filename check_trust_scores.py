import os
import json
from web3 import Web3

# ----------------------------
# Config
# ----------------------------
RPC_URL = os.getenv("GANACHE_RPC", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x206a41F32ecC5be2dF274f77887b52e4caf50dc1")
ABI_PATH = os.getenv("ABI_PATH", "TrustScore_abi.json")

# ----------------------------
# Connect to Ganache
# ----------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise SystemExit("Cannot connect to Ganache at " + RPC_URL)

with open(ABI_PATH, "r") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
accounts = w3.eth.accounts

# ----------------------------
# Read trust scores
# ----------------------------
print("\n--- Trust Scores of All Nodes ---\n")
for node in accounts:
    score = contract.functions.trustScores(Web3.to_checksum_address(node)).call()
    print(f"Node {node}: Trust Score = {score}")
