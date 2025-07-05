import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.exceptions import InvalidSignature

class Transtion:
    def __init__(self, sender, recipient, amount, signature=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        
    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }
        
    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True)
    
    def sign(self, private_key: Ed25519PrivateKey):
        message = self.to_json().encode()
        signature = private_key.sign(message)
        self.signature = base64.b64encode(signature).decode()
        
    def is_valid(self):
        if self.sender == "SYSTEM":
             return True
        if not self.signature:
            return False
        
        try:
            public_key = Ed25519PublicKey.from_public_bytes(
                base64.b64decode(self.sender)
            )
            public_key.verify(
                base64.b64decode(self.signature),
                self.to_json().encode()
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
        
    def __repr__(self):
        return f"<Tx {self.sender[:6]} -> {self.recipient[:6]}: {self.amount}>"

from cryptography.hazmat.primitives import serialization
privkey = Ed25519PrivateKey.generate()
pubkey = privkey.public_key()
pubkey_b64 = base64.b64encode(
    pubkey.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
).decode()

tx = Transtion(sender=pubkey_b64, recipient="SomeOtherPublicKey==", amount=25)
tx.sign(privkey)

print(f"transaction: {tx.to_dict()}")
print(f"sign: {tx.signature}")
print(f"is valid? {tx.is_valid()}")