from .base_agent import BaseAgent
from typing import Dict, Any, List


class CodeReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("CodeReviewAgent")
        self.naming_standards = {
            "class": "PascalCase",
            "method": "camelCase",
            "variable": "snake_case",
            "constant": "UPPER_SNAKE_CASE"
        }
        self.solid_principles = [
            "Single Responsibility",
            "Open/Closed",
            "Liskov Substitution",
            "Interface Segregation",
            "Dependency Inversion"
        ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['generated_scripts', 'project_id']):
                raise ValueError("Missing required input fields")

            project_id = input_data['project_id']
            generated_scripts = input_data['generated_scripts']

            review_results = self._review_code(generated_scripts)

            output_data = {
                "project_id": project_id,
                "review_results": review_results,
                "total_issues": len(review_results),
                "status": "reviewed"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Code review completed: {len(review_results)} issues found")

            return output_data

        except Exception as e:
            self.logger.error(f"Code review failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _review_code(self, scripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []

        for script in scripts:
            script_issues = {
                "script_name": script.get('name', 'Unknown'),
                "naming_violations": self._check_naming_standards(script),
                "solid_violations": self._check_solid_principles(script),
                "code_smells": self._check_code_smells(script),
                "reusability_issues": self._check_reusability(script),
                "duplicate_logic": self._check_duplicates(script)
            }
            issues.append(script_issues)

        return issues

    def _check_naming_standards(self, script: Dict[str, Any]) -> List[str]:
        violations = []
        content = script.get('content', '')
        
        if 'class ' in content:
            violations.append("Ensure class names follow PascalCase")
        if 'def ' in content:
            violations.append("Ensure method names follow camelCase")
        
        return violations

    def _check_solid_principles(self, script: Dict[str, Any]) -> List[str]:
        violations = []
        content = script.get('content', '')
        
        if len(content) > 500:
            violations.append("Class/Method may violate Single Responsibility Principle")
        if 'global ' in content:
            violations.append("Avoid global variables - violates Dependency Inversion")
        
        return violations

    def _check_code_smells(self, script: Dict[str, Any]) -> List[str]:
        smells = []
        content = script.get('content', '')
        
        if content.count('if ') > 5:
            smells.append("High cyclomatic complexity - consider refactoring")
        if 'TODO' in content or 'FIXME' in content:
            smells.append("Contains TODO/FIXME comments")
        if '# ' in content and content.count('# ') > 10:
            smells.append("Excessive comments - code should be self-documenting")
        
        return smells

    def _check_reusability(self, script: Dict[str, Any]) -> List[str]:
        issues = []
        content = script.get('content', '')
        
        if 'hardcoded' in content.lower():
            issues.append("Contains hardcoded values - reduce reusability")
        if 'magic number' in content.lower():
            issues.append("Contains magic numbers - use named constants")
        
        return issues

    def _check_duplicates(self, script: Dict[str, Any]) -> List[str]:
        duplicates = []
        content = script.get('content', '')
        
        lines = content.split('\n')
        if len(lines) != len(set(lines)):
            duplicates.append("Potential duplicate code blocks detected")
        
        return duplicates
