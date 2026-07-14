from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import json
from utils.openai_client import openai_client


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
        
        # Prepare content for OpenAI
        content_text = self._prepare_content_text(parsed_content)
        
        # Use OpenAI to extract requirements
        openai_response = openai_client.extract_requirements(content_text)
        
        if openai_response:
            # Parse OpenAI response and structure requirements
            requirements = self._parse_openai_requirements(openai_response)
        else:
            # Fallback to basic extraction if OpenAI fails
            requirements = self._basic_extract_requirements(parsed_content)
        
        return requirements

    def _prepare_content_text(self, parsed_content: Dict[str, Any]) -> str:
        """Prepare parsed content as text for Gemini"""
        text_parts = []
        
        if parsed_content.get('headings'):
            text_parts.append("Headings:\n" + "\n".join(parsed_content['headings']))
        
        if parsed_content.get('paragraphs'):
            text_parts.append("Content:\n" + "\n".join(parsed_content['paragraphs']))
        
        if parsed_content.get('tables'):
            text_parts.append("Tables:\n" + str(parsed_content['tables']))
        
        return "\n\n".join(text_parts)

    def _parse_openai_requirements(self, openai_response: str) -> List[Dict[str, Any]]:
        """Parse OpenAI response into structured requirements"""
        requirements = []
        
        # Split response by requirement lines
        lines = openai_response.split('\n')
        current_req = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a requirement line (e.g., "REQ-001: ...")
            if line.startswith('REQ-') or (current_req is None and ':' in line):
                if current_req:
                    requirements.append(current_req)
                
                parts = line.split(':', 1)
                req_id = parts[0].strip() if len(parts) > 0 else f"REQ-{len(requirements)+1:03d}"
                description = parts[1].strip() if len(parts) > 1 else line
                
                current_req = {
                    "requirement_id": req_id,
                    "feature": description,
                    "business_rules": [],
                    "workflows": [],
                    "validations": [],
                    "preconditions": [],
                    "dependencies": []
                }
            elif current_req and line.startswith('-'):
                # Add as business rule
                rule = line.lstrip('- ').strip()
                if rule:
                    current_req["business_rules"].append(rule)
        
        if current_req:
            requirements.append(current_req)
        
        return requirements

    def _basic_extract_requirements(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback basic extraction if Gemini is unavailable"""
        requirements = []
        
        headings = parsed_content.get('headings', [])
        tables = parsed_content.get('tables', [])

        for heading in headings:
            if any(keyword in heading.lower() for keyword in ['requirement', 'feature', 'business rule']):
                requirement = {
                    "requirement_id": f"REQ-{len(requirements)+1:03d}",
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
                            "requirement_id": f"REQ-{len(requirements)+1:03d}",
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
