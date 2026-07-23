from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are a Principal QA Automation Engineer at a top-tier software company specialising in enterprise BDD frameworks.
Generate production-ready Cucumber .feature files that are immediately executable with minimal manual edits.

STRICT GHERKIN RULES:
1. Feature title = business capability (not technical phrase)
2. EVERY test case MUST become exactly ONE Scenario (or Scenario Outline) — never merge, drop, or skip a test case
3. Every Scenario title is unique and matches the source test case name
4. Tag every Scenario with ALL of: priority tag, module tag, and EVERY applicable @req-<REQ-ID>
   - A scenario that verifies multiple requirements carries multiple @req-* tags
   - Every requirement in the provided REQUIREMENTS list that is exercised by any test case MUST appear on at least one scenario
5. Tag the primary happy-path scenario of each Feature with @smoke (in addition to High-priority test cases); tag all others @regression
6. Use Background: block for shared preconditions across scenarios in the same Feature
7. Use Scenario Outline + Examples: for data-driven tests with 2+ data sets
8. Given = system state, When = user action, Then = verifiable observable outcome
9. Then steps MUST reference exact expected values from the Expected Output section when provided
   Example: Then the HTTP response status should be 201
            And the success message should be "Registration successful. Please check your email."
10. Avoid vague Then steps like "the user sees a message" – be specific: assert exact text, exact status, exact state
11. Each step line must be a single, atomic action or assertion
12. Add @negative tag to all negative / error scenarios
13. Never output JSON, YAML, or Java inside .feature files
14. Return ONLY valid Gherkin – no prose, no markdown fences"""


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
            requirements = input_data.get('requirements', [])

            feature_files = self._generate_feature_files(test_cases, document_content, requirements)

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

    # ------------------------------------------------------------------
    # Module derivation
    # ------------------------------------------------------------------

    _MODULE_KEYWORDS = [
        (['login', 'sign in', 'logout', 'authentication', 'auth'], 'Authentication'),
        (['register', 'sign up', 'create account', 'registration'], 'Registration'),
        (['reset password', 'forgot password'], 'PasswordReset'),
        (['cart', 'basket', 'add to cart', 'shopping cart', 'remove from cart'], 'ShoppingCart'),
        (['checkout', 'payment', 'order', 'purchase', 'billing'], 'Checkout'),
        (['product', 'catalog', 'browse', 'search', 'listing', 'category'], 'ProductCatalog'),
        (['profile', 'account settings', 'my account'], 'UserProfile'),
    ]

    def _derive_module(self, scenario: str) -> str:
        lower = scenario.lower()
        for keywords, module in self._MODULE_KEYWORDS:
            if any(k in lower for k in keywords):
                return module
        return 'CoreFunctionality'

    def _generate_feature_files(self, test_cases: List[Dict[str, Any]], document_content: str, requirements: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Derive module for every test case that doesn't have one
        for tc in test_cases:
            if not tc.get('module') or tc['module'].strip().lower() in ('general', 'core', ''):
                tc['module'] = self._derive_module(
                    tc.get('scenario', tc.get('title', ''))
                )

        test_cases_text = self._format_test_cases(test_cases)
        modules = sorted(set(tc.get('module', 'CoreFunctionality') for tc in test_cases))
        requirements_text = self._format_requirements(requirements or [])

        # If keyword-based module derivation failed for most test cases (unknown domain),
        # let the LLM derive functional groupings from the content instead.
        generic_count = sum(1 for tc in test_cases if tc.get('module') == 'CoreFunctionality')
        if test_cases and generic_count / len(test_cases) > 0.5:
            module_instruction = (
                "Derive the functional modules YOURSELF from the test cases and requirements "
                "(e.g. by business process, transaction type, or workflow stage). "
                f"Group the {len(test_cases)} scenarios into multiple Feature files — "
                "aim for one Feature per functional area (typically 3\u20136 files). "
                "Do NOT put all scenarios into a single Feature file."
            )
        else:
            module_instruction = f"Modules identified: {', '.join(modules)}"

        user_prompt = f"""Generate one Cucumber .feature file per functional module.

