from .base_agent import BaseAgent
from typing import Dict, Any
import uuid
from datetime import datetime
import os
from pathlib import Path


class DocumentIngestionAgent(BaseAgent):
    def __init__(self):
        super().__init__("DocumentIngestionAgent")
        self.supported_types = ['.docx', '.xlsx', '.xls', '.pdf', '.txt', '.csv']

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['file_path', 'document_type', 'project_id']):
                raise ValueError("Missing required input fields")

            file_path = input_data['file_path']
            document_type = input_data['document_type']
            project_id = input_data['project_id']

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_extension = Path(file_path).suffix.lower()
            if file_extension not in self.supported_types:
                raise ValueError(f"Unsupported file type: {file_extension}")

            document_id = str(uuid.uuid4())
            
            output_data = {
                "document_id": document_id,
                "document_type": document_type,
                "project_id": project_id,
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "status": "ingested"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Document ingested successfully: {document_id}")

            return output_data

        except Exception as e:
            self.logger.error(f"Document ingestion failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise
