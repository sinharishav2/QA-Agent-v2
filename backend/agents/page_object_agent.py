from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid


class PageObjectAgent(BaseAgent):
    def __init__(self):
        super().__init__("PageObjectAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases', 'project_id']):
                raise ValueError("Missing required input fields")

            test_cases = input_data['test_cases']
            project_id = input_data['project_id']

            page_objects = self._generate_page_objects(test_cases)

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
            self.logger.error(f"Page object generation failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_page_objects(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        page_objects = []
        
        pages = {
            "LoginPage": self._create_login_page(),
            "DashboardPage": self._create_dashboard_page(),
            "FormPage": self._create_form_page(),
            "ResultsPage": self._create_results_page()
        }

        for page_name, page_obj in pages.items():
            page_objects.append(page_obj)

        return page_objects

    def _create_login_page(self) -> Dict[str, Any]:
        return {
            "page_id": str(uuid.uuid4()),
            "page_name": "LoginPage",
            "elements": {
                "username_field": {"id": "username", "type": "input"},
                "password_field": {"id": "password", "type": "input"},
                "login_button": {"id": "loginBtn", "type": "button"},
                "error_message": {"xpath": "//div[@class='error-message']", "type": "label"}
            },
            "methods": [
                "enterUsername(username)",
                "enterPassword(password)",
                "clickLoginButton()",
                "getErrorMessage()",
                "isLoginPageDisplayed()"
            ]
        }

    def _create_dashboard_page(self) -> Dict[str, Any]:
        return {
            "page_id": str(uuid.uuid4()),
            "page_name": "DashboardPage",
            "elements": {
                "welcome_message": {"xpath": "//h1[@class='welcome']", "type": "label"},
                "logout_button": {"id": "logoutBtn", "type": "button"},
                "user_menu": {"css": ".user-menu", "type": "dropdown"},
                "main_content": {"id": "mainContent", "type": "div"}
            },
            "methods": [
                "getWelcomeMessage()",
                "clickLogout()",
                "selectUserMenu(option)",
                "isDashboardDisplayed()"
            ]
        }

    def _create_form_page(self) -> Dict[str, Any]:
        return {
            "page_id": str(uuid.uuid4()),
            "page_name": "FormPage",
            "elements": {
                "form_title": {"xpath": "//h2[@class='form-title']", "type": "label"},
                "first_name": {"id": "firstName", "type": "input"},
                "last_name": {"id": "lastName", "type": "input"},
                "email": {"id": "email", "type": "input"},
                "submit_button": {"id": "submitBtn", "type": "button"},
                "cancel_button": {"id": "cancelBtn", "type": "button"}
            },
            "methods": [
                "enterFirstName(name)",
                "enterLastName(name)",
                "enterEmail(email)",
                "clickSubmit()",
                "clickCancel()",
                "isFormDisplayed()"
            ]
        }

    def _create_results_page(self) -> Dict[str, Any]:
        return {
            "page_id": str(uuid.uuid4()),
            "page_name": "ResultsPage",
            "elements": {
                "results_table": {"id": "resultsTable", "type": "table"},
                "success_message": {"xpath": "//div[@class='success']", "type": "label"},
                "back_button": {"id": "backBtn", "type": "button"},
                "export_button": {"id": "exportBtn", "type": "button"}
            },
            "methods": [
                "getResultsCount()",
                "getSuccessMessage()",
                "clickBack()",
                "clickExport()",
                "isResultsPageDisplayed()"
            ]
        }
