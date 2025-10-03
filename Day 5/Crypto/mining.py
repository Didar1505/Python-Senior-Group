import hashlib
import time
import base64
import json
from flask import Flask, request
import ecdsa

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # Number of leading zeros for PoW

    def create_genesis_block(self):
        return Block(0, time.time(), {"data": "Genesis Block"}, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.mine_block(new_block)
        self.chain.append(new_block)

    def mine_block(self, block):
        target = "0" * self.difficulty
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_balance(self, public_key):
        balance = 0
        # Normalize public key: remove spaces and special characters
        normalized_public_key = public_key.replace(" ", "").replace("+", "").replace("/", "").replace("=", "")
        print(f"Calculating balance for public_key: {public_key} (normalized: {normalized_public_key})")
        for block in self.chain[1:]:  # Skip genesis block
            print(f"Processing block {block.index}: {block.data}")
            if isinstance(block.data, dict):  # Ensure block.data is a dictionary
                # Normalize keys in block data
                block_from = block.data.get("from", "").replace(" ", "").replace("+", "").replace("/", "").replace("=", "")
                block_to = block.data.get("to", "").replace(" ", "").replace("+", "").replace("/", "").replace("=", "")
                amount = int(block.data.get("amount", 0))
                if block_from == normalized_public_key:
                    balance -= amount  # Subtract amount for sender
                    print(f"Debit: -{amount}, New balance: {balance}")
                if block_to == normalized_public_key:
                    balance += amount  # Add amount for recipient
                    print(f"Credit: +{amount}, New balance: {balance}")
            else:
                print(f"Skipping invalid block data: {block.data}")
        print(f"Final balance: {balance}")
        return balance

def validate_signature(public_key, signature, message):
    try:
        # Decode base64 public key
        public_key_bytes = base64.b64decode(public_key)
        public_key_hex = public_key_bytes.hex()
        signature = base64.b64decode(signature)
        verify_key = ecdsa.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1)
        is_valid = verify_key.verify(signature, message.encode())
        print(f"Signature validation {'successful' if is_valid else 'failed'} for public_key: {public_key}")
        return is_valid
    except Exception as e:
        print(f"Signature validation failed: {str(e)}")
        return False

# Flask setup
node = Flask(__name__)
blockchain = Blockchain()

@node.route('/txion', methods=['POST'])
def new_transaction():
    data = request.get_json()
    print(f"Received transaction: {data}")
    required_fields = ["from", "to", "amount", "signature", "message"]
    if not all(field in data for field in required_fields):
        print("Missing fields in transaction data")
        return "Missing fields", 400
    
    if validate_signature(data["from"], data["signature"], data["message"]):
        block_data = {
            "from": data["from"],
            "to": data["to"],
            "amount": data["amount"]
        }
        print(f"Signature valid. Adding block with data: {block_data}")
        new_block = Block(len(blockchain.chain), time.time(), block_data, blockchain.get_latest_block().hash)
        blockchain.add_block(new_block)
        print(f"Block added. Current chain length: {len(blockchain.chain)}")
        return "Transaction added", 201
    else:
        print("Invalid signature detected")
        return "Invalid signature", 401

@node.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        })
    return json.dumps({"chain": chain_data, "length": len(chain_data)})

@node.route('/balance', methods=['GET'])
def get_balance():
    public_key = request.args.get('public_key')
    if not public_key:
        print("Missing public_key parameter")
        return "Missing public_key parameter", 400
    print(f"Balance query for: {public_key}")
    balance = blockchain.get_balance(public_key)
    print(f"Returning balance: {balance}")
    return json.dumps({"public_key": public_key, "balance": balance})

if __name__ == '__main__':
    node.run(host='0.0.0.0', port=5000)