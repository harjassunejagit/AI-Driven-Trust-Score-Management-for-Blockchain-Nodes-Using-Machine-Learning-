from web3 import Web3
import time

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

sender = web3.eth.accounts[0]
receiver = web3.eth.accounts[1]

while True:
    tx_hash = web3.eth.send_transaction({
        "from": sender,
        "to": receiver,
        "value": web3.to_wei(0.0001, "ether")
    })

    print("Normal tx:", tx_hash.hex())
    time.sleep(3)  # slow, normal traffic
