import os
import uuid
import re
from typing import Dict, Any

from .base_agent import BaseAgent
from utils.openai_client import openai_client

SYSTEM_PROMPT = """You are a Principal SDET and Build Engineer specialising in enterprise Java Selenium + Cucumber frameworks.
Generate all infrastructure files needed to run a Maven-based Selenium + Cucumber project out of the box.

MANDATORY REQUIREMENTS:
1. All Java files must compile with Java 11+ — no placeholders, no TODOs
2. pom.xml must use Maven 3.6+ with all required dependencies at exact compatible versions:
   - selenium-java 4.18.1, cucumber-java 7.15.0, cucumber-junit 7.15.0,
     junit 4.13.2, webdrivermanager 5.6.3, log4j-core 2.22.1
3. DriverFactory.java: thread-local WebDriver for parallel execution,
   support Chrome (headless flag from config), configurable base URL
4. BasePage.java: WebDriverWait(20s), helper methods: waitForVisible, waitForClickable,
   getText, isPresent, navigateTo, getPageTitle
5. Hooks.java: @Before starts browser, @After quits browser + takes screenshot on failure via ScreenshotUtils
6. TestRunner.java: @CucumberOptions with features, glue, plugin=[\"pretty\",\"html:target/cucumber-reports/\",\"json:target/cucumber.json\"], tags=\"@smoke\"
7. ConfigReader.java: reads config.properties from classpath, provides getString, getBoolean methods
8. WaitUtils.java: explicit wait strategies — waitForText, waitForUrl, waitForAttributeContains
9. ScreenshotUtils.java: captures full-page screenshot, saves to target/screenshots/<timestamp>.png
10. config.properties: base.url, browser, headless, implicit.wait, explicit.wait
11. cucumber.properties: cucumber.publish.quiet=true, cucumber.ansi-colors.disabled=false
12. Return ONLY file content using the === FILE: === delimiter — no prose"""


class UtilityGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("UtilityGeneratorAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['project_id', 'framework']):
                raise ValueError("Missing required input fields")

            project_id = input_data['project_id']
            framework = input_data['framework']

            utilities = self._generate_framework_files()

            output_data = {
                "project_id": project_id,
                "framework": framework,
                "utilities": utilities,
                "total_utilities": len(utilities),
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Framework utilities generated: {len(utilities)}")
            return output_data

        except Exception as e:
            self.logger.error(f"Utility generation failed: {str(e)}", exc_info=True)
            return {"utilities": {}, "total_utilities": 0, "status": "failed", "error": str(e)}

    FILE_PATH_MAP = {
        "pom.xml":              "",
        "config.properties":    "src/test/resources",
        "cucumber.properties":  "src/test/resources",
        "log4j2.xml":           "src/test/resources",
        "DriverFactory.java":   "src/test/java/config",
        "ConfigReader.java":    "src/test/java/config",
        "BasePage.java":        "src/test/java/pages",
        "Hooks.java":           "src/test/java/hooks",
        "TestRunner.java":      "src/test/java/runners",
        "WaitUtils.java":       "src/test/java/utils",
        "ScreenshotUtils.java": "src/test/java/utils",
    }

    def _resolve_path(self, filename: str) -> str:
        base = os.path.splitext(filename)[0] + '.java' if not '.' in filename else filename
        for pattern, path in self.FILE_PATH_MAP.items():
            if filename == pattern:
                return f"{path}/{filename}" if path else filename
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        if ext == 'java':
            return f"src/test/java/utils/{filename}"
        if ext in ('properties', 'xml'):
            return f"src/test/resources/{filename}"
        return filename

    def _generate_framework_files(self) -> Dict[str, Any]:
        user_prompt = """Generate the COMPLETE Maven project infrastructure for a Java Selenium + Cucumber framework.

Generate ALL of the following files in order:
1.  pom.xml                  — Maven project file with ALL dependencies + Surefire plugin config
2.  config.properties         — src/test/resources — base.url, browser, headless, waits
3.  cucumber.properties       — src/test/resources — Cucumber 7.x publish/color settings
4.  DriverFactory.java        — package config — ThreadLocal<WebDriver>, Chrome/Firefox,
                                WebDriverManager, headless flag, browser factory method
5.  ConfigReader.java         — package config — load config.properties from classpath,
                                getString(key, default), getBoolean(key, default) methods
6.  BasePage.java             — package pages — WebDriverWait(20s), waitForVisible(By),
                                waitForClickable(By), getText(WebElement), isPresent(By),
                                navigateTo(String), getPageTitle()
7.  Hooks.java                — package hooks — @Before(order=1) initialise driver,
                                @After(order=1) screenshot on failure + quit driver
8.  TestRunner.java           — package runners — @RunWith(Cucumber.class),
                                @CucumberOptions(features, glue, plugin, tags, monochrome)
9.  WaitUtils.java            — package utils — static helpers: waitForTextPresent,
                                waitForUrlContains, waitForAttributeContains, waitForInvisibility
10. ScreenshotUtils.java      — package utils — TakesScreenshot, saves PNG to
                                target/screenshots/ with ISO timestamp filename

Return each file using this EXACT delimiter (one blank line before each delimiter):
=== FILE: filename.ext ===
[complete file content]

Generate all 10 files. Every Java class must compile. No TODOs."""

        self.logger.info("Calling LLM to generate framework files...")
        response = openai_client.generate_with_system_prompt(SYSTEM_PROMPT, user_prompt, max_tokens=7000)

        utilities = {}
        if response:
            self.logger.info(f"LLM returned {len(response)} chars for framework files")
            parts = re.split(r'=== FILE: (.+?) ===', response)
            i = 1
            while i < len(parts) - 1:
                filename = parts[i].strip()
                content = parts[i + 1].strip()
                if content:
                    name = filename.rsplit('.', 1)[0] if '.' in filename else filename
                    zip_path = self._resolve_path(filename)
                    utilities[name] = {
                        "utility_id": str(uuid.uuid4()),
                        "name": name,
                        "filename": filename if '.' in filename else filename + '.java',
                        "zip_path": zip_path,
                        "content": content
                    }
                i += 2
        else:
            self.logger.warning("LLM returned no response for framework files")

        return utilities
