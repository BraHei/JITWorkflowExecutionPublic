from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(input_file, output_file, key):
    fernet = Fernet(key)

    with open(input_file, 'rb') as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    with open(output_file, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

    print(f"\n '{input_file}' encrypted and saved as '{output_file}'.")

if __name__ == "__main__":
    choice = input("Generate a new key? (y/n): ").strip().lower()

    if choice == 'y':
        key = generate_key()
        print(f"\n Generated Fernet key:\n{key.decode()}")
        print("Save this key securely! You'll need it to decrypt.")
    elif choice == 'n':
        key_input = input("Paste your Fernet key: ").strip()
        key = key_input.encode()
    else:
        print("Invalid choice.")
        exit(1)

    encrypt_file('replication_settings.json', 'replication_settings.json.enc', key)

