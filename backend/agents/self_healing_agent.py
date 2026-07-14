from .base_agent import BaseAgent
from typing import Dict, Any, List


class SelfHealingAgent(BaseAgent):
    def __init__(self):
        super().__init__("SelfHealingAgent")
        self.healing_strategies = [
            "locator_update",
            "timeout_adjustment",
            "retry_logic",
            "dom_change_detection"
        ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['failed_tests', 'locators']):
                raise ValueError("Missing required input fields")

            failed_tests = input_data['failed_tests']
            locators = input_data['locators']

            healed_tests = self._heal_failures(failed_tests, locators)

            output_data = {
                "healed_tests": healed_tests,
                "total_healed": len([t for t in healed_tests if t['healed']]),
                "healing_strategies_used": self._get_strategies_used(healed_tests),
                "status": "completed"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Self-healing completed: {output_data['total_healed']} tests healed")

            return output_data

        except Exception as e:
            self.logger.error(f"Self-healing failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _heal_failures(self, failed_tests: List[Dict[str, Any]], locators: Dict[str, Any]) -> List[Dict[str, Any]]:
        healed = []

        for test in failed_tests:
            healing_result = {
                "test_id": test.get('test_id'),
                "original_error": test.get('error', ''),
                "healed": False,
                "healing_strategy": None,
                "new_locator": None,
                "adjusted_timeout": None
            }

            if "locator" in test.get('error', '').lower() or "element not found" in test.get('error', '').lower():
                healing_result = self._heal_broken_locator(test, locators, healing_result)
            elif "timeout" in test.get('error', '').lower():
                healing_result = self._heal_timeout_issue(test, healing_result)
            elif "stale element" in test.get('error', '').lower():
                healing_result = self._heal_stale_element(test, healing_result)

            healed.append(healing_result)

        return healed

    def _heal_broken_locator(self, test: Dict[str, Any], locators: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        page = test.get('page', '')
        element = test.get('element', '')

        if page in locators and element in locators[page]:
            alternative_locator = locators[page][element]
            result['healed'] = True
            result['healing_strategy'] = 'locator_update'
            result['new_locator'] = alternative_locator
            self.logger.info(f"Healed broken locator for {element} on {page}")

        return result

    def _heal_timeout_issue(self, test: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        original_timeout = test.get('timeout', 10)
        adjusted_timeout = original_timeout * 1.5

        result['healed'] = True
        result['healing_strategy'] = 'timeout_adjustment'
        result['adjusted_timeout'] = adjusted_timeout
        self.logger.info(f"Adjusted timeout from {original_timeout}s to {adjusted_timeout}s")

        return result

    def _heal_stale_element(self, test: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        result['healed'] = True
        result['healing_strategy'] = 'retry_logic'
        result['retry_count'] = 3
        self.logger.info(f"Added retry logic for stale element in test {test.get('test_id')}")

        return result

    def _get_strategies_used(self, healed_tests: List[Dict[str, Any]]) -> List[str]:
        strategies = set()
        for test in healed_tests:
            if test.get('healing_strategy'):
                strategies.add(test['healing_strategy'])
        return list(strategies)
