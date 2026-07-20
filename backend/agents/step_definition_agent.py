from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are a Principal SDET specialising in Java Cucumber BDD step definitions.
Generate production-ready Step Definition classes from Gherkin feature files.

MANDATORY CODING STANDARDS:
1. package stepdefinitions;
2. Imports: io.cucumber.java.en.Given/When/Then, org.junit.Assert, and every Page class used
3. Step regex pattern must EXACTLY match the Gherkin step text (case-insensitive string match)
4. Parameterise steps with {string} for quoted values and {int} for numeric values
5. NEVER duplicate a step definition — if two scenarios share a step, use one method
6. Instantiate Page Objects via the shared ScenarioContext or a PicoContainer-style constructor
7. For Then/And assertion steps: use Assert.assertEquals(expected, actual) with a descriptive failure message
   Example: Assert.assertEquals(\"Expected success message\", \"Registration successful. Please check your email.\", actualMsg);
8. For Then steps that check HTTP status or API response: use assertEquals with the exact value from Expected Output
9. Use WebDriverWait from BasePage — never Thread.sleep()
10. Organise step defs by feature: one class per Feature file (AuthenticationSteps, CartSteps, etc.)
11. All fields initialised in the constructor or @Before hook — no static state
12. Every method must have real code, no TODOs, no placeholders
13. Return ONLY Java source code, no prose, no markdown fences"""


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
            f"=== {f.get('filename', f.get('feature_name',''))} ===\n{f.get('content','')}"
            for f in feature_files
        ])
        page_api = self._extract_page_api(page_objects)

        user_prompt = f"""Generate Java Cucumber Step Definition classes for the feature files below.

FEATURE FILES (map every step to a @Given/@When/@Then method):
{feature_content[:4500]}

AVAILABLE PAGE OBJECT API (use ONLY these methods — do not invent new ones):
{page_api}

INSTRUCTIONS:
- Create one Step Definition class per Feature file
  (AuthenticationSteps.java, ShoppingCartSteps.java, etc.)
- The class must hold page object instances and a WebDriver field
- Initialise WebDriver and all page objects in the constructor
- Every Gherkin step must have exactly one corresponding @Given/@When/@Then method
- Match the step annotation text EXACTLY to the Gherkin step (excluding leading keyword)
- Use parameterised {string}/{int} where the Gherkin step uses double-quoted values or numbers
- Then-step assertions must use Assert.assertEquals(\"message\", expected, actual)
- Use the exact assertion values already embedded in the Gherkin Then steps

Return each file using this EXACT delimiter:
=== FILE: ClassName.java ===
[complete compilable Java class]"""

        self.logger.info("Calling LLM to generate step definitions...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=6000)

        if response:
            self.logger.info(f"LLM returned {len(response)} chars for step definitions")
            return self._parse_java_files(response)
        else:
            self.logger.warning("LLM returned no response for step definitions")
            return []

    def _extract_page_api(self, page_objects: List[Dict[str, Any]]) -> str:
        """Extract public method signatures from generated page object classes."""
        lines = []
        sig_pattern = re.compile(
            r'^\s*public\s+(?!class|interface|enum|static\s+class)'
            r'(?:[A-Za-z][\w<>\[\],\s]*)\s+([a-z][\w]*)\s*\([^)]*\)',
            re.MULTILINE
        )
        for po in page_objects:
            name = po.get('class_name') or po.get('page_name', 'UnknownPage')
            content = po.get('content', '')
            methods = sorted(set(sig_pattern.findall(content)))
            if methods:
                lines.append(f"{name}: {', '.join(methods)}")
            else:
                lines.append(f"{name}: (see generated class for available methods)")
        return "\n".join(lines) if lines else "(no page objects available)"

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
