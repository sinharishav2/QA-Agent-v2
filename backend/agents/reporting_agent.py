from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
from datetime import datetime


class ReportingAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReportingAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['execution_results', 'project_id']):
                raise ValueError("Missing required input fields")

            project_id = input_data['project_id']
            execution_results = input_data['execution_results']

            html_report = self._generate_html_report(execution_results)
            json_report = self._generate_json_report(execution_results)
            summary = self._generate_summary(execution_results)

            output_data = {
                "project_id": project_id,
                "html_report": html_report,
                "json_report": json_report,
                "summary": summary,
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Reports generated for project {project_id}")

            return output_data

        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_html_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(results)
        passed = len([r for r in results if r.get('status') == 'passed'])
        failed = len([r for r in results if r.get('status') == 'failed'])
        skipped = len([r for r in results if r.get('status') == 'skipped'])

        return {
            "report_id": str(uuid.uuid4()),
            "filename": f"test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html",
            "title": "Test Execution Report",
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_percentage": round((passed / total * 100) if total > 0 else 0, 2)
            },
            "test_details": results,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_json_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(results)
        passed = len([r for r in results if r.get('status') == 'passed'])
        failed = len([r for r in results if r.get('status') == 'failed'])

        return {
            "report_id": str(uuid.uuid4()),
            "filename": f"test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
            "execution_summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "skipped": len([r for r in results if r.get('status') == 'skipped']),
                "success_rate": round((passed / total * 100) if total > 0 else 0, 2)
            },
            "test_results": results,
            "generated_timestamp": datetime.utcnow().isoformat()
        }

    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(results)
        passed = len([r for r in results if r.get('status') == 'passed'])
        failed = len([r for r in results if r.get('status') == 'failed'])
        skipped = len([r for r in results if r.get('status') == 'skipped'])

        failed_tests = [r for r in results if r.get('status') == 'failed']
        execution_times = [r.get('execution_time', 0) for r in results]

        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "success_rate": round((passed / total * 100) if total > 0 else 0, 2),
            "average_execution_time": round(sum(execution_times) / len(execution_times) if execution_times else 0, 2),
            "total_execution_time": round(sum(execution_times), 2),
            "failed_test_details": [
                {
                    "test_id": t.get('test_id'),
                    "scenario": t.get('scenario'),
                    "error": t.get('error', 'Unknown error')
                }
                for t in failed_tests
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
