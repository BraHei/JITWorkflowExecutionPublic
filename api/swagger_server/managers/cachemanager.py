import time

from .rclonemanager import RcloneManager
from .mongodbmanager import MongoDBManager
from .awssecretsmanager import get_aws_secret
from swagger_server.settings.settings_reader import SettingsReader

from collections import OrderedDict
from pymongo import MongoClient
from typing import Optional, Callable


class CacheManager:
    def __init__(self, eviction_callback: Optional[Callable[[str, int], None]] = None,
                 settings_file='replication_settings.json.enc'):
        """
        Initialize the CacheManager with required primary and secondary storage names.

        Args:
            primary (str): The primary storage location.
            secondary (str): The secondary storage location.
            eviction_callback (Optional[Callable[[str, int], None]]): Callback for evictions.
        """
        self.document_id = "LRUCache"
        self.eviction_callback = eviction_callback
        self.primary_endpoint = None
        self.primary_folder = None
        self.secondary_endpoint = None
        self.secondary_folder = None
        self.files = None
        self.initialized = False

        # Retrieve the decryption key.
        self.decryption_key = get_aws_secret("decryption_secret")["decryption-key"]

        self.settings_reader = SettingsReader(settings_file, self.decryption_key)
        self.rclone_manager = RcloneManager()
        self.mongoDB_manager = MongoDBManager()

        self.configure_remotes_from_settings()

        # Ensure the cache document exists, if not present, create a default one
        cache_doc = self.mongoDB_manager.collection.find_one({"_id": self.document_id})
        if not cache_doc:
            self.mongoDB_manager.collection.insert_one({
                "_id": self.document_id,
                "capacity_bytes": 1000,
                "current_bytes": 0,
                "files": []
            })

        # For now, assume a static cache size of 
        self.capacity = 1000000000  # 1 GB
        self.set_capacity_bytes(self.capacity)

    def configure_remotes_from_settings(self):
        """
        Reads settings and configures Rclone remotes dynamically.
        """
        # Loop through each remote in settings
        for remote_name, config in self.settings_reader.settings.items():
            # Mandatory fields
            remote_type = config.get('type')
            access_key = config.get('access_key_id')
            secret_key = config.get('secret_access_key')
            endpoint = config.get('endpoint')

            # Optional "remote" parameter
            remote_path = config.get('remote', '')

            # Collect any additional options (exclude known keys)
            known_keys = {
                'type', 'provider', 'access_key_id', 'secret_access_key', 'endpoint', 'remote'
            }

            additional_options = {
                key: value for key, value in config.items() if key not in known_keys
            }

            print(f"Configuring remote '{remote_name}' of type '{remote_type}'...")

            # Configure the remote via RcloneManager
            result = self.rclone_manager.configure_remote(
                name=remote_name,
                remote_type=remote_type,
                access_key=access_key,
                secret_key=secret_key,
                endpoint=endpoint,
                remote=remote_path,
                additional_options=additional_options
            )

            print(f"Remote '{remote_name}' configured!")

    def set_primary_endpoint(self, primary):
        """Updates the primary storage endpoint."""
        self.primary_endpoint = primary

    def set_secondary_endpoint(self, secondary):
        """Updates the secondary storage endpoint."""
        self.secondary_endpoint = secondary

    def set_primary_folder(self, primary):
        """Updates the primary storage folder."""
        self.primary_folder = primary

    def set_secondary_folder(self, secondary):
        """Updates the secondary storage folder."""
        self.secondary_folder = secondary

    def set_files(self, files):
        """Updates the list of files to be handled."""
        self.files = files

    def sync_cache(self):
        """Synchronize the cache with the remote storage."""
        _, remote_files = self.rclone_manager.list_files(self.primary_endpoint + self.primary_folder)

        print(f"Remote files: {remote_files}")

        remote_file_set = {file_info["file_name"] for file_info in remote_files}

        # Compare remote files with current cache and add any missing files
        for file_info in remote_files:
            name = file_info["file_name"]
            file_size = file_info["size"]

            # Check if file already exists in cache, add it otherwise
            if self.get_file(f"/{name}") is None:
                self.add_file(f"/{name}", file_size)

        # Compare current cache with remote files and remove files that are no longer on the remote
        cache_files = self.get_cached_file_names()
        print(f"cached files: {cache_files}")

        for cached_file in cache_files:
            # Remove leading slash to match remote file naming
            clean_cached_file = cached_file.lstrip("/")

            if clean_cached_file not in remote_file_set:
                print(f"Evicting file no longer on remote: {cached_file}")
                self.evict_file(cached_file)

        _, used_storage = self.rclone_manager.get_remote_used_storage(self.primary_endpoint, self.primary_folder)
        self.set_current_bytes(used_storage)

        print("Cache synchronization complete.")

    def start(self):
        """
        Initiates the cache synchronization process:
        1. Requests missing files.
        2. Updates the cache with available files.
        3. Removes extra files in primary storage that are not in cache.
        4. Syncs cache with primary storage.
        """

        # Step 1: Request missing files
        files_to_transfer = self.rclone_manager.get_files_to_transfer(self.primary_endpoint + self.primary_folder, self.files)

        print(f"files to transfer {files_to_transfer}")        

        for file in files_to_transfer:
            file_size_success, file_size = self.rclone_manager.list_files(self.secondary_endpoint+self.secondary_folder, file)

            if not file_size_success:
                print(f"[ERROR] Could not retrieve size for file: {file}. The error was {file_size}. Skipping...")
                continue

            # Check if file already exists in cache, add it otherwise
            if self.get_file(file) is not None:
                print(f"get file {file}")
                continue
            else:
                print(f"add file {file}")
                self.add_file(file, file_size[0]["size"])

        # Step 2: Remove files present in primary storage but not in the cache
        success, remote_files = self.rclone_manager.list_files(self.primary_endpoint + self.primary_folder)

        state = self._load_state()
        cache_files = self._list_to_ordereddict(state["files"])

        if success:
            print(f"remove these files: {remote_files}")
            for file in remote_files:
                name = file["file_name"]
                if name not in cache_files.keys():
                    print(f"[INFO] Removing {name} from primary storage (not in cache).")
                    self.rclone_manager.delete_file(self.primary_endpoint, name)
        else:
            print("[INFO] Could not list remote files. Skipping cleanup step.")

            
        # Step 3: Sync cache with primary storage
        print("[INFO] Syncing cache with primary storage...")
        self.rclone_manager.copy_files(
            source=self.secondary_endpoint+self.secondary_folder,
            destination=self.primary_endpoint+self.primary_folder,
            files=list(cache_files.keys())
        )

        print("[INFO] Cache synchronization complete.")

    def add_file(self, file_name: str, file_size: int) -> None:
        """Add a file to the cache, evicting as needed."""
        state = self._load_state()
        if file_size > state["capacity_bytes"]:
            print("File to large for cache")
            return None

        files_dict = self._list_to_ordereddict(state["files"])

        # If file already exists, remove it first
        if file_name in files_dict:
            old_size, _ = files_dict[file_name]
            state["current_bytes"] -= old_size
            del files_dict[file_name]

        files_dict[file_name] = (file_size, time.time())
        state["current_bytes"] += file_size

        # Evict old files if needed
        while state["current_bytes"] > state["capacity_bytes"] and files_dict:
            oldest_file, (old_size, _) = files_dict.popitem(last=False)
            state["current_bytes"] -= old_size
            if self.eviction_callback:
                self.eviction_callback(oldest_file, old_size)

        self._save_state(state["capacity_bytes"], state["current_bytes"], self._ordereddict_to_list(files_dict))

    def get_file(self, file_name: str):
        """Access a file, updating its LRU status."""
        state = self._load_state()
        files_dict = self._list_to_ordereddict(state["files"])

        if file_name not in files_dict:
            return None

        file_size, _ = files_dict[file_name]
        files_dict[file_name] = (file_size, time.time())

        self._save_state(state["capacity_bytes"], state["current_bytes"], self._ordereddict_to_list(files_dict))
        return file_name, file_size

    def evict_file(self, file_name: str) -> None:
        """Manually evict a file."""
        state = self._load_state()
        files_dict = self._list_to_ordereddict(state["files"])

        if file_name in files_dict:
            file_size, _ = files_dict[file_name]
            del files_dict[file_name]
            state["current_bytes"] -= file_size
            if self.eviction_callback:
                self.eviction_callback(file_name, file_size)

        self._save_state(state["capacity_bytes"], state["current_bytes"], self._ordereddict_to_list(files_dict))

    def list_files(self):
        """List files in LRU order."""
        state = self._load_state()
        return state["files"]

    def set_capacity_bytes(self, capacity: int):
        """
        Updates the maximum cache capacity (in bytes).

        Args:
            capacity (int): New maximum cache capacity in bytes.
        """
        if capacity < 0:
            raise ValueError("Capacity cannot be negative")

        self.mongoDB_manager.collection.update_one(
            {"_id": self.document_id},
            {"$set": {"capacity_bytes": capacity}}
        )

        print(f"[INFO] Cache capacity updated to {capacity} bytes")

    def set_current_bytes(self, current: int):
        """
        Updates the current cache usage (in bytes).

        Args:
            current (int): New current cache usage in bytes.
        """
        if current < 0:
            raise ValueError("Current bytes cannot be negative")
       
        cache_doc = self.mongoDB_manager.collection.find_one({"_id": self.document_id})
        if not cache_doc:
            raise RuntimeError("Cache document not found in MongoDB")

        capacity = cache_doc.get("capacity_bytes", 1000)
        if current > capacity:
            raise ValueError(f"Current bytes ({current}) cannot exceed capacity ({capacity})")
        
        self.mongoDB_manager.collection.update_one(
            {"_id": self.document_id},
            {"$set": {"current_bytes": current}}
        )

        print(f"[INFO] Current cache usage updated to {current} bytes")

    def _load_state(self):
        """Load the cache state from MongoDB."""
        return self.mongoDB_manager.collection.find_one({"_id": self.document_id})

    def _save_state(self, capacity_bytes, current_bytes, files_list):
        """Save the cache state back to MongoDB."""
        self.mongoDB_manager.collection.update_one({"_id": self.document_id}, {
            "$set": {"capacity_bytes": capacity_bytes, "current_bytes": current_bytes, "files": files_list}
        })

    def _list_to_ordereddict(self, files_list):
        """Convert list to OrderedDict sorted by access time (oldest first)."""
        sorted_files = sorted(files_list, key=lambda x: x["last_access_time"])
        return OrderedDict((f["file_name"], (f["size"], f["last_access_time"])) for f in sorted_files)

    def _ordereddict_to_list(self, od):
        """Convert OrderedDict to list format."""
        return [{"file_name": k, "size": v[0], "last_access_time": v[1]} for k, v in od.items()]
    
    def get_cached_file_names(self):
        """Retrieve a list of cached file names in LRU order."""
        state = self._load_state()

        if not state or "files" not in state:
            return []  # Return an empty list if cache is empty or doesn't exist

        return [file["file_name"] for file in state["files"]]
