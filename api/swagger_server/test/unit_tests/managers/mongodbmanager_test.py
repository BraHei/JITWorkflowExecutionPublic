import pytest
from unittest.mock import patch, MagicMock
from swagger_server.managers.mongodbmanager import MongoDBManager


@pytest.fixture
def mock_mongo_client():
    """Creates a mock MongoDB client."""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    return mock_client, mock_db, mock_collection


@pytest.fixture
def mock_aws_secret():
    """Mocks AWS Secrets Manager response for MongoDB credentials."""
    return {
        "username": "test_user",
        "password": "test_password",
        "host": "test_host",
        "database": "test_db"
    }


@pytest.fixture
def mongo_manager(mock_aws_secret, mock_mongo_client):
    """Provides a MongoDBManager instance with mocked dependencies."""
    with patch("swagger_server.managers.mongodbmanager.get_aws_secret", return_value=mock_aws_secret):
        with patch("swagger_server.managers.mongodbmanager.MongoClient", return_value=mock_mongo_client[0]):
            return MongoDBManager(db_name="test_db", collection_name="test_collection")


def test_mongo_manager_initialization(mongo_manager):
    """Tests MongoDBManager initialization."""
    assert mongo_manager.db is not None
    assert mongo_manager.collection is not None


def test_insert_event(mongo_manager, mock_mongo_client):
    """Tests inserting an event into MongoDB."""
    mock_insert_result = MagicMock(inserted_id="12345")
    mock_mongo_client[2].insert_one.return_value = mock_insert_result

    event_data = {"unique_id": "event123", "name": "Test Event"}
    inserted_id = mongo_manager.insert_event(event_data)

    mock_mongo_client[2].insert_one.assert_called_once_with(event_data)
    assert inserted_id == "12345"


def test_insert_event_invalid_data(mongo_manager):
    """Tests that inserting invalid event data raises an error."""
    with pytest.raises(ValueError, match="Event data must be a dictionary."):
        mongo_manager.insert_event(["invalid_data"])


def test_get_event(mongo_manager, mock_mongo_client):
    """Tests retrieving an event from MongoDB."""
    var = mock_mongo_client[2].find
