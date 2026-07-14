from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid


class LocatorIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("LocatorIntelligenceAgent")
        self.locator_priority = ["id", "name", "css", "xpath", "relative_xpath"]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['page_objects', 'project_id']):
                raise ValueError("Missing required input fields")

            page_objects = input_data['page_objects']
            project_id = input_data['project_id']

            locators = self._generate_locators(page_objects)

            output_data = {
                "project_id": project_id,
                "locators": locators,
                "total_locators": len(locators),
                "locator_priority": self.locator_priority,
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Locators generated: {len(locators)}")

            return output_data

        except Exception as e:
            self.logger.error(f"Locator generation failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_locators(self, page_objects: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
        locators = {}

        for page in page_objects:
            page_name = page.get('page_name', 'UnknownPage')
            page_locators = {}
            elements = page.get('elements', {})

            for element_name, element_info in elements.items():
                locator_strategy = self._select_best_locator(element_info)
                page_locators[element_name] = locator_strategy

            locators[page_name] = page_locators

        return locators

    def _select_best_locator(self, element_info: Dict[str, str]) -> Dict[str, str]:
        selected_locator = {
            "strategy": "xpath",
            "value": "//div"
        }

        if 'id' in element_info and element_info['id']:
            selected_locator = {
                "strategy": "id",
                "value": element_info['id'],
                "priority": 1
            }
        elif 'name' in element_info and element_info['name']:
            selected_locator = {
                "strategy": "name",
                "value": element_info['name'],
                "priority": 2
            }
        elif 'css' in element_info and element_info['css']:
            selected_locator = {
                "strategy": "css",
                "value": element_info['css'],
                "priority": 3
            }
        elif 'xpath' in element_info and element_info['xpath']:
            selected_locator = {
                "strategy": "xpath",
                "value": element_info['xpath'],
                "priority": 4
            }

        if 'xpath' in element_info:
            selected_locator['relative_xpath'] = self._generate_relative_xpath(element_info['xpath'])

        return selected_locator

    def _generate_relative_xpath(self, xpath: str) -> str:
        if xpath.startswith('//'):
            return xpath
        return f"//{xpath.split('/')[-1]}"
