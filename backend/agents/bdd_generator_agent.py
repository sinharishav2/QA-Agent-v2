from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid


class BDDGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("BDDGeneratorAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases', 'project_id']):
                raise ValueError("Missing required input fields")

            test_cases = input_data['test_cases']
            project_id = input_data['project_id']

            feature_files = self._generate_feature_files(test_cases, project_id)

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
            self.logger.error(f"BDD generation failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_feature_files(self, test_cases: List[Dict[str, Any]], project_id: str) -> List[Dict[str, Any]]:
        feature_files = []
        modules = {}

        for tc in test_cases:
            module = tc.get('module', 'general')
            if module not in modules:
                modules[module] = []
            modules[module].append(tc)

        for module, tests in modules.items():
            feature_file = {
                "feature_id": str(uuid.uuid4()),
                "feature_name": f"{module.replace('_', ' ').title()} Feature",
                "filename": f"{module}.feature",
                "scenarios": self._generate_scenarios(tests),
                "background": self._generate_background()
            }
            feature_files.append(feature_file)

        return feature_files

    def _generate_scenarios(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scenarios = []
        for tc in test_cases:
            scenario = {
                "scenario_id": str(uuid.uuid4()),
                "scenario_name": tc.get('scenario', 'Test Scenario'),
                "given": self._generate_given_steps(tc),
                "when": self._generate_when_steps(tc),
                "then": self._generate_then_steps(tc)
            }
            scenarios.append(scenario)
        return scenarios

    def _generate_background(self) -> Dict[str, Any]:
        return {
            "given": [
                "User is on the application login page",
                "Browser is initialized with required capabilities"
            ]
        }

    def _generate_given_steps(self, test_case: Dict[str, Any]) -> List[str]:
        steps = test_case.get('preconditions', [])
        if not steps:
            steps = ["User is logged in", "Application is ready"]
        return steps

    def _generate_when_steps(self, test_case: Dict[str, Any]) -> List[str]:
        steps = test_case.get('steps', [])
        if not steps:
            steps = ["User performs the action"]
        return steps

    def _generate_then_steps(self, test_case: Dict[str, Any]) -> List[str]:
        steps = test_case.get('expected_results', [])
        if not steps:
            steps = ["Expected result is achieved"]
        return steps
