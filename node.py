from flask import Flask, request, jsonify
from blockchain import Blockchain, Block
from transaction import Transaction
import json
import requests

app = Flask(__name__)
blockchain = Blockchain()
peers = set()

def is_chain_valid(chain_data):
    for i in range(1, len(chain_data)):
        prev = chain_data[i - 1]
        curr = chain_data[i]
        if curr["previous_hash"] != prev["hash"]:
            return False
    return True

def convert_chain(chain_data):
    chain = []
    for block_data in chain_data:
        txs = [Transaction(**tx) for tx in block_data["transactions"]]
        block = Block(
            index=block_data["index"],
            timestamp=block_data["timestamp"],
            transaction=txs,
            previous_hash=block_data["previous_hash"],
            nonce=block_data["nonce"]
        )
        block.hash = block_data["hash"]
        chain.append(block)
    return chain

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
    
    try:
        blockchain.add_transaction(tx)
    except Exception as e:
        return f'Error: {str(e)}', 400
    
    for peer in peers:
        try:
            requests.post(f"{peer}/transaction/new",json=data)
        except:
            continue
    
    return 'Transaction added', 201

@app.route('/block/receive', methods=['POST'])
def receive_block():
    data = request.get_json()
    transactions = [Transaction(**tx) for tx in data['transactions']]
    new_block = blockchain.create_genesis_block()
    new_block.index = data['index']
    new_block.timestamp = data['timestamp']
    new_block.transaction = transactions
    new_block.previous_hash = data['previous_hash']
    new_block.nonce = data['nonce']
    new_block.hash = data['hash']
    
    if new_block.previous_hash == blockchain.get_latest_block().hash:
        blockchain.chain.append(new_block)
        blockchain.pending_transactions = []
        return 'Block accepted', 201
    else:
        return 'Block rejected', 400
    
@app.route('/peer/add', methods=['POST'])
def add_peer():
    data = request.get_json()
    peer = data.get("peer")
    if peer:
        peers.add(peer)
        return 'Peer added', 201
    return 'No peer', 400

@app.route('/peers', methods=["GET"])
def get_peers():
    return jsonify(list(peers)), 200

@app.route("/sync", methods=["POST"])
def sync_chain():
    imported = 0
    longest_chain = None
    max_length = len(blockchain.chain)
    
    for peer in peers:
        try:
            response = requests.get(f"{peer}/chain")
            if response.status_code == 200:
                remote_chain = response.json()
                if len(remote_chain) > max_length and is_chain_valid(remote_chain):
                    max_length = len(remote_chain)
                    longest_chain = remote_chain
        except Exception as e:
            print(f"Error syncing with {peer}: {e}")
            continue
        
    if longest_chain:
        blockchain.chain = convert_chain(longest_chain)
        blockchain.save_chain_to_file()
        return f"Chain syncronized. New length: {max_length}", 200
    
    return f"No longer valid chain found",200

@app.route("/balance", methods=["GET"])
def get_balance():
    address = request.args.get("address")
    if not address:
        return "Address is not specified", 400
    balance = blockchain.get_balance(address)
    return jsonify({"address": address, "balance": balance}), 200

if __name__ == "__main__":
    import sys
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)