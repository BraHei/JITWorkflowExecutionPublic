import json
import boto3
from botocore.exceptions import ClientError

def get_aws_secret(secret_name: str, region_name: str = "eu-central-1") -> dict:
    """
    Retrieve a secret from AWS Secrets Manager.

    Args:
        secret_name (str): Name of the secret in AWS Secrets Manager.
        region_name (str): AWS region where the secret is stored.

    Returns:
        dict: Parsed secret as a dictionary.
    """
    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])  # Parse JSON secret
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        print(f"Error retrieving secret: {e}")
        raise
