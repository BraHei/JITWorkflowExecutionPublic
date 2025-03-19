import yaml
import json

def parse_argo_workflow(data):
    """
    Parses an Argo workflow from a JSON or YAML string/dictionary.
    
    :param data: JSON/YAML string or dictionary.
    :return: Extracted workflow details including unique ID, endpoints, files, event type, and status.
    """
    try:
        # Convert string input to dictionary if necessary
        if isinstance(data, str):
            try:
                data = json.loads(data)  # Try JSON parsing
            except json.JSONDecodeError:
                data = yaml.safe_load(data)  # Fallback to YAML parsing
        
        # Extract event type (ADD, UPDATE, DELETE, etc.)
        event_type = data.get("type", "UNKNOWN")
        
        # Extract workflow data if embedded
        workflow_data = data.get("body", data)
        
        # Extract unique identifier
        unique_id = workflow_data.get('metadata', {}).get('uid', None)
        
        # Extract files
        files = []
        try:
            for param in workflow_data['spec']['arguments']['parameters']:
                if param['name'] == 'files':
                    files = json.loads(param['value'])
                    break
        except (KeyError, TypeError, json.JSONDecodeError):
            files = []
        
        # Extract endpoints
        primary_endpoint = None
        secondary_endpoint = None
        
        try:
            for template in workflow_data['spec']['templates']:
                if template['name'] == 'download-file-with-fallback':
                    for step_group in template['steps']:
                        for step in step_group:
                            if step['name'] == 'try-primary-endpoint':
                                primary_endpoint = step['arguments']['parameters'][1]['value']
                            elif step['name'] == 'fallback-to-secondary':
                                secondary_endpoint = step['arguments']['parameters'][1]['value']
        except (KeyError, IndexError, TypeError):
            primary_endpoint = None
            secondary_endpoint = None
        
        # Extract status for both ADD and UPDATE events
        status = workflow_data.get("status", {}).get("phase", "UNKNOWN")
        
        return {
            'unique_id': unique_id,
            'event_type': event_type,  # Indicates ADD, UPDATE, or DELETE
            'primary_endpoint': primary_endpoint,
            'secondary_endpoint': secondary_endpoint,
            'endpoint_type': 'UNKNOWN',  # Assuming UNKNOWN unless specified
            'files': files,
            'status': status  # Include status for both ADD and UPDATE events
        }
    
    except Exception as e:
        return {"error": str(e)}

# Example usage for server endpoint
if __name__ == "__main__":
    file_path = "workflow_argo_push.json"  # Replace with your actual file path
    
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        result = parse_argo_workflow(file_content)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(json.dumps({"error": "File not found"}, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))

