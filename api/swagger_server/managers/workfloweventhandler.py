from .argofileextractor import parse_argo_workflow


class WorkflowEventHandler:
    """
    This class handles a generic workflow event (ADD, UPDATE, FINISH, etc.)
    by ensuring files listed in the workflow JSON are present in the primary endpoint.
    """

    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager

    def handle_workflow_event(self, workflow_json: dict):
        """
        Entry point for handling any workflow event. 
        It parses the workflow JSON for endpoints/files and calls helpers to ensure files are present.
        
        Args:
            workflow_json (dict): A dictionary containing (at minimum):
                - 'primary_endpoint': str
                - 'secondary_endpoint': str
                - 'files': list of filenames
        """

        workflow_data = parse_argo_workflow(workflow_json)

        print(f"workflowdata: {workflow_data}")

        primary_endpoint = f"{self.cache_manager.rclone_manager.get_endpoint_name(workflow_data.get('primary_endpoint'))}:"
        secondary_endpoint = f"{self.cache_manager.rclone_manager.get_endpoint_name(workflow_data.get('secondary_endpoint'))}:"
        primary_folder = workflow_data.get("primary_folder")
        secondary_folder = workflow_data.get("secondary_folder")
        files = workflow_data.get("files", [])

        # Update the shared CacheManager via setters instead of re-instantiating
        self.cache_manager.set_primary_endpoint(primary_endpoint)
        self.cache_manager.set_primary_folder(primary_folder)
        self.cache_manager.set_secondary_endpoint(secondary_endpoint)
        self.cache_manager.set_secondary_folder(secondary_folder)
        self.cache_manager.set_files(files)

        # sync cache
        self.cache_manager.sync_cache()

        # Start the cache synchronization process
        self.cache_manager.start()
