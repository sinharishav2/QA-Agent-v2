from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are a Principal SDET specialising in Java Cucumber BDD step definitions.
Generate production-ready Step Definition classes from Gherkin feature files.

MANDATORY CODING STANDARDS:
1. package stepdefinitions;
2. Imports: io.cucumber.java.en.Given/When/Then, org.junit.Assert, org.openqa.selenium.WebDriver, config.DriverFactory, and every Page class used (package pages)
3. WIRING PATTERN — use EXACTLY this driver/page lifecycle (it must compile against DriverFactory and page constructors that take WebDriver):
   public class AuthenticationSteps {
       private final WebDriver driver = DriverFactory.getDriver();
       private final LoginPage loginPage = new LoginPage(driver);
       private final DashboardPage dashboardPage = new DashboardPage(driver);
       ...
   }
   NEVER instantiate BasePage directly. NEVER call a page constructor without the driver argument.
4. Step pattern must EXACTLY match the Gherkin step text
5. Parameterise steps with {string} for quoted values and {int} for numeric values — one parameterised method replaces near-identical steps
6. NEVER duplicate a step definition — each unique step pattern string must appear EXACTLY ONCE
   in the class. Before finishing, re-check the file: no two annotations may share the same pattern.
7. ASSERTION RULE — every Then/And assertion MUST compare an EXPECTED literal against an ACTUAL
   value fetched live from a Page Object getter:
   Assert.assertEquals(\"Order status mismatch\", \"Processed\", orderPage.getOrderStatus());
   FORBIDDEN (tautological — never write these):
   - Assert.assertEquals(\"msg\", \"X\", \"X\")          // literal vs literal
   - Assert.assertEquals(\"msg\", expected, expected)  // same variable twice
   - Assert.assertTrue(\"msg\", true)                  // constant condition
   If the Page Object lacks a getter for the value being verified, call the most plausible
   getter name (e.g. page.getStatusMessage()) — do NOT fall back to a constant.
8. Assert exact expected values from the Expected Output / requirements
9. Use WebDriverWait via the Page Object methods — never Thread.sleep()
10. Organise step defs by feature: one class per Feature file (AuthenticationSteps, CartSteps, etc.)
11. Keep step methods thin: delegate ALL UI interaction to Page Object methods; step methods contain flow + assertions only.
    Each step performs its action exactly ONCE — never call two page methods that trigger the same operation.
12. Store values shared between steps (e.g. entered data, expected messages) in private instance fields
13. Every method must have real, complete code — no TODOs, no placeholders, no truncated bodies
14. Return ONLY Java source code, no prose, no markdown fences"""


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
        """Generate one step definition class per feature file with global step dedup.

        Cucumber treats duplicate step patterns across classes as ambiguous, so steps
        already implemented by an earlier class are excluded from later classes.
        """
        page_api = self._extract_page_api(page_objects)
        all_step_defs: List[Dict[str, Any]] = []
        implemented: set = set()  # normalized step patterns implemented so far

        for feature in feature_files:
            result = self._generate_for_single_feature(feature, page_api, implemented)
            all_step_defs.extend(result)

        return all_step_defs

    @staticmethod
    def _normalize_step(step: str) -> str:
        """Normalize a Gherkin step so data-driven variants map to one parameterized pattern."""
        s = step.strip().lower()
        s = re.sub(r'"[^"]*"', '{string}', s)   # quoted values -> {string}
        s = re.sub(r'<[^>]+>', '{param}', s)      # outline placeholders
        s = re.sub(r'\b\d+(?:\.\d+)?\b', '{int}', s)  # numbers -> {int}
        return re.sub(r'\s+', ' ', s)

    def _generate_for_single_feature(self, feature: Dict[str, Any], page_api: str, implemented: set = None) -> List[Dict[str, Any]]:
        """Generate a step definition class for one feature file, skipping steps already implemented elsewhere."""
        implemented = implemented if implemented is not None else set()
        raw_name = feature.get('filename', feature.get('feature_name', 'Feature'))
        feature_name = raw_name.split('/')[-1].split('\\')[-1]  # basename only
        content = feature.get('content', '').strip()
        if not content:
            return []

        base = re.sub(r'\.feature$', '', feature_name, flags=re.IGNORECASE)
        class_name = re.sub(r'[^\w]', '', base.replace(' ', '_').title().replace('_', '')) + 'Steps'

        # Extract unique step texts; exclude steps already implemented in earlier classes
        step_texts = list(dict.fromkeys(
            s.strip() for s in re.findall(r'^\s*(?:Given|When|Then|And|But)\s+(.+)', content, re.MULTILINE)
        ))
        new_steps = [s for s in step_texts if self._normalize_step(s) not in implemented]
        skipped   = [s for s in step_texts if self._normalize_step(s) in implemented]

        if not new_steps:
            self.logger.info(f"All steps of {feature_name} already implemented — skipping class generation")
            return []

        for s in new_steps:
            implemented.add(self._normalize_step(s))

        steps_list = '\n'.join(f'  - {s}' for s in new_steps)
        skipped_note = ''
        if skipped:
            skipped_list = '\n'.join(f'  - {s}' for s in skipped)
            skipped_note = f"""
STEPS ALREADY IMPLEMENTED IN OTHER CLASSES — DO NOT implement these again (Cucumber resolves them globally):
{skipped_list}
"""

        user_prompt = f"""Generate ONE Java Cucumber Step Definition class: {class_name}.java

FEATURE FILE (for context):
{content}

STEPS THAT MUST EACH HAVE AN @Given/@When/@Then METHOD ({len(new_steps)} steps — implement ONLY these):
{steps_list}
{skipped_note}
PAGE OBJECT API (use only these methods):
{page_api}

REQUIREMENTS:
- Class: {class_name}, package stepdefinitions;
- Implement EVERY step listed above — no step may be skipped
- Deduplicate steps shared across scenarios (one method per unique text)
- Parameterise {'{string}'}/{'{int}'} for quoted/numeric values in step text
- Assert.assertEquals(\"message\", expected, actual) in all Then-step assertions — assert the exact expected values from the feature file
- Initialise driver via DriverFactory.getDriver() and pass it to every page constructor:
  private final WebDriver driver = DriverFactory.getDriver();
  private final SomePage somePage = new SomePage(driver);
- Do NOT instantiate BasePage; do NOT use static driver state

Return ONLY:
=== FILE: {class_name}.java ===
[complete compilable Java class]"""

        self.logger.info(f"Generating step definitions for {feature_name} ({len(new_steps)} new steps, {len(skipped)} shared)...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=6000)

        if response:
            parsed = self._parse_java_files(response)
            if not parsed:
                parsed = [{
                    "step_id": str(uuid.uuid4()),
                    "name": class_name,
                    "filename": f"{class_name}.java",
                    "content": response.strip()
                }]
            else:
                # Force the expected class name — prevents misnamed fallbacks causing ZIP duplicates
                parsed[0]['filename'] = f"{class_name}.java"
                parsed[0]['name']     = class_name
                parsed = parsed[:1]  # one class per feature file
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
