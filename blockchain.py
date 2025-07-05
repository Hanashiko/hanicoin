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
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        
    def mine_pending_transactions(self, miner_address):
        reward_tx = {
            'sender': "SYSTEM",
            'recipient': miner_address,
            'amount': self.mining_reward
        }
        self.pending_transactions.append(reward_tx)
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transaction=self.pending_transactions,
            previous_hash=self.get_latest_block().hash
        )
        
        self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.pending_transactions = []
        
    def proof_of_work(self, block):
        while not block.hash.startswith('0' * self.difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            prev = self.chain[i-1]
            curr = self.chain[i]
            
            if curr.hash != curr.calculate_hash():
                return False
            
            if curr.previous_hash != prev.hash:
                return False
        
        return True