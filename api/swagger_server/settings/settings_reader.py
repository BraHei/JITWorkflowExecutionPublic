from cryptography.fernet import Fernet
import json
import os

class SettingsReader:
    def __init__(self, encrypted_file_path='replication_settings.json.enc', key = None):
        self.encrypted_file_path = encrypted_file_path
        self.settings = {}
        self.load(key)

    def load(self, key = None):
        if not os.path.exists(self.encrypted_file_path):
            raise FileNotFoundError(f"File not found: {self.encrypted_file_path}")

        if key is None:
            raise ValueError("Key must be provided")

        try:
            fernet = Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid Fernet key: {e}")

        with open(self.encrypted_file_path, 'rb') as enc_file:
            encrypted_data = enc_file.read()

        try:
            decrypted_data = fernet.decrypt(encrypted_data)
        except Exception as e:
            raise ValueError(f"Decryption failed. Wrong key? {e}")

        try:
            decrypted_data_str = decrypted_data.decode()
        except UnicodeDecodeError:
            raise ValueError("Couldn't decode decrypted data. Wrong key or file corrupt?")

        try:
            self.settings = json.loads(decrypted_data_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parsing failed: {e}")

    def get(self, section, key=None, default=None):
        section_data = self.settings.get(section, {})
        if key is None:
            return section_data
        return section_data.get(key, default)

    def __getitem__(self, section):
        return self.settings[section]

if __name__ == "__main__":
    settings = SettingsReader()

    print("\n Settings loaded successfully!")
    print("UvA endpoint:", settings.get('UvA', 'endpoint'))

