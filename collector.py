from web3 import Web3
import time
import csv

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not web3.is_connected():
    print("Error: Not connected to blockchain")
    exit()

# Treat Ganache accounts as nodes
nodes = web3.eth.accounts

# CSV file to store data
csv_file = "node_activity.csv"

# Write header if file is empty
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "node", "tx_count", "gas_used", "block_number"])

print("Collecting data... Press CTRL + C to stop.")

try:
    while True:
        for node in nodes:
            tx_count = web3.eth.get_transaction_count(node)

            latest_block = web3.eth.get_block("latest")
            gas_used = latest_block.gasUsed

            with open(csv_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    time.time(),
                    node,
                    tx_count,
                    gas_used,
                    latest_block.number
                ])

        time.sleep(2)  # collect every 2 seconds

except KeyboardInterrupt:
    print("\nData collection stopped.")
