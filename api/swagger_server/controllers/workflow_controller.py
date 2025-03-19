import connexion
from flask import jsonify, request
from swagger_server.models.workflow_event import WorkflowEvent  # noqa: E501
from ..managers.workfloweventhandler import WorkflowEventHandler
from swagger_server.__main__ import workflow_event_handler

import json
import yaml
import base64

def workflow_event_handler_post():  # noqa: E501
    """Handle a workflow event"""

    # Step 1: Read raw data
    try:
        raw_data = request.get_data()
        if not raw_data:
            return jsonify({"error": "Empty request body"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to read request body: {str(e)}"}), 400

    # Step 2: Parse JSON first, fallback to YAML
    try:
        parsed_data = json.loads(raw_data.decode('utf-8'))
    except json.JSONDecodeError:
        try:
            parsed_data = yaml.safe_load(raw_data.decode('utf-8'))
        except yaml.YAMLError:
            return jsonify({"error": "Unsupported content type, expecting JSON or YAML"}), 400

    print("\n--- Parsed Incoming Data ---")
    print(json.dumps(parsed_data))

    # Step 3: Handle different payload structures

    # Case 1: Direct UPDATE or ADD event (commonly from event stream)
    event_type = parsed_data.get("type")
    workflow_event = parsed_data.get("body")

    if event_type in ["UPDATE", "ADD"] and workflow_event:
        print(f"\n--- Handling event type: {event_type} ---")

        try:
            workflow_event_handler.handle_workflow_event(workflow_event)
            return jsonify({"message": f"Workflow {event_type} event handled successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to handle {event_type} workflow event: {str(e)}"}), 500

    # Case 2: workflow_submission or full_event
    event_key = None
    if "workflow_submission" in parsed_data:
        event_key = "workflow_submission"
    elif "full_event" in parsed_data:
        event_key = "full_event"

    if event_key:
        workflow_submission = parsed_data.get(event_key)

        # If workflow_submission is a JSON string, parse it
        if isinstance(workflow_submission, str):
            try:
                workflow_submission = json.loads(workflow_submission)
            except json.JSONDecodeError:
                return jsonify({"error": f"Invalid JSON in {event_key}"}), 400

        # Case 2.1: Base64-encoded `data` inside workflow_submission
        data_b64 = workflow_submission.get("data")
        if data_b64:
            try:
                decoded_data_str = base64.b64decode(data_b64).decode('utf-8')
                decoded_data_json = json.loads(decoded_data_str)
                print("\n--- Decoded Base64 Data ---")
                print(json.dumps(decoded_data_json))

                # Pass decoded data to handler
                try:
                    workflow_event_handler.handle_workflow_event(decoded_data_json)
                    return jsonify({"message": "Base64 decoded workflow event handled successfully"}), 200
                except Exception as e:
                    return jsonify({"error": f"Failed to handle decoded workflow event: {str(e)}"}), 500

            except Exception as e:
                return jsonify({"error": f"Failed to decode base64 data: {str(e)}"}), 400

        # Case 2.2: No `data` field, pass workflow_submission directly
        try:
            workflow_event_handler.handle_workflow_event(workflow_submission)
            return jsonify({"message": "Workflow submission handled successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to handle workflow submission: {str(e)}"}), 500

    # Fallback: Unrecognized structure
    return jsonify({"error": "Unsupported workflow event format"}), 400
