import hashlib
import json
import time

class Block:
    def __init__(self, index, timestamp, transaction, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transaction,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

block = Block(index=1, timestamp=2, transaction="fdsfds", previous_hash="fdsfsdf")
print(block.calculate_hash())