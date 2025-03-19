import pytest
import time
from unittest.mock import MagicMock, patch
from swagger_server.managers.cachemanager import CacheManager


@pytest.fixture
def mock_rclone_manager():
    """Creates a mock RcloneManager instance."""
    mock = MagicMock()

    mock.get_remote_used_storage.return_value = (True, 5000)
    mock.get_files_to_transfer.return_value = ["file1.txt", "file2.csv"]
    mock.delete_file.return_value = True

    def mock_list_files(remote, folder=""):
        if folder:
            return True, [{"file_name": folder, "size": 400}]
        return True, [
            {"file_name": "file1.txt", "size": 400},
            {"file_name": "file2.csv", "size": 500},
            {"file_name": "old_file.json", "size": 200},
        ]

    mock.list_files.side_effect = mock_list_files

    return mock


@pytest.fixture
def mock_mongo_db_manager():
    """Creates a fully mocked MongoDBManager instance."""
    mock = MagicMock()
    mock.collection = MagicMock()  # Ensure 'collection' exists

    mock.collection.find_one.return_value = {
        "_id": "LRUCache",
        "capacity_bytes": 10000,
        "current_bytes": 3000,
        "files": [{"file_name": "file1.txt", "size": 400, "last_access_time": time.time()}]
    }
    mock.collection.update_one.return_value = None
    return mock


@pytest.fixture
def cache_manager(mock_rclone_manager, mock_mongo_db_manager):
    """Provides a CacheManager instance with fully mocked dependencies."""

    with patch("swagger_server.managers.cachemanager.get_aws_secret",
               return_value={"decryption-key": "mock-secret-key"}):
        with patch("swagger_server.managers.cachemanager.MongoDBManager", return_value=mock_mongo_db_manager):
            with patch("swagger_server.managers.cachemanager.SettingsReader") as mock_settings:
                mock_settings_instance = MagicMock()
                mock_settings.return_value = mock_settings_instance
                mock_settings_instance.settings = {}

                cm = CacheManager()
                cm.rclone_manager = mock_rclone_manager
                cm.mongoDB_manager = mock_mongo_db_manager
                cm.collection = mock_mongo_db_manager.collection

                cm.set_primary_endpoint("test_primary/")
                cm.set_secondary_endpoint("test_secondary/")
                cm.set_files(["file1.txt", "file2.csv"])
                cm.set_primary_folder("test_primary_folder")
                cm.set_secondary_folder("test_secondary_folder")

                return cm


def test_cache_manager_initialization(cache_manager):
    """Tests if CacheManager initializes correctly."""
    assert cache_manager.primary_endpoint == "test_primary/"
    assert cache_manager.secondary_endpoint == "test_secondary/"
    assert isinstance(cache_manager.files, list)
    assert "file1.txt" in cache_manager.files


def test_start_process(cache_manager):
    """Tests the start process including file transfer handling."""
    cache_manager.start()

    cache_manager.rclone_manager.get_files_to_transfer.assert_called_once_with("test_primary/test_primary_folder",
                                                                               ["file1.txt", "file2.csv"])
    cache_manager.rclone_manager.list_files.assert_any_call("test_secondary/test_secondary_folder", "file1.txt")


def test_add_file(cache_manager):
    """Tests adding a file to the cache."""
    cache_manager.add_file("file3.json", 500)
    cache_manager.mongoDB_manager.collection.update_one.assert_called()


def test_get_file(cache_manager):
    """Tests retrieving a file from the cache."""
    result = cache_manager.get_file("file1.txt")
    assert result is not None
    assert result[0] == "file1.txt"


def test_evict_file(cache_manager):
    """Tests evicting a file from the cache."""
    cache_manager.evict_file("file1.txt")
    cache_manager.mongoDB_manager.collection.update_one.assert_called()


def test_remove_old_files(cache_manager):
    """Tests removing files present in primary storage but not in the cache."""
    cache_manager.start()
    cache_manager.rclone_manager.delete_file.assert_called_with("test_primary/", "old_file.json")


def test_set_capacity_bytes(cache_manager):
    """Tests updating the cache capacity."""
    cache_manager.set_capacity_bytes(8000)

    cache_manager.mongoDB_manager.collection.update_one.assert_any_call(
        {"_id": cache_manager.document_id},
        {"$set": {"capacity_bytes": 8000}}
    )


def test_set_capacity_bytes_negative(cache_manager):
    """Tests that setting a negative cache capacity raises an error."""
    with pytest.raises(ValueError, match="Capacity cannot be negative"):
        cache_manager.set_capacity_bytes(-500)


def test_set_current_bytes(cache_manager):
    """Tests updating the current cache usage."""
    cache_manager.set_current_bytes(3000)

    cache_manager.mongoDB_manager.collection.update_one.assert_any_call(
        {"_id": cache_manager.document_id},
        {"$set": {"current_bytes": 3000}}
    )


def test_set_current_bytes_exceeding_capacity(cache_manager):
    """Tests that setting current bytes above capacity raises an error."""
    with pytest.raises(ValueError, match="Current bytes .* cannot exceed capacity .*"):
        cache_manager.set_current_bytes(12000)


def test_set_current_bytes_negative(cache_manager):
    """Tests that setting a negative current byte value raises an error."""
    with pytest.raises(ValueError, match="Current bytes cannot be negative"):
        cache_manager.set_current_bytes(-100)


def test_set_current_bytes_no_cache_doc(cache_manager):
    """Tests error handling when the cache document is missing in MongoDB."""
    cache_manager.mongoDB_manager.collection.find_one.return_value = None

    with pytest.raises(RuntimeError, match="Cache document not found in MongoDB"):
        cache_manager.set_current_bytes(1000)


def test_evict_nonexistent_file(cache_manager):
    """Tests that evicting a file not in cache does nothing."""
    cache_manager.evict_file("missing_file.txt")
    state = cache_manager._load_state()
    assert "missing_file.txt" not in [f["file_name"] for f in state["files"]]


def test_get_missing_file(cache_manager):
    """Tests retrieving a file that doesn't exist in cache."""
    result = cache_manager.get_file("nonexistent_file.txt")
    assert result is None
