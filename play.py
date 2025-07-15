from web3 import Web3
from solcx import compile_source
import os

w3 = Web3(Web3.HTTPProvider("https://your-somnia-testnet-rpc"))
private_key = "0xYourPrivateKey"
acct = w3.eth.account.from_key(private_key)

contract_source_code = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FrontrunTarget {
    event Action(address sender, uint256 amount);

    function emitAction(uint256 amount) public {
        emit Action(msg.sender, amount);
    }
}
'''

compiled_sol = compile_source(contract_source_code)
contract_id, contract_interface = compiled_sol.popitem()

FrontrunTarget = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
nonce = w3.eth.get_transaction_count(acct.address)

tx = FrontrunTarget.constructor().build_transaction({
    'from': acct.address,
    'nonce': nonce,
    'gas': 3000000,
    'gasPrice': w3.to_wei('2', 'gwei'),
    'chainId': w3.eth.chain_id
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("📡 Deploying contract...")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("✅ Contract deployed at:", tx_receipt.contractAddress)
