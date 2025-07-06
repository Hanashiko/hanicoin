import argparse
from wallet import generate_keypair, save_keys_to_files, load_private_key, load_public_key, get_address_from_public_key
from transaction import Transaction
from blockchain import Blockchain
import os
import base64
import requests

WALLET_PREFIX = "wallet"
NODE_URL = "http://localhost:5000"

def create_wallet():
    priv, pub = generate_keypair()
    save_keys_to_files(priv, pub, name=WALLET_PREFIX)
    addr = get_address_from_public_key(pub)
    print("✅ Wallet created")
    print(f"🔑 Address: {addr}")
    
def show_address():
    pub = load_public_key(f"{WALLET_PREFIX}_public.pem")
    print(f"🔑 Your address: {get_address_from_public_key(pub)}")
    
def send_transaction(to, amount):
    priv = load_private_key(f"{WALLET_PREFIX}_private.pem")
    pub = load_public_key(f"{WALLET_PREFIX}_public.pem")
    addr = get_address_from_public_key(pub)
    
    tx = Transaction(
        sender=addr,
        recipient=to,
        amount=float(amount)
    )
    tx.sign(priv)
    
    import requests
    response = requests.post("http://localhost:5000/transaction/new", json={
        "sender": tx.sender,
        "recipient": tx.recipient,
        "amount": tx.amount,
        "signature": tx.signature
    })
    
    if response.status_code == 201:
        print("✅ Transaction sent")
    else:
        print(f"❌ Error: {response.text}")

def mine_block():
    pub = load_public_key(f"{WALLET_PREFIX}_public.pem")
    addr = get_address_from_public_key(pub)
    
    response = requests.post(f"{NODE_URL}/mine", json={"miner_address": addr})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Mined block #{data['index']} with {data['transactions']} transactions")
        print(f"🔗 Hash: {data['hash']}")
    else:
        print(f"❌ Mining error: {response.text}")
    
    from blockchain import Blockchain
    bc = Blockchain()
    bc.mine_pending_transactions(addr)
    bc.print_chain()

def check_balance():
    from blockchain import Blockchain
    pub  = load_public_key(f"{WALLET_PREFIX}_public.pem")
    addr = get_address_from_public_key(pub)
    
    response = requests.get(f"{NODE_URL}/balance", params={"address": addr})
    
    if response.status_code == 200:
        data = response.json()
        print(f"💰 Balance: {data['balance']} coins")
    else:
        print(f"❌ Error when checking balance: {response.text}")
        
def show_latest_block():
    response = requests.get(f"{NODE_URL}/latest")
    if response.status_code == 200:
        block = response.json()
        print(f"🧱 Block #{block['index']}")
        print(f"🔗 Hash: {block['hash']}")
        print(f"📦 Transactions: {len(block['transactions'])}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HaniCoin CLI")
    
    subparsers = parser.add_subparsers(dest='command')
    
    subparsers.add_parser("create-wallet", help="Create new wallet")
    subparsers.add_parser("show-address", help="Show yourself address")
    
    send_parser = subparsers.add_parser("send", help="Send transaction")
    send_parser.add_argument("--to", required=True, help="Recipient address")
    send_parser.add_argument("--amount", required=True, help="Amount")
    
    subparsers.add_parser("mine", help="Mine a new block")
    
    subparsers.add_parser("balance", help="Check balance")
    
    subparsers.add_parser("chain", help="Show latest block")
    
    args = parser.parse_args()
    
    if args.command == "create-wallet":
        create_wallet()
    elif args.command == "show-address":
        show_address()
    elif args.command == "send":
        send_transaction(args.to, args.amount)
    elif args.command == "mine":
        mine_block()
    elif args.command == "balance":
        check_balance()
    elif args.command == "chain":
        show_latest_block()
    else:
        parser.print_help()