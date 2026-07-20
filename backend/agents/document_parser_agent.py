from .base_agent import BaseAgent
from typing import Dict, Any
from parsers.document_parser import DocumentParser


class DocumentParserAgent(BaseAgent):
    def __init__(self):
        super().__init__("DocumentParserAgent")
        self.parser = DocumentParser()

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['document_id', 'file_path', 'document_type']):
                raise ValueError("Missing required input fields")

            document_id = input_data['document_id']
            file_path = input_data['file_path']
            document_type = input_data['document_type']

            parsed_content = self.parser.parse_document(file_path, document_type)

            output_data = {
                "document_id": document_id,
                "document_type": document_type,
                "parsed_content": parsed_content,
                "status": "parsed"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Document parsed successfully: {document_id}")

            return output_data

        except Exception as e:
            self.logger.error(f"Document parsing failed for {input_data.get('file_path')}: {str(e)}", exc_info=True)
            output_data = {
                "document_id": input_data.get('document_id'),
                "document_type": input_data.get('document_type'),
                "parsed_content": {"paragraphs": [], "lines": [], "content": "", "tables": [], "headings": []},
                "status": "failed",
                "error": str(e)
            }
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            return output_data
