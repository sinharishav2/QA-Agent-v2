from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are a Principal QA Automation Engineer at a top-tier software company specialising in enterprise BDD frameworks.
Generate production-ready Cucumber .feature files that are immediately executable with minimal manual edits.

STRICT GHERKIN RULES:
1. Feature title = business capability (not technical phrase)
2. Every Scenario title is unique and matches the source test case name
3. Tag every Scenario: @<priority-tag> @<module-tag> @req-<REQ-ID> (use @smoke for High priority, @regression for Medium/Low)
4. Use Background: block for shared preconditions across scenarios in the same Feature
5. Use Scenario Outline + Examples: for data-driven tests with 2+ data sets
6. Given = system state, When = user action, Then = verifiable observable outcome
7. Then steps MUST reference exact expected values from the Expected Output section when provided
   Example: Then the HTTP response status should be 201
            And the success message should be "Registration successful. Please check your email."
8. Avoid vague Then steps like "the user sees a message" – be specific
9. Each step line must be a single, atomic action or assertion
10. Add @negative tag to all negative / error scenarios
11. Never output JSON, YAML, or Java inside .feature files
12. Return ONLY valid Gherkin – no prose, no markdown fences"""


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
        modules = sorted(set(tc.get('module', 'General') for tc in test_cases if tc.get('module')))

        user_prompt = f"""Generate one Cucumber .feature file per module. Group test cases by their Module field.

Modules identified: {', '.join(modules) if modules else 'Authentication, Core'}

CONTEXT (Requirements + Expected Outputs):
{document_content[:4000]}

TEST CASES TO CONVERT:
{test_cases_text}

INSTRUCTIONS:
- One .feature file per module (e.g. Authentication.feature, ShoppingCart.feature)
- Group Scenarios from the same module into the same Feature file
- Carry @req-<REQ-ID> tags from the test cases where available
- Use Scenario Outline + Examples for any test case that tests multiple data inputs
- Extract exact error messages and HTTP codes from the Context section for Then steps
- Add Background: block if 2+ scenarios in a Feature share the same Given step

Return each file using this EXACT delimiter (no deviation):
=== FILE: ModuleName.feature ===
[complete feature file content]

Generate all feature files now."""

        self.logger.info("Calling LLM to generate feature files...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=6000)

        if response:
            self.logger.info(f"LLM returned {len(response)} chars for feature files")
            return self._parse_files(response, '.feature')
        else:
            self.logger.warning("LLM returned no response for feature files")
            return []

    def _format_test_cases(self, test_cases: List[Dict[str, Any]]) -> str:
        lines = []
        for tc in test_cases:
            lines.append(f"--- Test ID: {tc.get('test_id', 'TC-?')} | Priority: {tc.get('priority','Medium')} | Module: {tc.get('module','General')} ---")
            lines.append(f"Scenario Title : {tc.get('scenario', tc.get('title', '(untitled)'))!s}")
            preconditions = tc.get('preconditions', [])
            if preconditions:
                lines.append(f"Preconditions  : {'; '.join(preconditions)}")
            for i, step in enumerate(tc.get('steps', []), 1):
                lines.append(f"  Step {i}: {step}")
            expected = tc.get('expected_results', tc.get('expected', []))
            if expected:
                lines.append(f"Expected Results:")
                for exp in (expected if isinstance(expected, list) else [expected]):
                    lines.append(f"  - {exp}")
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
