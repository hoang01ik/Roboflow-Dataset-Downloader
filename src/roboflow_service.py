import os
from datetime import datetime
from roboflow import Roboflow

class RoboflowService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rf = Roboflow(api_key=api_key)

    def list_projects(self, workspace_id: str):
        """Returns a list of project IDs in the workspace."""
        try:
            workspace = self.rf.workspace(workspace_id)
            # Fetch project list
            projects = workspace.projects()
            # If project ID is in 'workspace/project' format, strip the workspace part
            clean_projects = [p.split("/")[-1] for p in projects]
            return True, clean_projects
        except Exception as e:
            return False, str(e)

    def list_versions(self, workspace_id: str, project_id: str):
        """Returns a list of version numbers for a project."""
        try:
            workspace = self.rf.workspace(workspace_id)
            project = workspace.project(project_id)
            versions = project.versions()
            # Return list of version numbers (strings)
            return True, [str(v.version.split("/")[-1]) for v in versions]
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_available_formats():
        """Returns common Roboflow export formats."""
        return ["yolo26", "yolov11", "yolov10", "yolov8", "yolov9", "yolov5py", "coco", "tfrecord", "csv"]

    def download_dataset(self, 
                         workspace_id: str, 
                         project_id: str, 
                         version: str, 
                         model_format: str, 
                         target_root: str = "datasets",
                         log_callback=None):
        """
        Downloads a dataset from Roboflow and returns the target directory path.
        """
        try:
            if log_callback:
                log_callback(f"Connecting to workspace: {workspace_id}...")
            
            workspace = self.rf.workspace(workspace_id)
            project = workspace.project(project_id)
            
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_dir = os.path.join(target_root, f"{project_id}_{now_str}")
            
            if log_callback:
                log_callback(f"Starting download for {project_id} v{version}...")
            
            # Tải dataset
            dataset = project.version(int(version)).download(model_format, location=target_dir)
            
            return True, target_dir
        except Exception as e:
            return False, str(e)
