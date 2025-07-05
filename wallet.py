import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization

def generate_keypair():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def save_keys_to_files(private_key, public_key, name="wallet"):
    with open(f"{name}_private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    with open(f"{name}_public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
        
def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)
    
def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())
    
def get_address_from_public_key(public_key):
    raw_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return base64.b64encode(raw_bytes).decode()

priv, pub = generate_keypair()
save_keys_to_files(priv, pub, name="mywallet")
address = get_address_from_public_key(pub)
print(f"your address: {address}")

priv2 = load_private_key("mywallet_private.pem")
pub2 = load_public_key("mywallet_public.pem")
addr2 = get_address_from_public_key(pub2)

print(f"address from file: {addr2}")