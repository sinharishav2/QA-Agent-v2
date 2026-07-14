from .base_agent import BaseAgent
from typing import Dict, Any


class AutomationFrameworkAgent(BaseAgent):
    def __init__(self):
        super().__init__("AutomationFrameworkAgent")
        self.supported_frameworks = {
            "java": {
                "language": "Java",
                "version": "21",
                "build_tool": "Maven",
                "test_framework": "TestNG",
                "bdd_framework": "Cucumber",
                "reporting": "Extent Reports",
                "dependencies": ["Selenium 4", "Apache POI", "Jackson"]
            },
            "python": {
                "language": "Python",
                "version": "3.12+",
                "build_tool": "PyTest",
                "test_framework": "PyTest",
                "bdd_framework": "Behave",
                "reporting": "Pytest HTML",
                "dependencies": ["Selenium", "Pandas", "OpenPyXL"]
            }
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['project_id']):
                raise ValueError("Missing required input fields")

            project_id = input_data['project_id']
            preferred_framework = input_data.get('preferred_framework', 'python').lower()

            if preferred_framework not in self.supported_frameworks:
                preferred_framework = 'python'

            selected_framework = self.supported_frameworks[preferred_framework]

            output_data = {
                "project_id": project_id,
                "selected_framework": preferred_framework,
                "framework_details": selected_framework,
                "status": "selected"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Framework selected: {preferred_framework} for project {project_id}")

            return output_data

        except Exception as e:
            self.logger.error(f"Framework selection failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise
