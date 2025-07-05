import wallet

private, public = wallet.generate_keypair()
wallet.save_keys_to_files(private, public, name="mywallet")
address = wallet.get_address_from_public_key(public)
print(f"your address: {address}")