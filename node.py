from flask import Flask, request, jsonify
from blockchain import Blockchain
from transaction import Transaction
import json

app = Flask(__name__)
blockchain = Blockchain()
peers = set()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactiond": [tx.to_dict() if isinstance(tx, Transaction) else tx for tx in block.transaction],
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })
    return jsonify(chain_data), 200

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    required_fields = ['sender', 'recipient', 'amount', 'signature']
    if not all(k in data for k in required_fields):
        return 'Not enough data', 400
    
    tx = Transaction(
        sender=data['sender'],
        recipient=data['recipient'],
        amount=data['amount'],
        signature=data['signature']
    )
    
    if not tx.is_valid():
        return 'Invalid signature', 400
    
    blockchain.add_transaction(tx)
    return 'Transaction added', 201

if __name__ == "__main__":
    import sys
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)