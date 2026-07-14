from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid


class StepDefinitionAgent(BaseAgent):
    def __init__(self):
        super().__init__("StepDefinitionAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['feature_files', 'project_id']):
                raise ValueError("Missing required input fields")

            feature_files = input_data['feature_files']
            project_id = input_data['project_id']

            step_definitions = self._generate_step_definitions(feature_files)

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
            self.logger.error(f"Step definition generation failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_step_definitions(self, feature_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        step_definitions = []

        for feature in feature_files:
            scenarios = feature.get('scenarios', [])
            for scenario in scenarios:
                given_steps = scenario.get('given', [])
                when_steps = scenario.get('when', [])
                then_steps = scenario.get('then', [])

                for step in given_steps:
                    step_def = self._create_step_definition(step, "given", feature.get('feature_name'))
                    step_definitions.append(step_def)

                for step in when_steps:
                    step_def = self._create_step_definition(step, "when", feature.get('feature_name'))
                    step_definitions.append(step_def)

                for step in then_steps:
                    step_def = self._create_step_definition(step, "then", feature.get('feature_name'))
                    step_definitions.append(step_def)

        return step_definitions

    def _create_step_definition(self, step_text: str, step_type: str, feature_name: str) -> Dict[str, Any]:
        return {
            "step_id": str(uuid.uuid4()),
            "step_text": step_text,
            "step_type": step_type,
            "feature": feature_name,
            "implementation": self._generate_implementation(step_text, step_type),
            "page_objects_used": self._identify_page_objects(step_text),
            "assertions": self._identify_assertions(step_text)
        }

    def _generate_implementation(self, step_text: str, step_type: str) -> str:
        if step_type == "given":
            return f"@Given(\"{step_text}\")\npublic void {self._to_method_name(step_text)}() {{\n    // Setup preconditions\n}}"
        elif step_type == "when":
            return f"@When(\"{step_text}\")\npublic void {self._to_method_name(step_text)}() {{\n    // Perform action\n}}"
        else:
            return f"@Then(\"{step_text}\")\npublic void {self._to_method_name(step_text)}() {{\n    // Assert expected result\n}}"

    def _to_method_name(self, step_text: str) -> str:
        words = step_text.lower().split()
        method_name = ''.join(word.capitalize() for word in words if word.isalnum())
        return method_name[0].lower() + method_name[1:] if method_name else "step"

    def _identify_page_objects(self, step_text: str) -> List[str]:
        page_objects = []
        if any(word in step_text.lower() for word in ['login', 'username', 'password']):
            page_objects.append("LoginPage")
        if any(word in step_text.lower() for word in ['dashboard', 'welcome', 'logout']):
            page_objects.append("DashboardPage")
        if any(word in step_text.lower() for word in ['form', 'submit', 'enter']):
            page_objects.append("FormPage")
        if any(word in step_text.lower() for word in ['result', 'table', 'export']):
            page_objects.append("ResultsPage")
        return page_objects

    def _identify_assertions(self, step_text: str) -> List[str]:
        assertions = []
        if any(word in step_text.lower() for word in ['displayed', 'shown', 'visible']):
            assertions.append("isDisplayed()")
        if any(word in step_text.lower() for word in ['error', 'message', 'text']):
            assertions.append("getText()")
        if any(word in step_text.lower() for word in ['enabled', 'disabled', 'clickable']):
            assertions.append("isEnabled()")
        return assertions
