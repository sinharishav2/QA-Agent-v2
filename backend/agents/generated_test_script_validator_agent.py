import json
import re
from typing import Any, Dict, List

from .base_agent import BaseAgent
from utils.openai_client import openai_client

SYSTEM_PROMPT = (
    "You are a senior QA Automation Architect and code reviewer with 15+ years of experience. "
    "Evaluate the provided Java Selenium + Cucumber BDD automation artifacts and return quality scores. "
    "Return ONLY a valid JSON object — no markdown, no explanation, no code fences."
)


class GeneratedTestScriptValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("GeneratedTestScriptValidatorAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            feature_files = input_data.get("feature_files", [])
            page_objects = input_data.get("page_objects", [])
            step_definitions = input_data.get("step_definitions", [])
            utilities = input_data.get("utilities", {})
            requirements = input_data.get("requirements", [])
            test_cases = input_data.get("test_cases", [])

            scores = self._validate(
                feature_files, page_objects, step_definitions, utilities, requirements, test_cases
            )

            output_data = {"validation_score": scores, "status": "validated"}
            self.log_execution(input_data, output_data, status="success")
            return output_data

        except Exception as exc:
            self.logger.error(f"Validation failed: {exc}", exc_info=True)
            return {"validation_score": self._default_scores(), "status": "validation_failed", "error": str(exc)}

    # ------------------------------------------------------------------

    def _validate(
        self,
        feature_files: List[Dict],
        page_objects: List[Dict],
        step_definitions: List[Dict],
        utilities: Dict,
        requirements: List[Dict],
        test_cases: List[Dict],
    ) -> Dict[str, Any]:

        parts: List[str] = []

        parts.append(
            f"ARTIFACT COUNTS:\n"
            f"- Feature Files: {len(feature_files)}\n"
            f"- Page Objects: {len(page_objects)}\n"
            f"- Step Definitions: {len(step_definitions)}\n"
            f"- Utilities: {len(utilities) if isinstance(utilities, dict) else 0} "
            f"({', '.join(utilities.keys()) if isinstance(utilities, dict) else ''})\n"
            f"- Requirements: {len(requirements)}\n"
            f"- Test Cases: {len(test_cases)}"
        )

        if feature_files:
            sample = feature_files[0].get("content", "")[:1500]
            parts.append(f"=== FEATURE FILE SAMPLE ===\n{sample}")

        if page_objects:
            sample = page_objects[0].get("content", "")[:1500]
            parts.append(f"=== PAGE OBJECT SAMPLE ===\n{sample}")

        if step_definitions:
            sample = step_definitions[0].get("content", "")[:1500]
            parts.append(f"=== STEP DEFINITION SAMPLE ===\n{sample}")

        artifact_summary = "\n\n".join(parts)

        user_prompt = (
            f"Evaluate the following generated automation project artifacts:\n\n"
            f"{artifact_summary}\n\n"
            f"Return ONLY this JSON (fill every field, no extra text):\n"
            f'{{\n'
            f'  "overall_score": <0-100>,\n'
            f'  "gherkin_quality": <0-100>,\n'
            f'  "java_code_quality": <0-100>,\n'
            f'  "step_definition_coverage": <0-100>,\n'
            f'  "page_object_quality": <0-100>,\n'
            f'  "locator_quality": <0-100>,\n'
            f'  "framework_structure": <0-100>,\n'
            f'  "traceability": <0-100>,\n'
            f'  "missing_components": ["list", "of", "missing", "items"],\n'
            f'  "improvement_suggestions": ["suggestion 1", "suggestion 2"],\n'
            f'  "summary": "One-sentence overall assessment"\n'
            f"}}"
        )

        self.logger.info("Calling LLM for artifact validation...")
        response = openai_client.generate_with_system_prompt(
            SYSTEM_PROMPT, user_prompt, max_tokens=800, temperature=0.1
        )

        if response:
            try:
                match = re.search(r"\{.*\}", response, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except Exception as exc:
                self.logger.warning(f"Could not parse LLM validation response: {exc}")

        return self._default_scores()

    @staticmethod
    def _default_scores() -> Dict[str, Any]:
        return {
            "overall_score": 70,
            "gherkin_quality": 70,
            "java_code_quality": 70,
            "step_definition_coverage": 70,
            "page_object_quality": 70,
            "locator_quality": 65,
            "framework_structure": 75,
            "traceability": 60,
            "missing_components": [],
            "improvement_suggestions": ["Review generated code before execution"],
            "summary": "Validation completed with default scores (LLM unavailable).",
        }
