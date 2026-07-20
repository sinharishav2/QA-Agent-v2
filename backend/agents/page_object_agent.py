from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import re
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are a Principal SDET specialising in enterprise Java Selenium Page Object Model frameworks.
Generate production-grade Java Page Object classes that are immediately compilable and maintainable.

MANDATORY CODING STANDARDS:
1. package pages;
2. Every class MUST extend BasePage (from package pages)
3. Private @FindBy WebElement fields only — never expose elements publicly
4. Locator priority order: By.id > By.name > By.cssSelector > By.xpath
5. All @FindBy XPath must be RELATIVE (start with //) and NOT absolute paths
6. Avoid brittle locators like //div[1] or long absolute XPaths
7. Prefer CSS selectors like input[name='email'], button[type='submit'], .error-message
8. Public action methods: camelCase verbs (enterEmail, clickLogin, selectCategory)
9. Methods return void for terminal actions, or the next Page class for navigation
10. Use BasePage.waitForElementVisible() and BasePage.waitForElementClickable() for all interactions
11. Include a Javadoc comment on every public method
12. PageFactory.initElements(driver, this) in the constructor
13. All required Java imports must be at the top — NO wildcard imports
14. No TODO comments, no placeholder implementations, every method must be real code
15. Return ONLY Java source code, no prose, no markdown fences"""


class PageObjectAgent(BaseAgent):
    def __init__(self):
        super().__init__("PageObjectAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases', 'project_id']):
                raise ValueError("Missing required input fields")

            test_cases = input_data['test_cases']
            project_id = input_data['project_id']
            document_content = input_data.get('document_content', '')

            page_objects = self._generate_page_objects(test_cases, document_content)

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
            self.logger.error(f"Page object generation failed: {str(e)}", exc_info=True)
            return {"page_objects": [], "total_pages": 0, "status": "failed", "error": str(e)}

    def _generate_page_objects(self, test_cases: List[Dict[str, Any]], document_content: str) -> List[Dict[str, Any]]:
        pages_needed = sorted(set(tc.get('module', 'Core') for tc in test_cases if tc.get('module')))
        test_actions_text = "\n".join([
            f"  [{tc.get('test_id','?')}] {tc.get('scenario','')}: {' | '.join(tc.get('steps', []))}"
            for tc in test_cases
        ])

        user_prompt = f"""Generate Java Selenium Page Object classes for the application described below.

APPLICATION CONTEXT:
{document_content[:4000]}

UI INTERACTIONS NEEDED (derived from test cases):
{test_actions_text}

PAGES TO GENERATE:
Create one Page class per logical UI page/screen. Based on the test cases, identify pages such as:
{', '.join(p + 'Page' for p in pages_needed) if pages_needed else 'LoginPage, RegistrationPage, DashboardPage, ProductPage, CartPage, CheckoutPage'}

Also generate:
- BasePage.java (package pages) — contains: WebDriver driver, WebDriverWait wait, constructor, helper methods:
  waitForElementVisible(By), waitForElementClickable(By), getText(WebElement), isElementPresent(By)

For each application page:
- Identify all interactive elements from the context (input fields, buttons, links, error messages, headings)
- Map each element to the most stable locator (prefer id, then name, then CSS selector)
- Create one action method per user interaction

Return each file using this EXACT delimiter:
=== FILE: ClassName.java ===
[complete compilable Java class]

Generate BasePage.java first, then all application page classes."""

        self.logger.info("Calling LLM to generate page objects...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=6000)

        if response:
            self.logger.info(f"LLM returned {len(response)} chars for page objects")
            return self._parse_java_files(response)
        else:
            self.logger.warning("LLM returned no response for page objects")
            return []

    def _parse_java_files(self, response: str) -> List[Dict[str, Any]]:
        files = []
        parts = re.split(r'=== FILE: (.+?) ===', response)
        i = 1
        while i < len(parts) - 1:
            filename = parts[i].strip()
            content = parts[i + 1].strip()
            if content:
                class_name = filename.replace('.java', '')
                files.append({
                    "page_id": str(uuid.uuid4()),
                    "class_name": class_name,
                    "page_name": class_name,
                    "filename": filename if filename.endswith('.java') else filename + '.java',
                    "content": content
                })
            i += 2

        if not files and response.strip():
            files.append({
                "page_id": str(uuid.uuid4()),
                "class_name": "GeneratedPage",
                "page_name": "GeneratedPage",
                "filename": "GeneratedPage.java",
                "content": response.strip()
            })

        return files
