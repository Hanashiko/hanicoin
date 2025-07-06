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
        
        reconstructed = Block(
            index=curr["index"],
            timestamp=curr["timestamp"],
            transaction=[Transaction(**tx) for tx in curr["transaction"]],
            previous_hash=curr["previous_hash"],
            nonce=curr["nonce"]
        )
        if reconstructed.hash != curr["hash"]:
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
        blockchain.save_chain_to_file()
        
        for peer in peers:
            try:
                requests.post(f"{peer}/block/receive", json=data)
            except:
                continue
        
        return 'Block accepted', 201
    else:
        return 'Block rejected', 400
    
@app.route('/peer/add', methods=['POST'])
def add_peer():
    data = request.get_json()
    peer = data.get("peer")
    
    if not peer:
        return "No peer provided", 400
    
    if not peer.startswith("http://") and not peer.startswith("https://"):
        peer = f"http://{peer}"
        
    peers.add(peer)
    return 'Peer added', 201

@app.route('/peers', methods=["GET"])
def get_peers():
    return jsonify(list(peers)), 200

@app.route("/sync", methods=["POST"])
def sync_chain():
    best_chain = blockchain.chain
    best_length = len(best_chain)

    for peer in peers:
        try:
            response = requests.get(f"{peer}/chain", timeout=5)
            print(f"[test] Response: {response}")
            if response.status_code != 200:
                continue
            
            remote_chain_data = response.json()

            print(f"[test] Peer {peer} have chain with {remote_chain_data} blocks")
            print(f"[test] Our chain have {len(blockchain.chain)} blocks")
            print(f"[test] Chain from {peer} valid: {is_chain_valid(remote_chain_data)}")
            if not is_chain_valid(remote_chain_data):
                continue
            if len(remote_chain_data) > best_length:
                best_chain = convert_chain(remote_chain_data)
                best_length = len(best_chain)
            
        except Exception as e:
            print(f"Error syncing with {peer}: {str(e)}")
            continue
        
    if best_length > len(blockchain.chain):
        blockchain.chain = best_chain
        blockchain.save_chain_to_file()
        return jsonify({
            "message": "✅ Chain updated from another node",
            "length": best_length,
            "hash": blockchain.get_latest_block().hash
        }), 200
    else:
        return jsonify({
            "message": "[i] Our chain is already up to date",
            "length": len(blockchain.chain),
            "hash": blockchain.get_latest_block().hash
        }), 200

@app.route("/balance", methods=["GET"])
def get_balance():
    address = request.args.get("address")
    if not address:
        return "Address is not specified", 400
    balance = blockchain.get_balance(address)
    return jsonify({"address": address, "balance": balance}), 200

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/latest", methods=["GET"])
def latest_block():
    latest = blockchain.get_latest_block()
    return jsonify({
        "index": latest.index,
        "timestamp": latest.timestamp,
        "transactions": [
            tx.to_dict() if isinstance(tx, Transaction) else tx
            for tx in latest.transaction
        ],
        "previous_hash": latest.previous_hash,
        "nonce": latest.nonce,
        "hash": latest.hash
    }), 200

@app.route("/pending", methods=["GET"])
def get_pending_transactions():
    pending = [
        tx.to_dict() if isinstance(tx, Transaction) else tx
        for tx in blockchain.pending_transactions
    ]
    return jsonify(pending), 200

@app.route("/peer/announce", methods=["POST"])
def peer_announce():
    data = request.get_json()
    peer = data.get("peer")
    if peer and peer != request.host_url.strip("/"):
        peers.add(peer)
        print(f"[+] New peer connected: {peer}")
        return "OK", 200
    return "Invalid peer", 400

@app.route("/mine", methods=["POST"])
def mine_block():
    data = request.get_json()
    miner_address = data.get("miner_address")
    if not miner_address:
        return "You need to specify 'miner_address'", 400
    
    blockchain.mine_pending_transactions(miner_address)
    blockchain.save_chain_to_file()
    
    latest = blockchain.get_latest_block()
    
    block_data = {
        "index": latest.index,
        "timestamp": latest.timestamp,
        "transactions": [
            tx.to_dict() if isinstance(tx, Transaction) else tx
            for tx in latest.transaction
        ],
        "previous_hash": latest.previous_hash,
        "nonce": latest.nonce,
        "hash": latest.hash
    }
    
    for peer in peers:
        try:
            requests.post(f"{peer}/block/receive", json=block_data)
        except:
            continue
        
    return jsonify({
        "message": "✅ New block mined",
        "index": latest.index,
        "hash": latest.hash,
        "transaction": len(latest.transaction)
    }), 200

if __name__ == "__main__":
    import sys
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port)