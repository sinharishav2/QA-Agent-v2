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
        """Generate one step definition class per feature file to ensure full step coverage."""
        page_api = self._extract_page_api(page_objects)
        all_step_defs: List[Dict[str, Any]] = []

        for feature in feature_files:
            result = self._generate_for_single_feature(feature, page_api)
            all_step_defs.extend(result)

        return all_step_defs

    def _generate_for_single_feature(self, feature: Dict[str, Any], page_api: str) -> List[Dict[str, Any]]:
        """Generate a step definition class for one feature file."""
        raw_name = feature.get('filename', feature.get('feature_name', 'Feature'))
        feature_name = raw_name.split('/')[-1].split('\\')[-1]  # basename only
        content = feature.get('content', '').strip()
        if not content:
            return []

        base = re.sub(r'\.feature$', '', feature_name, flags=re.IGNORECASE)
        class_name = re.sub(r'[^\w]', '', base.replace(' ', '_').title().replace('_', '')) + 'Steps'

        # Extract unique step texts for explicit coverage instruction
        step_texts = re.findall(r'^\s*(?:Given|When|Then|And|But)\s+(.+)', content, re.MULTILINE)
        steps_list = '\n'.join(f'  - {s.strip()}' for s in dict.fromkeys(step_texts))

        user_prompt = f"""Generate ONE Java Cucumber Step Definition class: {class_name}.java

FEATURE FILE TO IMPLEMENT IN FULL:
{content}

STEPS THAT MUST EACH HAVE AN @Given/@When/@Then METHOD ({len(step_texts)} steps):
{steps_list}

PAGE OBJECT API (use only these methods):
{page_api}

REQUIREMENTS:
- Class: {class_name}, package stepdefinitions;
- Implement EVERY step listed above — no step may be skipped
- Deduplicate steps shared across scenarios (one method per unique text)
- Parameterise {'{string}'}/{'{int}'} for quoted/numeric values in step text
- Assert.assertEquals(\"message\", expected, actual) in all Then-step assertions
- WebDriver + page objects initialised in constructor (no static state)

Return ONLY:
=== FILE: {class_name}.java ===
[complete compilable Java class]"""

        self.logger.info(f"Generating step definitions for {feature_name} ({len(step_texts)} steps)...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

        if response:
            parsed = self._parse_java_files(response)
            if not parsed:
                parsed = [{
                    "step_id": str(uuid.uuid4()),
                    "name": class_name,
                    "filename": f"{class_name}.java",
                    "content": response.strip()
                }]
            return parsed
        self.logger.warning(f"No LLM response for {feature_name} step definitions")
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
