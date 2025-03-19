from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import yaml
import base64
from argoFileExtractor import parse_argo_workflow  # Import the function

class WorkflowHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        parsed_data = None

        # Try JSON decoding first
        try:
            parsed_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            try:
                parsed_data = yaml.safe_load(post_data.decode('utf-8'))
            except yaml.YAMLError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Unsupported content type; please send JSON or YAML')
                return

        # Determine the key that contains the event
        event_key = "workflow_submission" if "workflow_submission" in parsed_data else "full_event"
        workflow_submission = parsed_data.get(event_key, {})

        if isinstance(workflow_submission, str):  # Ensure it's a string before parsing
            try:
                workflow_submission = json.loads(workflow_submission)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid JSON in event data')
                return

        # Extract and decode the 'data' field
        base64_encoded_data = workflow_submission.get("data", "")
        decoded_data = None
        if base64_encoded_data:
            try:
                decoded_data = base64.b64decode(base64_encoded_data).decode('utf-8')
                decoded_data = json.loads(decoded_data)  # Convert to JSON
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'Failed to decode base64 data: {str(e)}'.encode('utf-8'))
                return

        print(decoded_data)

        # Process the workflow submission with parse_argo_workflow
        parsed_workflow = parse_argo_workflow(decoded_data)

        # Pretty print the parsed workflow data
        print("\n--- Parsed Workflow Data ---")
        print(json.dumps(parsed_workflow, indent=4))

        # Send a 200 OK response with the parsed workflow data
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(parsed_workflow).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('0.0.0.0', 13337)
    httpd = HTTPServer(server_address, WorkflowHandler)
    print("🚀 Server is running on port 13337... 🚀")
    httpd.serve_forever()

