import yaml
import json
import re


def clean_yaml_input(raw_data):
    """
    Cleans the input YAML data by removing any invalid preamble (e.g., log lines).

    :param raw_data: Raw string from the YAML file.
    :return: Cleaned YAML string.
    """
    try:
        match = re.search(r"(\{.*)", raw_data, re.DOTALL)
        if match:
            return match.group(1)
        return raw_data
    except Exception as e:
        print("ERROR: Failed to clean YAML input:", str(e))
        return raw_data


def parse_argo_workflow(data):
    """
    Parses an Argo workflow from a JSON or YAML string/dictionary.

    :param data: JSON/YAML string or dictionary.
    :return: Extracted workflow details including unique ID, endpoints, files, event type, status, and folders.
    """
    try:
        data = clean_yaml_input(data)

        if isinstance(data, str):
            try:
                data = yaml.safe_load(data)
                print("DEBUG: Successfully parsed YAML input")
            except Exception as e:
                print(f"Could not parse data '{data}':", str(e))
                return {"error": str(e)}

        event_type = data.get("type", "UNKNOWN")

        workflow_data = data.get("body", data)

        unique_id = workflow_data.get('metadata', {}).get('uid', None)

        files = []
        primary_endpoint = None
        secondary_endpoint = None
        primary_folder = None
        secondary_folder = None

        try:
            print("DEBUG: Checking for workflow parameters")
            for param in workflow_data['spec']['arguments']['parameters']:
                param_name = param['name']
                param_value = param['value']

                if param_name == 'files':
                    cleaned_files = re.sub(r'\\n', '', param_value).strip()
                    cleaned_files = cleaned_files.replace("'", '"')
                    files = json.loads(cleaned_files)

                elif param_name == 'primary_endpoint':
                    primary_endpoint = param_value

                elif param_name == 'secondary_endpoint':
                    secondary_endpoint = param_value

                elif param_name == 'primary_folder':
                    primary_folder = param_value

                elif param_name == 'secondary_folder':
                    secondary_folder = param_value

        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            print("ERROR: Failed to extract parameters:", str(e))

        if primary_endpoint and secondary_endpoint:
            endpoint_type = "DUAL"
        elif primary_endpoint:
            endpoint_type = "PRIMARY_ONLY"
        elif secondary_endpoint:
            endpoint_type = "SECONDARY_ONLY"
        else:
            endpoint_type = "UNKNOWN"

        # Fix status handling logic
        status = "UNKNOWN"
        try:
            labels = workflow_data.get("metadata", {}).get("labels", {})
            phase_from_labels = labels.get("workflows.argoproj.io/phase")

            phase_from_status = workflow_data.get("status", {}).get("phase")
            started_at = workflow_data.get("status", {}).get("startedAt")
            finished_at = workflow_data.get("status", {}).get("finishedAt")

            if phase_from_labels:
                status = phase_from_labels.upper()
            elif phase_from_status:
                status = phase_from_status.upper()
            elif started_at is None and finished_at is None:
                status = "UNKNOWN"
            elif started_at and finished_at is None:
                status = "RUNNING"
            elif finished_at and finished_at != "None":
                status = "COMPLETED"

        except (KeyError, TypeError) as e:
            print("ERROR: Failed to determine status:", str(e))

        return {
            'unique_id': unique_id,
            'event_type': event_type,
            'primary_endpoint': primary_endpoint,
            'secondary_endpoint': secondary_endpoint,
            'primary_folder': primary_folder,
            'secondary_folder': secondary_folder,
            'endpoint_type': endpoint_type,
            'files': files,
            'status': status
        }

    except Exception as e:
        print("CRITICAL ERROR:", str(e))
        return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    file_path = "ADD_workflow_baseset.yaml"

    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        result = parse_argo_workflow(file_content)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(json.dumps({"error": "File not found"}, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))

    file_path = "RUNNING_workflow_baseset.yaml"

    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        result = parse_argo_workflow(file_content)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(json.dumps({"error": "File not found"}, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))

    file_path = "SUCCEED_workflow_baseset.yaml"

    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        result = parse_argo_workflow(file_content)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(json.dumps({"error": "File not found"}, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
