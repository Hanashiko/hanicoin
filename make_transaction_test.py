import requests
from wallet import generate_keypair, get_address_from_public_key
from transaction import Transaction

priv, pub = generate_keypair()
sender = get_address_from_public_key(pub)
recipient = "mdYpZrODaFE82vbKcmj2wAw+d/doye4vH/RMxdaN7dY="

tx = Transaction(sender, recipient, 5)
tx.sign(priv)

if not tx.is_valid():
    print("Error: Transaction is not valid!")
    exit(1)
    
tx_data = tx.to_dict()
print(f"Sending transaction: {tx_data}")

try:
    response = requests.post(
        "http://localhost:5000/transaction/new",
        json=tx_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Server response {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error while sending: {e}")