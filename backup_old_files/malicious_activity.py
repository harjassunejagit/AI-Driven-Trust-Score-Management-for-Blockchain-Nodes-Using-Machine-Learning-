from web3 import Web3
import time

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

attacker = web3.eth.accounts[3]
victim = web3.eth.accounts[4]

while True:
    tx_hash = web3.eth.send_transaction({
        "from": attacker,
        "to": victim,
        "value": web3.to_wei(0.00001, "ether")
    })

    print("MALICIOUS tx:", tx_hash.hex())
    time.sleep(0.2)  # fast spam
