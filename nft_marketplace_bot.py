import json
import time
from web3 import Web3
from requests import get

# Replace with your Infura or other Ethereum node provider URL
INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
# Replace with the wallet's private key for signing transactions
PRIVATE_KEY = "your_private_key_here"
# Replace with the NFT marketplace API URL
MARKETPLACE_API_URL = "https://api.opensea.io/api/v1/assets"

# The contract address for the specific NFT collection (ERC-721)
NFT_CONTRACT_ADDRESS = "0xYourNFTContractAddressHere"
# Example of token ID to check
TOKEN_ID = 1234

# Connect to the Ethereum network
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Wallet address derived from private key
account = web3.eth.account.privateKeyToAccount(PRIVATE_KEY)
wallet_address = account.address

# Sample ABI for ERC-721
ERC721_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "ownerOf",
        "outputs": [
            {"name": "", "type": "address"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "tokenURI",
        "outputs": [
            {"name": "", "type": "string"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

def get_token_metadata(token_id):
    """Fetch metadata for a specific NFT from the marketplace API"""
    params = {
        "order_direction": "desc",
        "offset": "0",
        "limit": "1",
        "order_by": "price",
        "order_direction": "asc",
        "order_by": "price",
        "token_ids": token_id,
        "asset_contract_address": NFT_CONTRACT_ADDRESS
    }
    
    response = get(MARKETPLACE_API_URL, params=params)
    data = response.json()
    
    if data['assets']:
        asset = data['assets'][0]
        token_uri = asset['token_uri']
        return token_uri
    else:
        print("❌ No NFT found with the given token ID.")
        return None

def buy_nft(token_id, price):
    """Function to automate purchasing an NFT"""
    # Check if we have enough funds to buy
    balance = web3.eth.get_balance(wallet_address)
    
    if balance >= price:
        print(f"✅ Buying NFT with Token ID {token_id} for {price} ETH")
        
        # Prepare the transaction
        nonce = web3.eth.get_transaction_count(wallet_address)
        transaction = {
            'to': NFT_CONTRACT_ADDRESS,
            'value': price,
            'gas': 200000,
            'gasPrice': web3.toWei('20', 'gwei'),
            'nonce': nonce
        }
        
        # Sign and send the transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        
        print(f"Transaction sent, TX Hash: {web3.toHex(tx_hash)}")
        return web3.toHex(tx_hash)
    else:
        print(f"❌ Insufficient funds to purchase the NFT with Token ID {token_id}")
        return None

def main():
    print("=== NFT Marketplace Bot ===")
    
    while True:
        token_metadata = get_token_metadata(TOKEN_ID)
        
        if token_metadata:
            print(f"Metadata for Token ID {TOKEN_ID}: {token_metadata}")
            
            # Example condition to buy an NFT if the price is below a threshold
            price_threshold = web3.toWei(0.1, 'ether')  # 0.1 ETH
            price = web3.toWei(0.05, 'ether')  # Example price to trigger purchase
            
            if price <= price_threshold:
                tx_hash = buy_nft(TOKEN_ID, price)
                if tx_hash:
                    print(f"✅ NFT purchased! Transaction hash: {tx_hash}")
                    
        time.sleep(60)  # Wait for 1 minute before checking again

if __name__ == "__main__":
    main()
