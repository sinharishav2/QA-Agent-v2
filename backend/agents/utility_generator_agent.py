from .base_agent import BaseAgent
from typing import Dict, Any
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are an expert Senior QA Automation Architect with 15+ years of experience designing enterprise Selenium automation frameworks.
Generate production-ready Java framework infrastructure files for Selenium + Cucumber.
Every file must compile. No placeholders. No TODOs. SOLID principles. Real implementations only."""


class UtilityGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("UtilityGeneratorAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['project_id', 'framework']):
                raise ValueError("Missing required input fields")

            project_id = input_data['project_id']
            framework = input_data['framework']

            utilities = self._generate_framework_files()

            output_data = {
                "project_id": project_id,
                "framework": framework,
                "utilities": utilities,
                "total_utilities": len(utilities),
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Framework utilities generated: {len(utilities)}")
            return output_data

        except Exception as e:
            self.logger.error(f"Utility generation failed: {str(e)}", exc_info=True)
            return {"utilities": {}, "total_utilities": 0, "status": "failed", "error": str(e)}

    def _generate_framework_files(self) -> Dict[str, Any]:
        user_prompt = """Generate the complete Java Selenium + Cucumber framework infrastructure files.

Generate ALL of the following files:
1. DriverFactory.java (package config) - manages WebDriver lifecycle, thread-safe singleton
2. ConfigReader.java (package config) - reads from config.properties file
3. BasePage.java (package pages) - base class all page objects extend, with WaitUtils methods
4. Hooks.java (package hooks) - @Before and @After Cucumber hooks, takes screenshot on failure
5. TestRunner.java (package runners) - @RunWith(Cucumber.class) with @CucumberOptions
6. WaitUtils.java (package utils) - reusable WebDriverWait helper methods
7. ScreenshotUtils.java (package utils) - captures and saves screenshots

Return each file using this exact format:
=== FILE: FileName.java ===
[complete compilable Java class]

All classes must be production-ready, no TODOs, no placeholders."""

        self.logger.info("Calling LLM to generate framework files...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

        utilities = {}
        if response:
            self.logger.info(f"LLM returned {len(response)} chars for framework files")
            parts = re.split(r'=== FILE: (.+?) ===', response)
            i = 1
            while i < len(parts) - 1:
                filename = parts[i].strip()
                content = parts[i + 1].strip()
                if content:
                    name = filename.replace('.java', '')
                    utilities[name] = {
                        "utility_id": str(uuid.uuid4()),
                        "name": name,
                        "filename": filename if filename.endswith('.java') else filename + '.java',
                        "content": content
                    }
                i += 2
        else:
            self.logger.warning("LLM returned no response for framework files")

        return utilities
