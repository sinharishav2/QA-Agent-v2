from .base_agent import BaseAgent
from typing import Dict, Any
import uuid


class UtilityGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("UtilityGeneratorAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['project_id', 'framework']):
                raise ValueError("Missing required input fields")

            project_id = input_data['project_id']
            framework = input_data['framework']

            utilities = self._generate_utilities(framework)

            output_data = {
                "project_id": project_id,
                "framework": framework,
                "utilities": utilities,
                "total_utilities": len(utilities),
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Utilities generated: {len(utilities)}")

            return output_data

        except Exception as e:
            self.logger.error(f"Utility generation failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_utilities(self, framework: str) -> Dict[str, Dict[str, Any]]:
        utilities = {
            "DriverManager": self._create_driver_manager(framework),
            "ConfigManager": self._create_config_manager(),
            "Logger": self._create_logger(),
            "ScreenshotUtility": self._create_screenshot_utility(),
            "ExcelReader": self._create_excel_reader(),
            "JSONReader": self._create_json_reader(),
            "RetryUtility": self._create_retry_utility(),
            "WaitUtility": self._create_wait_utility(),
            "ReportingUtility": self._create_reporting_utility()
        }
        return utilities

    def _create_driver_manager(self, framework: str) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "DriverManager",
            "description": "Manages WebDriver initialization and teardown",
            "methods": [
                "initializeDriver(browserType)",
                "getDriver()",
                "quitDriver()",
                "maximizeWindow()",
                "setImplicitWait(timeout)"
            ],
            "framework": framework
        }

    def _create_config_manager(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "ConfigManager",
            "description": "Manages configuration properties",
            "methods": [
                "loadProperties(filePath)",
                "getProperty(key)",
                "setProperty(key, value)",
                "getAllProperties()"
            ]
        }

    def _create_logger(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "Logger",
            "description": "Centralized logging utility",
            "methods": [
                "info(message)",
                "warn(message)",
                "error(message)",
                "debug(message)"
            ]
        }

    def _create_screenshot_utility(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "ScreenshotUtility",
            "description": "Captures screenshots on demand or failure",
            "methods": [
                "takeScreenshot(testName)",
                "takeScreenshotOnFailure(testName)",
                "getScreenshotPath()"
            ]
        }

    def _create_excel_reader(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "ExcelReader",
            "description": "Reads test data from Excel files",
            "methods": [
                "readExcel(filePath, sheetName)",
                "getRowData(rowNumber)",
                "getColumnData(columnName)",
                "getRowCount()"
            ]
        }

    def _create_json_reader(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "JSONReader",
            "description": "Reads test data from JSON files",
            "methods": [
                "readJSON(filePath)",
                "getJSONObject(key)",
                "getJSONArray(key)"
            ]
        }

    def _create_retry_utility(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "RetryUtility",
            "description": "Implements retry logic for flaky tests",
            "methods": [
                "retry(action, maxAttempts)",
                "retryOnException(action, exceptionType, maxAttempts)"
            ]
        }

    def _create_wait_utility(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "WaitUtility",
            "description": "Implements explicit waits",
            "methods": [
                "waitForElement(locator, timeout)",
                "waitForElementToBeClickable(locator, timeout)",
                "waitForElementToBeVisible(locator, timeout)",
                "waitForText(locator, text, timeout)"
            ]
        }

    def _create_reporting_utility(self) -> Dict[str, Any]:
        return {
            "utility_id": str(uuid.uuid4()),
            "name": "ReportingUtility",
            "description": "Generates test reports",
            "methods": [
                "startReport(reportName)",
                "logTestStep(stepName, status)",
                "addScreenshot(screenshotPath)",
                "endReport()"
            ]
        }
