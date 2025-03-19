import json
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from swagger_server.managers.awssecretsmanager import get_aws_secret


@pytest.fixture
def mock_boto3_client():
    """Creates a mock Boto3 Secrets Manager client."""
    with patch("boto3.session.Session.client") as mock_client:
        yield mock_client


def test_get_aws_secret_success(mock_boto3_client):
    """Tests retrieving a secret successfully."""
    mock_secret = {"username": "test_user", "password": "test_password"}
    mock_response = {"SecretString": json.dumps(mock_secret)}

    mock_client_instance = MagicMock()
    mock_client_instance.get_secret_value.return_value = mock_response
    mock_boto3_client.return_value = mock_client_instance

    secret = get_aws_secret("test_secret")

    mock_boto3_client.assert_called_once_with(service_name="secretsmanager", region_name="eu-central-1")
    mock_client_instance.get_secret_value.assert_called_once_with(SecretId="test_secret")

    assert secret == mock_secret


def test_get_aws_secret_invalid_json(mock_boto3_client):
    """Tests handling of an invalid JSON response."""
    mock_response = {"SecretString": "invalid_json_string"}

    mock_client_instance = MagicMock()
    mock_client_instance.get_secret_value.return_value = mock_response
    mock_boto3_client.return_value = mock_client_instance

    with pytest.raises(json.JSONDecodeError):
        get_aws_secret("test_secret")


def test_get_aws_secret_client_error(mock_boto3_client):
    """Tests handling of a ClientError from AWS."""
    mock_client_instance = MagicMock()
    error_response = {
        "Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}
    }
    mock_client_instance.get_secret_value.side_effect = ClientError(error_response, "GetSecretValue")
    mock_boto3_client.return_value = mock_client_instance

    with pytest.raises(ClientError):
        get_aws_secret("test_secret")

    mock_boto3_client.assert_called_once_with(service_name="secretsmanager", region_name="eu-central-1")
    mock_client_instance.get_secret_value.assert_called_once_with(SecretId="test_secret")


def test_get_aws_secret_no_secret_string(mock_boto3_client):
    """Tests handling of a missing 'SecretString' in response."""
    mock_response = {}

    mock_client_instance = MagicMock()
    mock_client_instance.get_secret_value.return_value = mock_response
    mock_boto3_client.return_value = mock_client_instance

    with pytest.raises(KeyError):
        get_aws_secret("test_secret")
