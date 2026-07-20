from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are an expert Senior QA Automation Architect with 15+ years of experience designing enterprise Selenium automation frameworks.
Your ONLY responsibility is to generate production-ready Java Selenium Page Object classes.
Rules:
- Use PageFactory with @FindBy annotations
- Use WebDriverWait, never Thread.sleep()
- Each page exposes actions, never assertions, never public WebElements
- Use id > name > cssSelector > xpath locator priority
- Every file must compile
- No JSON, no YAML, no explanations - only Java source code"""


class PageObjectAgent(BaseAgent):
    def __init__(self):
        super().__init__("PageObjectAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases', 'project_id']):
                raise ValueError("Missing required input fields")

            test_cases = input_data['test_cases']
            project_id = input_data['project_id']
            document_content = input_data.get('document_content', '')

            page_objects = self._generate_page_objects(test_cases, document_content)

            output_data = {
                "project_id": project_id,
                "page_objects": page_objects,
                "total_pages": len(page_objects),
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Page objects generated: {len(page_objects)}")
            return output_data

        except Exception as e:
            self.logger.error(f"Page object generation failed: {str(e)}", exc_info=True)
            return {"page_objects": [], "total_pages": 0, "status": "failed", "error": str(e)}

    def _generate_page_objects(self, test_cases: List[Dict[str, Any]], document_content: str) -> List[Dict[str, Any]]:
        test_cases_text = "\n".join([
            f"- {tc.get('test_id','')}: {tc.get('scenario','')} | Steps: {', '.join(tc.get('steps',[]))}"
            for tc in test_cases
        ])

        user_prompt = f"""Generate Java Selenium Page Object classes for the following application based on the test cases.

Document Content:
{document_content[:3000]}

Test Cases:
{test_cases_text}

Requirements:
- package pages;
- Use PageFactory with @FindBy annotations
- Use WebDriverWait for all interactions
- Each class must have a constructor accepting WebDriver
- Expose action methods, never public WebElements
- Use SOLID principles

Return each Java class using this exact format:
=== FILE: ClassName.java ===
[complete Java class content]

Generate all page classes needed to cover the test cases."""

        self.logger.info("Calling LLM to generate page objects...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

        if response:
            self.logger.info(f"LLM returned {len(response)} chars for page objects")
            return self._parse_java_files(response)
        else:
            self.logger.warning("LLM returned no response for page objects")
            return []

    def _parse_java_files(self, response: str) -> List[Dict[str, Any]]:
        files = []
        parts = re.split(r'=== FILE: (.+?) ===', response)
        i = 1
        while i < len(parts) - 1:
            filename = parts[i].strip()
            content = parts[i + 1].strip()
            if content:
                class_name = filename.replace('.java', '')
                files.append({
                    "page_id": str(uuid.uuid4()),
                    "class_name": class_name,
                    "page_name": class_name,
                    "filename": filename if filename.endswith('.java') else filename + '.java',
                    "content": content
                })
            i += 2

        if not files and response.strip():
            files.append({
                "page_id": str(uuid.uuid4()),
                "class_name": "GeneratedPage",
                "page_name": "GeneratedPage",
                "filename": "GeneratedPage.java",
                "content": response.strip()
            })

        return files
