from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are an expert Senior QA Automation Architect with 15+ years of experience designing enterprise Selenium automation frameworks.
Your ONLY responsibility is to generate production-ready Java Cucumber Step Definition classes.
Rules:
- package stepdefinitions;
- Use @Given, @When, @Then from io.cucumber.java.en
- Use parameterized steps: {string}, {int}
- Reference page objects for all interactions
- Use Assert from org.junit.Assert for assertions
- Use WebDriverWait, never Thread.sleep()
- No duplicate step definitions
- No placeholder implementations - every method must have real code
- Every file must compile"""


class StepDefinitionAgent(BaseAgent):
    def __init__(self):
        super().__init__("StepDefinitionAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['feature_files', 'project_id']):
                raise ValueError("Missing required input fields")

            feature_files = input_data['feature_files']
            project_id = input_data['project_id']
            page_objects = input_data.get('page_objects', [])

            step_definitions = self._generate_step_definitions(feature_files, page_objects)

            output_data = {
                "project_id": project_id,
                "step_definitions": step_definitions,
                "total_steps": len(step_definitions),
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Step definitions generated: {len(step_definitions)}")
            return output_data

        except Exception as e:
            self.logger.error(f"Step definition generation failed: {str(e)}", exc_info=True)
            return {"step_definitions": [], "total_steps": 0, "status": "failed", "error": str(e)}

    def _generate_step_definitions(self, feature_files: List[Dict[str, Any]], page_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        feature_content = "\n\n".join([
            f"Feature: {f.get('feature_name','')}\n{f.get('content','')}"
            for f in feature_files
        ])
        page_object_names = [p.get('class_name') or p.get('page_name', '') for p in page_objects]

        user_prompt = f"""Generate Java Cucumber Step Definition classes for the following feature files.

Feature Files:
{feature_content[:3000]}

Available Page Objects:
{', '.join(page_object_names)}

Requirements:
- package stepdefinitions;
- Import and instantiate each page object
- Implement every step from every feature file
- Use Assert.assertEquals / Assert.assertTrue for validations
- Use parameterized steps where applicable

Return each Java class using this exact format:
=== FILE: ClassName.java ===
[complete Java class content]"""

        self.logger.info("Calling LLM to generate step definitions...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

        if response:
            self.logger.info(f"LLM returned {len(response)} chars for step definitions")
            return self._parse_java_files(response)
        else:
            self.logger.warning("LLM returned no response for step definitions")
            return []

    def _parse_java_files(self, response: str) -> List[Dict[str, Any]]:
        files = []
        parts = re.split(r'=== FILE: (.+?) ===', response)
        i = 1
        while i < len(parts) - 1:
            filename = parts[i].strip()
            content = parts[i + 1].strip()
            if content:
                files.append({
                    "step_id": str(uuid.uuid4()),
                    "name": filename.replace('.java', ''),
                    "filename": filename if filename.endswith('.java') else filename + '.java',
                    "content": content
                })
            i += 2

        if not files and response.strip():
            files.append({
                "step_id": str(uuid.uuid4()),
                "name": "StepDefinitions",
                "filename": "StepDefinitions.java",
                "content": response.strip()
            })

        return files
