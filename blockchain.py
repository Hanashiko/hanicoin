import hashlib
import json
import time
from transaction import Transaction

class Block:
    def __init__(self, index, timestamp, transaction, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        transaction_data = [tx.to_dict() if isinstance(tx, Transaction) else tx for tx in self.transaction]
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": transaction_data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def __str__(self):
        tx_output = []
        for tx in self.transaction:
            if isinstance(tx, Transaction):
                tx_output.append(str(tx))
            else:
                tx_output.append(json.dumps(tx, indent=2))
        
        return (
            f"--- Block  {self.index} ---\n"
            f"Hash: {self.hash}\n"
            f"Prev: {self.previous_hash}\n"
            f"Nonce: {self.nonce}\n"
            f"Transactions:\n" + "\n".join(f"  {tx}" for tx in tx_output)
        )

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
        if not isinstance(transaction, Transaction):
            raise TypeError("The Transaction object was waiting")
        if not transaction.is_valid():
            raise ValueError("Invalid signature of transaction format")
        
        if transaction.sender != "SYSTEM":
            sender_balance = self.get_balance(transaction.sender)
            if transaction.amount > sender_balance:
                raise ValueError("Insufficient funds")
        
        self.pending_transactions.append(transaction)
        
    def mine_pending_transactions(self, miner_address):
        reward_tx = Transaction(
            sender="SYSTEM",
            recipient=miner_address,
            amount=self.mining_reward,
            signature=None
        )
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
    
    def print_chain(self):
        for block in self.chain:
            print(f"--- Block {block.index} ---")
            print(f"Hash: {block.hash}")
            print(f"Prev: {block.previous_hash}")
            print("Transaction:")
            for tx in block.transaction:
                if isinstance(tx, Transaction):
                    print(f"  {tx}")
                else:
                    print(f"  {tx}")
            print()

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transaction:
                if isinstance(tx, dict):
                    sender = tx.get("sender")
                    recipient = tx.get("recipient")
                    amount = tx.get("amount")
                else:
                    sender = tx.sender
                    recipient = tx.recipient
                    amount = tx.amount
                    
                if sender == address:
                    balance -= amount
                if recipient == address:
                    balance += amount
        return balance
