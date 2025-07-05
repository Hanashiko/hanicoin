from wallet import generate_keypair, get_address_from_public_key
from transaction import Transaction
from blockchain import Blockchain

priv_alice, pub_alice = generate_keypair()
addr_alice = get_address_from_public_key(pub_alice)

priv_bob, pub_bob = generate_keypair()
addr_bob = get_address_from_public_key(pub_bob)

bc = Blockchain()

tx1 = Transaction(sender=addr_alice, recipient=addr_bob, amount=5)
tx1.sign(priv_alice)

bc.mine_pending_transactions(miner_address=addr_bob)

bc.print_chain()