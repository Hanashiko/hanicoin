from blockchain import Blockchain
from wallet import load_private_key, load_public_key, get_address_from_public_key
from transaction import Transaction
import time

miner_private = load_private_key("mywallet_private.pem")
miner_public = load_public_key("mywallet_public.pem")
miner_address = get_address_from_public_key(miner_public)

bc = Blockchain()

print(">>> Preparing transactions...")

recipient = "SOME_PUBLIC_KEY=="
tx = Transaction(sender=miner_address, recipient=recipient, amount=8)
tx.sign(miner_private)

bc.add_transaction(tx)

print(">>> Start mining...")

start_time = time.time()
bc.mine_pending_transactions(miner_address)
end_time = time.time()

print(f"Mining comppleted in {round(end_time - start_time, 2)} seconds")
print(f"Miner's balance: {bc.mining_reward}")
print("Result:")
bc.print_chain()