{module_instruction}

REQUIREMENTS TO TRACE (tag scenarios with the matching @req-<ID> tags — a scenario may carry several):
{requirements_text}

CONTEXT (Specification + Expected Outputs):
{document_content[:4000]}

TEST CASES TO CONVERT ({len(test_cases)} test cases → you MUST produce exactly {len(test_cases)} scenarios):
{test_cases_text}

INSTRUCTIONS:
- One .feature file per functional module, named after the module (PascalCase, e.g. OrderExport.feature)
- Group related Scenarios into the same Feature file; split unrelated ones into separate files
- STRICT COUNT RULE: EVERY test case becomes exactly ONE Scenario. Your output must contain
  EXACTLY {len(test_cases)} Scenario/Scenario Outline blocks across all files — count them before finishing.
  Do NOT invent additional scenarios, do NOT split one test case into several scenarios.
- Map each scenario to the REQUIREMENTS list above: tag with EVERY @req-<ID> it verifies
- Cover as many requirements from the list as the test cases allow — spread tags accurately, never invent coverage
- Tag the primary happy-path scenario of each Feature with @smoke
- Use Scenario Outline + Examples for any test case that tests multiple data inputs
- Extract exact error messages, field validations, and status codes from the Context section for Then steps
- Add Background: block if 2+ scenarios in a Feature share the same Given step

IMPORTANT: NEVER use 'General.feature' or 'Core.feature' as a filename.
Always use the specific functional module name (e.g. Authentication.feature, ShoppingCart.feature).

Return each file using this EXACT delimiter (no deviation):
=== FILE: ModuleName.feature ===
[complete feature file content]

Generate all feature files now."""

        self.logger.info("Calling LLM to generate feature files...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=6000)

        if response:
            self.logger.info(f"LLM returned {len(response)} chars for feature files")
            files = self._parse_files(response, '.feature')
            return self._split_general_features(files)
        else:
            self.logger.warning("LLM returned no response for feature files")
            return []

    def _format_requirements(self, requirements: List[Dict[str, Any]]) -> str:
        if not requirements:
            return "(no requirements list provided — derive @req tags from test case references)"
        lines = []
        for req in requirements:
            rid = req.get('requirement_id', 'REQ-?')
            text = req.get('feature') or req.get('requirement') or req.get('description') or ''
            rules = req.get('business_rules') or []
            lines.append(f"{rid}: {text}")
            for rule in rules[:3]:
                lines.append(f"    - {rule}")
        return "\n".join(lines)

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

    def _split_general_features(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """If a file is named General/Core, split it into module-specific files by Feature: blocks."""
        result = []
        for f in files:
            fname = f.get('filename', '')
            if re.match(r'(?i)(general|core|corefunctionality)', fname.replace('.feature', '')):
                result.extend(self._split_by_feature_blocks(f.get('content', '')))
            else:
                result.append(f)
        return result if result else files

    def _split_by_feature_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Split a multi-Feature Gherkin string into one file per Feature: block."""
        blocks = re.split(r'(?=^Feature:)', content, flags=re.MULTILINE)
        files = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            m = re.match(r'Feature:\s*(.+)', block)
            if not m:
                continue
            module_name = re.sub(r'[^\w]', '', m.group(1).strip().title().replace(' ', ''))
            if not module_name:
                module_name = 'Feature'
            files.append({
                "feature_id": str(uuid.uuid4()),
                "feature_name": module_name,
                "filename": f"{module_name}.feature",
                "content": block,
            })
        return files or [{
            "feature_id": str(uuid.uuid4()),
            "feature_name": "CoreFunctionality",
            "filename": "CoreFunctionality.feature",
            "content": content,
        }]
