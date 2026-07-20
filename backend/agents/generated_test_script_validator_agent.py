import json
import re
from collections import Counter
from typing import Any, Dict, List

from .base_agent import BaseAgent
from utils.openai_client import openai_client

SYSTEM_PROMPT = (
    "You are a Principal QA Automation Architect and code auditor. "
    "You receive a static analysis report and code samples from a generated Java Selenium + Cucumber project. "
    "Evaluate automation readiness and return a JSON quality scorecard. "
    "Return ONLY a valid JSON object — no markdown, no explanation, no code fences."
)


class GeneratedTestScriptValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("GeneratedTestScriptValidatorAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            feature_files    = input_data.get("feature_files", [])
            page_objects     = input_data.get("page_objects", [])
            step_definitions = input_data.get("step_definitions", [])
            utilities        = input_data.get("utilities", {})
            requirements     = input_data.get("requirements", [])
            test_cases       = input_data.get("test_cases", [])

            static_report = self._static_analysis(feature_files, page_objects, step_definitions, utilities)
            scores = self._llm_validate(feature_files, page_objects, step_definitions, static_report, requirements, test_cases)

            output_data = {"validation_score": scores, "status": "validated"}
            self.log_execution(input_data, output_data, status="success")
            return output_data

        except Exception as exc:
            self.logger.error(f"Validation failed: {exc}", exc_info=True)
            return {"validation_score": self._default_scores(), "status": "validation_failed", "error": str(exc)}

    # ------------------------------------------------------------------
    # Deterministic static analysis
    # ------------------------------------------------------------------

    def _static_analysis(
        self,
        feature_files: List[Dict],
        page_objects: List[Dict],
        step_definitions: List[Dict],
        utilities: Dict,
    ) -> Dict[str, Any]:
        report: Dict[str, Any] = {}

        # --- Feature file analysis ---
        all_feature_text = "\n".join(f.get("content", "") for f in feature_files)
        scenarios        = re.findall(r"^\s*(?:Scenario|Scenario Outline):", all_feature_text, re.MULTILINE)
        scenario_outline = re.findall(r"^\s*Scenario Outline:", all_feature_text, re.MULTILINE)
        smoke_tags       = re.findall(r"@smoke", all_feature_text, re.IGNORECASE)
        regression_tags  = re.findall(r"@regression", all_feature_text, re.IGNORECASE)
        req_tags         = re.findall(r"@req-\w+", all_feature_text, re.IGNORECASE)
        then_steps       = re.findall(r"^\s*Then\s+.+", all_feature_text, re.MULTILINE)
        vague_then       = [s for s in then_steps if re.search(r"\bshould\s+(be\s+)?(visible|present|displayed)\b", s, re.IGNORECASE)]

        report["gherkin"] = {
            "total_feature_files": len(feature_files),
            "total_scenarios": len(scenarios),
            "scenario_outlines": len(scenario_outline),
            "smoke_tagged": len(smoke_tags),
            "regression_tagged": len(regression_tags),
            "req_traced_tags": len(req_tags),
            "vague_then_steps": len(vague_then),
            "has_background": "Background:" in all_feature_text,
        }

        # --- Page object analysis ---
        all_po_text   = "\n".join(p.get("content", "") for p in page_objects)
        thread_sleep  = len(re.findall(r"Thread\.sleep", all_po_text))
        brittle_xpath = len(re.findall(r'@FindBy\s*\([^)]*xpath\s*=\s*"(?!//)(?!.*\$)', all_po_text))
        todo_count    = len(re.findall(r"//\s*TODO", all_po_text, re.IGNORECASE))
        base_page_ext = len(re.findall(r"extends\s+BasePage", all_po_text))
        div_xpath     = len(re.findall(r'xpath\s*=\s*"//div(?!\[@)', all_po_text))

        report["page_objects"] = {
            "total_classes": len(page_objects),
            "extends_base_page": base_page_ext,
            "thread_sleep_usages": thread_sleep,
            "brittle_absolute_xpath": brittle_xpath,
            "generic_div_xpath": div_xpath,
            "todo_comments": todo_count,
        }

        # --- Step definition analysis ---
        all_step_text  = "\n".join(s.get("content", "") for s in step_definitions)
        step_patterns  = re.findall(r'@(?:Given|When|Then)\s*\("([^"]+)"\)', all_step_text)
        dup_steps      = [p for p, c in Counter(step_patterns).items() if c > 1]
        assert_calls   = len(re.findall(r"Assert\.", all_step_text))
        no_assert_then = len(re.findall(r'@Then\s*\("', all_step_text)) - assert_calls

        report["step_definitions"] = {
            "total_classes": len(step_definitions),
            "total_step_patterns": len(step_patterns),
            "duplicate_steps": dup_steps,
            "assert_calls": assert_calls,
            "then_steps_without_assert": max(0, no_assert_then),
        }

        # --- Utility coverage ---
        util_keys = list(utilities.keys()) if isinstance(utilities, dict) else []
        expected_utils = {"DriverFactory", "BasePage", "Hooks", "TestRunner", "ConfigReader"}
        missing_utils  = expected_utils - set(util_keys)
        has_pom        = "pom" in util_keys

        report["utilities"] = {
            "generated": util_keys,
            "missing_core": list(missing_utils),
            "has_pom_xml": has_pom,
        }

        return report

    # ------------------------------------------------------------------
    # LLM-based evaluation
    # ------------------------------------------------------------------

    def _llm_validate(
        self,
        feature_files: List[Dict],
        page_objects: List[Dict],
        step_definitions: List[Dict],
        static_report: Dict[str, Any],
        requirements: List[Dict],
        test_cases: List[Dict],
    ) -> Dict[str, Any]:

        req_coverage = (
            static_report["gherkin"]["req_traced_tags"] / max(len(requirements), 1) * 100
        )

        context_parts = [
            f"STATIC ANALYSIS FINDINGS:\n{json.dumps(static_report, indent=2)}",
            f"REQUIREMENT COVERAGE: {req_coverage:.0f}% ({static_report['gherkin']['req_traced_tags']} of {len(requirements)} requirements traced via @req-* tags)",
            f"SCENARIO COUNT vs TEST CASE COUNT: {static_report['gherkin']['total_scenarios']} scenarios generated from {len(test_cases)} test cases",
        ]

        if feature_files:
            context_parts.append(f"FEATURE FILE SAMPLE:\n{feature_files[0].get('content','')[:1200]}")
        if page_objects:
            context_parts.append(f"PAGE OBJECT SAMPLE:\n{page_objects[0].get('content','')[:1200]}")
        if step_definitions:
            context_parts.append(f"STEP DEFINITION SAMPLE:\n{step_definitions[0].get('content','')[:1200]}")

        context = "\n\n".join(context_parts)

        user_prompt = f"""Evaluate this generated Java Selenium + Cucumber automation project.
Use the static analysis findings and code samples to score each dimension.

{context}

Return ONLY this JSON object (all fields required, no extra text):
{{
  "overall_score": <0-100>,
  "gherkin_quality": <0-100>,
  "java_code_quality": <0-100>,
  "step_definition_coverage": <0-100>,
  "page_object_quality": <0-100>,
  "locator_quality": <0-100>,
  "framework_structure": <0-100>,
  "traceability": <0-100>,
  "assertion_quality": <0-100>,
  "maintainability": <0-100>,
  "automation_readiness": <0-100>,
  "requirement_coverage_pct": {req_coverage:.0f},
  "duplicate_steps": {json.dumps(static_report['step_definitions']['duplicate_steps'])},
  "missing_components": <list of strings: missing files, missing tags, missing patterns>,
  "improvement_suggestions": <list of 3-5 specific, actionable suggestions>,
  "critical_issues": <list of blocking issues that must be fixed before running>,
  "summary": "<one sentence overall assessment>"
}}"""

        self.logger.info("Calling LLM for deep artifact validation...")
        response = openai_client.generate_with_system_prompt(
            SYSTEM_PROMPT, user_prompt, max_tokens=1200, temperature=0.1
        )

        if response:
            try:
                match = re.search(r"\{.*\}", response, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                    result.setdefault("static_analysis", static_report)
                    return result
            except Exception as exc:
                self.logger.warning(f"Could not parse LLM validation response: {exc}")

        defaults = self._default_scores()
        defaults["static_analysis"] = static_report
        return defaults

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
            "assertion_quality": 65,
            "maintainability": 70,
            "automation_readiness": 65,
            "requirement_coverage_pct": 0,
            "duplicate_steps": [],
            "missing_components": [],
            "improvement_suggestions": ["Review generated code before execution"],
            "critical_issues": [],
            "summary": "Validation completed with default scores (LLM unavailable).",
        }
