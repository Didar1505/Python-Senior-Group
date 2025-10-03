import ecdsa
import base64
import requests
import json

def generate_ecdsa_keys():
    sign_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    private_key = sign_key.to_string().hex()
    verif_key = sign_key.get_verifying_key()
    public_key = verif_key.to_string().hex()
    public_key_b64 = base64.b64encode(bytes.fromhex(public_key)).decode()
    filename = input("Write the name of your new address: ") + ".txt"
    with open(filename, "w") as f:
        f.write(f"Private key: {private_key}\n")
        f.write(f"Wallet address | Public key: {public_key_b64}")
    print(f"Your new address and private key are now in the file {filename}")
    return private_key, public_key_b64

def sign_ecdsa_msg(private_key):
    try:
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        message = "Transaction Message"  # Simplified message for signing
        signature = sk.sign(message.encode())
        return base64.b64encode(signature).decode(), message
    except Exception as e:
        print(f"Signing failed: {str(e)}")
        return None, None

def send_transaction(addr_from, private_key, addr_to, amount):
    if len(private_key) == 64:
        signature, message = sign_ecdsa_msg(private_key)
        if not signature or not message:
            print("Failed to sign transaction")
            return
        url = 'http://localhost:5000/txion'
        try:
            amount = int(amount)  # Ensure amount is an integer
            payload = {
                "from": addr_from,
                "to": addr_to,
                "amount": amount,
                "signature": signature,
                "message": message
            }
            headers = {
                "Content-Type": "application/json"
            }
            print(f"Sending transaction: {payload}")
            res = requests.post(url, json=payload, headers=headers)
            print(f"Transaction response: {res.text} (Status: {res.status_code})")
            if res.status_code == 201:
                print("Transaction successfully added to blockchain")
            else:
                print(f"Transaction failed: {res.text}")
        except Exception as e:
            print(f"Failed to send transaction: {str(e)}")
    else:
        print("Wrong address or key length! Verify and try again.")

def check_balance(public_key):
    url = f'http://localhost:5000/balance?public_key={public_key}'
    print(f"Querying balance at: {url}")
    try:
        res = requests.get(url)
        print(f"Balance response: {res.text} (Status: {res.status_code})")
        if res.status_code == 200:
            data = res.json()
            print(f"Balance for {public_key}: {data['balance']}")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"Failed to fetch balance: {str(e)}")

def check_chain():
    url = 'http://localhost:5000/chain'
    try:
        res = requests.get(url)
        print(f"Chain response: {res.text} (Status: {res.status_code})")
        if res.status_code == 200:
            data = res.json()
            print(f"Blockchain length: {data['length']}")
            for block in data['chain']:
                print(f"Block {block['index']}: {block['data']}")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"Failed to fetch chain: {str(e)}")

if __name__ == '__main__':
    print("1. Generate new wallet")
    print("2. Send transaction")
    print("3. Check balance")
    print("4. Check blockchain")
    choice = input("Choose an option (1, 2, 3, or 4): ")
    if choice == "1":
        generate_ecdsa_keys()
    elif choice == "2":
        addr_from = input("Enter your public key (wallet address): ")
        private_key = input("Enter your private key: ")
        addr_to = input("Enter recipient's public key (wallet address): ")
        amount = input("Enter amount to send: ")
        send_transaction(addr_from, private_key, addr_to, amount)
    elif choice == "3":
        public_key = input("Enter your public key (wallet address): ")
        check_balance(public_key)
    elif choice == "4":
        check_chain()
    else:
        print("Invalid choice")