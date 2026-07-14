import google.generativeai as genai
from loguru import logger
from config import settings
from typing import Optional

class GeminiClient:
    def __init__(self):
        if not settings.google_api_key:
            logger.warning("Google API key not configured. Gemini features will be unavailable.")
            self.client = None
        else:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.client = True
            logger.info("Gemini client initialized successfully")

    def generate_content(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Generate content using Gemini API"""
        if not self.client:
            logger.error("Gemini client not initialized")
            return None
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=4096,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            return None

    def extract_requirements(self, document_content: str) -> Optional[str]:
        """Extract requirements from a document"""
        prompt = f"""
        Analyze the following document and extract all functional requirements, business rules, and features.
        Format the output as a structured list with requirement IDs, descriptions, and related business rules.
        
        Document:
        {document_content}
        
        Output format:
        REQ-001: [Requirement Description]
        - Business Rule 1
        - Business Rule 2
        """
        return self.generate_content(prompt, temperature=0.3)

    def extract_test_cases(self, document_content: str) -> Optional[str]:
        """Extract test cases from a document"""
        prompt = f"""
        Analyze the following document and extract all test cases.
        For each test case, provide: Test ID, Scenario, Preconditions, Steps, Expected Results, and Priority.
        
        Document:
        {document_content}
        
        Output format:
        TC-001: [Test Case Name]
        Scenario: [Description]
        Preconditions: [List preconditions]
        Steps:
        1. [Step 1]
        2. [Step 2]
        Expected Results: [Expected outcome]
        Priority: [High/Medium/Low]
        """
        return self.generate_content(prompt, temperature=0.3)

    def generate_test_script(self, framework: str, test_cases: str, page_objects: str) -> Optional[str]:
        """Generate test automation script"""
        prompt = f"""
        Generate a complete test automation script in {framework} based on the following:
        
        Test Cases:
        {test_cases}
        
        Page Objects:
        {page_objects}
        
        Requirements:
        - Use {framework} best practices
        - Include proper error handling
        - Add logging statements
        - Use page object model pattern
        - Include assertions for all expected results
        - Add wait strategies for dynamic elements
        
        Generate complete, production-ready code.
        """
        return self.generate_content(prompt, temperature=0.5)

    def generate_page_objects(self, application_description: str, test_cases: str) -> Optional[str]:
        """Generate page object models"""
        prompt = f"""
        Based on the application description and test cases, generate page object models.
        
        Application:
        {application_description}
        
        Test Cases:
        {test_cases}
        
        Requirements:
        - Create separate page classes for each page/screen
        - Include locators as class attributes
        - Add methods for user interactions
        - Use meaningful method names
        - Include proper documentation
        
        Generate complete page object classes.
        """
        return self.generate_content(prompt, temperature=0.5)

    def generate_step_definitions(self, feature_content: str, page_objects: str) -> Optional[str]:
        """Generate BDD step definitions"""
        prompt = f"""
        Generate step definitions for the following feature file and page objects.
        
        Feature File:
        {feature_content}
        
        Page Objects:
        {page_objects}
        
        Requirements:
        - Create step definitions for all steps in the feature file
        - Use the page objects for interactions
        - Include proper assertions
        - Add error handling
        - Use meaningful step implementations
        
        Generate complete step definition code.
        """
        return self.generate_content(prompt, temperature=0.5)

    def generate_feature_file(self, test_cases: str, requirements: str) -> Optional[str]:
        """Generate BDD feature file"""
        prompt = f"""
        Generate a Gherkin feature file based on the following test cases and requirements.
        
        Requirements:
        {requirements}
        
        Test Cases:
        {test_cases}
        
        Requirements:
        - Use Gherkin syntax (Given, When, Then)
        - Create scenarios for each test case
        - Include background steps if applicable
        - Use meaningful scenario names
        - Include proper tags for categorization
        
        Generate a complete feature file.
        """
        return self.generate_content(prompt, temperature=0.5)

    def generate_test_data(self, test_cases: str, data_requirements: str) -> Optional[str]:
        """Generate test data"""
        prompt = f"""
        Generate test data for the following test cases.
        
        Test Cases:
        {test_cases}
        
        Data Requirements:
        {data_requirements}
        
        Requirements:
        - Create realistic test data
        - Include positive and negative test data
        - Add edge cases
        - Format as JSON or CSV
        - Include data descriptions
        
        Generate comprehensive test data.
        """
        return self.generate_content(prompt, temperature=0.5)

    def select_framework(self, application_type: str, requirements: str) -> Optional[str]:
        """Recommend automation framework"""
        prompt = f"""
        Based on the application type and requirements, recommend the best automation framework.
        
        Application Type: {application_type}
        
        Requirements:
        {requirements}
        
        Provide:
        1. Recommended Framework
        2. Justification
        3. Setup instructions
        4. Pros and Cons
        5. Best practices for this framework
        """
        return self.generate_content(prompt, temperature=0.3)

gemini_client = GeminiClient()
