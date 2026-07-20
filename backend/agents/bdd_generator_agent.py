from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are an expert Senior QA Automation Architect with 15+ years of experience designing enterprise Selenium automation frameworks.
Your ONLY responsibility is to generate production-ready Cucumber .feature files.
Generate VALID Gherkin syntax only. No JSON, no YAML, no explanations.
Use Given/When/Then structure. Include meaningful scenario names. Include Background if applicable.
Never use Thread.sleep(). Never output JSON inside .feature files."""


class BDDGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("BDDGeneratorAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases', 'project_id']):
                raise ValueError("Missing required input fields")

            test_cases = input_data['test_cases']
            project_id = input_data['project_id']
            document_content = input_data.get('document_content', '')

            feature_files = self._generate_feature_files(test_cases, document_content)

            output_data = {
                "project_id": project_id,
                "feature_files": feature_files,
                "total_features": len(feature_files),
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"BDD feature files generated: {len(feature_files)}")
            return output_data

        except Exception as e:
            self.logger.error(f"BDD generation failed: {str(e)}", exc_info=True)
            return {"feature_files": [], "total_features": 0, "status": "failed", "error": str(e)}

    def _generate_feature_files(self, test_cases: List[Dict[str, Any]], document_content: str) -> List[Dict[str, Any]]:
        test_cases_text = self._format_test_cases(test_cases)

        user_prompt = f"""Generate Cucumber .feature files based on the following test cases extracted from the uploaded documents.

Document Content:
{document_content[:3000]}

Test Cases:
{test_cases_text}

Return each feature file using this exact format:
=== FILE: FeatureName.feature ===
[feature file content]

Generate complete, executable Cucumber feature files with proper Gherkin syntax."""

        self.logger.info("Calling LLM to generate feature files...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

        if response:
            self.logger.info(f"LLM returned {len(response)} chars for feature files")
            return self._parse_files(response, '.feature')
        else:
            self.logger.warning("LLM returned no response for feature files")
            return []

    def _format_test_cases(self, test_cases: List[Dict[str, Any]]) -> str:
        lines = []
        for tc in test_cases:
            lines.append(f"Test ID: {tc.get('test_id', 'TC-001')}")
            lines.append(f"Scenario: {tc.get('scenario', '')}")
            lines.append(f"Preconditions: {', '.join(tc.get('preconditions', []))}")
            lines.append(f"Steps: {', '.join(tc.get('steps', []))}")
            lines.append(f"Expected: {', '.join(tc.get('expected_results', []))}")
            lines.append("")
        return "\n".join(lines)

    def _parse_files(self, response: str, extension: str) -> List[Dict[str, Any]]:
        files = []
        parts = re.split(r'=== FILE: (.+?) ===', response)
        i = 1
        while i < len(parts) - 1:
            filename = parts[i].strip()
            content = parts[i + 1].strip()
            if content:
                files.append({
                    "feature_id": str(uuid.uuid4()),
                    "feature_name": filename.replace(extension, '').replace('_', ' '),
                    "filename": filename if filename.endswith(extension) else filename + extension,
                    "content": content
                })
            i += 2

        if not files and response.strip():
            files.append({
                "feature_id": str(uuid.uuid4()),
                "feature_name": "Generated Feature",
                "filename": f"generated{extension}",
                "content": response.strip()
            })

        return files
