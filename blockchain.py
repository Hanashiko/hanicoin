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

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4
        self.mining_reward = 10
        
    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
