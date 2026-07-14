from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid


class RequirementExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__("RequirementExtractionAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['document_id', 'parsed_content']):
                raise ValueError("Missing required input fields")

            document_id = input_data['document_id']
            parsed_content = input_data['parsed_content']

            requirements = self._extract_requirements(parsed_content)

            output_data = {
                "document_id": document_id,
                "requirements": requirements,
                "total_requirements": len(requirements),
                "status": "extracted"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Requirements extracted: {len(requirements)} from {document_id}")

            return output_data

        except Exception as e:
            self.logger.error(f"Requirement extraction failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _extract_requirements(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        requirements = []
        
        headings = parsed_content.get('headings', [])
        paragraphs = parsed_content.get('paragraphs', [])
        tables = parsed_content.get('tables', [])

        for heading in headings:
            if any(keyword in heading.lower() for keyword in ['requirement', 'feature', 'business rule']):
                requirement = {
                    "requirement_id": str(uuid.uuid4()),
                    "feature": heading,
                    "business_rules": [],
                    "workflows": [],
                    "validations": [],
                    "preconditions": [],
                    "dependencies": []
                }
                requirements.append(requirement)

        for table in tables:
            if len(table) > 0:
                for row in table[1:]:
                    if len(row) > 0:
                        requirement = {
                            "requirement_id": str(uuid.uuid4()),
                            "feature": row[0] if len(row) > 0 else "",
                            "business_rules": [row[i] for i in range(1, len(row))] if len(row) > 1 else [],
                            "workflows": [],
                            "validations": [],
                            "preconditions": [],
                            "dependencies": []
                        }
                        if requirement["feature"]:
                            requirements.append(requirement)

        return requirements
