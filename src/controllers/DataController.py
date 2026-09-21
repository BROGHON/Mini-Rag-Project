from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import os
import re
from pathlib import Path

class DataController(BaseController):



    def __init__(self):
        super().__init__()

    def validate_uploaded_file(self, file: UploadFile):
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED
        
        return True, ResponseSignal.FILE_UPLOADED_SUCCESS

    
    def generate_unique_filepath(self, orig_file_name: str, project_id:str):

        random_filename = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

    
        cleaned_file_name = self.get_clean_file_name(
            orig_file_name= orig_file_name
        )

        new_file_path = os.path.join(
            project_path,
            random_filename + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )
        return new_file_path, os.path.basename(new_file_path)

    def get_clean_file_name(self, orig_file_name: str) -> str:
        # Get only the filename, removing any directory/path components
        orig_file_name = Path(orig_file_name).name

        # Separate filename and extension
        name = Path(orig_file_name).stem
        extension = Path(orig_file_name).suffix

        # Replace whitespace with underscores
        name = re.sub(r"\s+", "_", name)

        # Keep only letters, numbers, underscores, and hyphens
        name = re.sub(r"[^a-zA-Z0-9_-]", "", name)

        # Remove consecutive underscores/hyphens
        name = re.sub(r"[_-]+", "_", name)

        # Remove leading/trailing underscores
        name = name.strip("_")

        return f"{name}{extension.lower()}"