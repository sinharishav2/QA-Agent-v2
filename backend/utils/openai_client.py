from loguru import logger
from config import settings
from typing import Optional

try:
    from openai import AzureOpenAI, OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not installed. OpenAI features will be unavailable.")

class OpenAIClient:
    def __init__(self):
        self.client = None
        self.deployment_name = None
        self.is_azure = False

        print(f"[OpenAIClient] INIT - azure_key set: {bool(settings.azure_openai_api_key)}, endpoint set: {bool(settings.azure_openai_endpoint)}, openai_key set: {bool(settings.openai_api_key)}")
        logger.info(f"OpenAIClient init - azure_key: {'SET' if settings.azure_openai_api_key else 'MISSING'}, endpoint: {'SET' if settings.azure_openai_endpoint else 'MISSING'}, deployment: {settings.azure_openai_deployment or 'NOT SET'}")

        # Check if Azure OpenAI is configured
        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            try:
                self.client = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version or "2024-12-01-preview",
                    azure_endpoint=settings.azure_openai_endpoint
                )
                self.deployment_name = settings.azure_openai_deployment or "gpt-4o-mini"
                self.is_azure = True
                logger.info(f"Azure OpenAI client initialized successfully with deployment: {self.deployment_name}")
                print(f"[OpenAIClient] Azure OpenAI initialized OK, deployment={self.deployment_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {str(e)}", exc_info=True)
                print(f"[OpenAIClient] Azure init FAILED: {str(e)}")
                self.client = None

        # Fallback to standard OpenAI
        elif settings.openai_api_key:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.is_azure = False
                logger.info("OpenAI client initialized successfully")
                print("[OpenAIClient] Standard OpenAI initialized OK")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {str(e)}", exc_info=True)
                print(f"[OpenAIClient] Standard OpenAI init FAILED: {str(e)}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured. OpenAI features will be unavailable.")
            print("[OpenAIClient] WARNING: No API key configured - client will be None")

    def _try_reinitialize(self):
        """Lazy re-initialization if client is None"""
        if self.client is not None:
            return
        print("[OpenAIClient] _try_reinitialize called - attempting to create client...")
        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            try:
                self.client = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version or "2024-12-01-preview",
                    azure_endpoint=settings.azure_openai_endpoint
                )
                self.deployment_name = settings.azure_openai_deployment or "gpt-4o-mini"
                self.is_azure = True
                print(f"[OpenAIClient] Re-initialization OK, deployment={self.deployment_name}")
                logger.info(f"Azure OpenAI re-initialized, deployment={self.deployment_name}")
            except Exception as e:
                print(f"[OpenAIClient] Re-initialization FAILED: {e}")
                logger.error(f"Azure OpenAI re-initialization failed: {e}", exc_info=True)
        elif settings.openai_api_key:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.is_azure = False
                print("[OpenAIClient] Re-initialization OK (standard OpenAI)")
            except Exception as e:
                print(f"[OpenAIClient] Re-initialization FAILED: {e}")

    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 4000) -> Optional[str]:
        """Generate content using a system prompt + user prompt"""
        if not self.client:
            self._try_reinitialize()
        if not self.client:
            logger.error("OpenAI client not initialized - check AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env")
            return None
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name if self.is_azure else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content with system prompt: {str(e)}")
            return None

    def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """Generate content using OpenAI API"""
        if not self.client:
            self._try_reinitialize()
        if not self.client:
            logger.error("OpenAI client not initialized - check AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env")
            return None
        
        try:
            if self.is_azure:
                # For Azure, use deployment name
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content with OpenAI: {str(e)}", exc_info=True)
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
        return self.generate_content(prompt, temperature=0.5, max_tokens=4000)

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
        return self.generate_content(prompt, temperature=0.5, max_tokens=3000)

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
        return self.generate_content(prompt, temperature=0.5, max_tokens=3000)

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
        return self.generate_content(prompt, temperature=0.5, max_tokens=2000)

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
        return self.generate_content(prompt, temperature=0.5, max_tokens=2000)

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

openai_client = OpenAIClient()
