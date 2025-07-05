import argparse
from wallet import generate_keypair, save_keys_to_files, load_private_key, load_public_key, get_address_from_public_key
from transaction import Transaction
from blockchain import Blockchain
import os
import base64

WALLET_PREFIX = "wallet"

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
        amount=amount
    )
    tx.sign()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HaniCoin CLI")
    
    subparsers = parser.add_subparsers(dest='command')
    
    subparsers.add_parser("create-wallet", help="Create new wallet")
    subparsers.add_parser("show-address", help="Show yourself address")
    
    args = parser.parse_args()
    
    if args.command == "create-wallet":
        create_wallet()
    elif args.command == "show-address":
        show_address()