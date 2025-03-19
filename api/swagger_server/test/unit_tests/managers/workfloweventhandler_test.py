import pytest
from unittest.mock import MagicMock, patch
from swagger_server.managers.workfloweventhandler import WorkflowEventHandler
from swagger_server.managers.argofileextractor import parse_argo_workflow


@pytest.fixture
def mock_cache_manager():
    """Creates a fully mocked CacheManager instance."""
    mock = MagicMock()
    mock.rclone_manager.get_endpoint_name.side_effect = lambda x: x  # Returns the endpoint name as is
    mock.set_primary_endpoint.return_value = None
    mock.set_secondary_endpoint.return_value = None
    mock.set_primary_folder.return_value = None
    mock.set_secondary_folder.return_value = None
    mock.set_files.return_value = None
    mock.start.return_value = None
    return mock


@pytest.fixture
def workflow_event_handler(mock_cache_manager):
    """Provides a WorkflowEventHandler instance with a mocked CacheManager."""
    return WorkflowEventHandler(cache_manager=mock_cache_manager)


@patch("swagger_server.managers.workfloweventhandler.parse_argo_workflow")
def test_handle_workflow_event_success(mock_parse_argo_workflow, workflow_event_handler, mock_cache_manager):
    """Tests handling a valid workflow event and updating CacheManager correctly."""

    # Mock parsed workflow data
    mock_parse_argo_workflow.return_value = {
        "primary_endpoint": "s3://primary-bucket",
        "secondary_endpoint": "s3://secondary-bucket",
        "primary_folder": "primary-folder",
        "secondary_folder": "secondary-folder",
        "files": ["file1.txt", "file2.csv"],
    }

    workflow_json = {"workflow": "mocked-data"}
    workflow_event_handler.handle_workflow_event(workflow_json)

    # Ensure parse_argo_workflow is called correctly
    mock_parse_argo_workflow.assert_called_once_with(workflow_json)

    # Ensure CacheManager setters are called with correct values
    mock_cache_manager.set_primary_endpoint.assert_called_once_with("s3://primary-bucket:")
    mock_cache_manager.set_secondary_endpoint.assert_called_once_with("s3://secondary-bucket:")
    mock_cache_manager.set_primary_folder.assert_called_once_with("primary-folder")
    mock_cache_manager.set_secondary_folder.assert_called_once_with("secondary-folder")
    mock_cache_manager.set_files.assert_called_once_with(["file1.txt", "file2.csv"])

    # Ensure cache synchronization starts
    mock_cache_manager.start.assert_called_once()


@patch("swagger_server.managers.workfloweventhandler.parse_argo_workflow")
def test_handle_workflow_event_missing_fields(mock_parse_argo_workflow, workflow_event_handler, mock_cache_manager):
    """Tests handling a workflow event where some expected fields are missing."""

    # Mock parsed workflow with missing fields
    mock_parse_argo_workflow.return_value = {
        "primary_endpoint": None,
        "secondary_endpoint": None,
        "primary_folder": None,
        "secondary_folder": None,
        "files": [],
    }

    workflow_json = {"workflow": "mocked-data"}
    workflow_event_handler.handle_workflow_event(workflow_json)

    # Ensure parse_argo_workflow is called
    mock_parse_argo_workflow.assert_called_once_with(workflow_json)

    # Ensure CacheManager setters are still called but with `None` or empty values
    mock_cache_manager.set_primary_endpoint.assert_called_once_with("None:")
    mock_cache_manager.set_secondary_endpoint.assert_called_once_with("None:")
    mock_cache_manager.set_primary_folder.assert_called_once_with(None)
    mock_cache_manager.set_secondary_folder.assert_called_once_with(None)
    mock_cache_manager.set_files.assert_called_once_with([])

    # Ensure cache synchronization starts
    mock_cache_manager.start.assert_called_once()


@patch("swagger_server.managers.workfloweventhandler.parse_argo_workflow")
def test_handle_workflow_event_no_files(mock_parse_argo_workflow, workflow_event_handler, mock_cache_manager):
    """Tests handling a workflow event with no files listed."""

    mock_parse_argo_workflow.return_value = {
        "primary_endpoint": "s3://primary-bucket",
        "secondary_endpoint": "s3://secondary-bucket",
        "primary_folder": "primary-folder",
        "secondary_folder": "secondary-folder",
        "files": [],
    }

    workflow_json = {"workflow": "mocked-data"}
    workflow_event_handler.handle_workflow_event(workflow_json)

    mock_parse_argo_workflow.assert_called_once_with(workflow_json)
    mock_cache_manager.set_files.assert_called_once_with([])

    # Ensure cache synchronization still starts
    mock_cache_manager.start.assert_called_once()


@patch("swagger_server.managers.workfloweventhandler.parse_argo_workflow")
def test_handle_workflow_event_invalid_json(mock_parse_argo_workflow, workflow_event_handler, mock_cache_manager):
    """Tests handling a workflow event with an invalid JSON format (bad parse)."""

    mock_parse_argo_workflow.return_value = {"error": "Invalid JSON"}

    workflow_json = {"bad": "data"}
    workflow_event_handler.handle_workflow_event(workflow_json)

    # Ensure parse_argo_workflow is called
    mock_parse_argo_workflow.assert_called_once_with(workflow_json)

    # Ensure CacheManager was still called with "None:"
    mock_cache_manager.set_primary_endpoint.assert_called_once_with("None:")
    mock_cache_manager.set_secondary_endpoint.assert_called_once_with("None:")
    mock_cache_manager.set_primary_folder.assert_called_once_with(None)
    mock_cache_manager.set_secondary_folder.assert_called_once_with(None)
    mock_cache_manager.set_files.assert_called_once_with([])

    # Ensure cache synchronization does not start
    mock_cache_manager.start.assert_called_once()
