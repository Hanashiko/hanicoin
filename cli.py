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