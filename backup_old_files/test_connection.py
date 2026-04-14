from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

print("Connected:", web3.is_connected())

print("Latest Block:", web3.eth.block_number)
