#!/usr/bin/env python3
"""Test script to verify Azure OpenAI connection and API key"""

from config import settings
from utils.openai_client import openai_client
import sys

print("=" * 60)
print("AZURE OPENAI CONNECTION TEST")
print("=" * 60)

# Check configuration
print("\n1. Checking Configuration:")
print(f"   - Azure API Key configured: {bool(settings.azure_openai_api_key)}")
print(f"   - Azure Endpoint configured: {bool(settings.azure_openai_endpoint)}")
print(f"   - Endpoint URL: {settings.azure_openai_endpoint}")

# Check client initialization
print("\n2. Checking OpenAI Client:")
if openai_client.client:
    print(f"   ✓ Client initialized successfully")
    print(f"   - Using Azure: {openai_client.is_azure}")
else:
    print(f"   ✗ Client NOT initialized")
    sys.exit(1)

# Test a simple API call
print("\n3. Testing API Call:")
test_prompt = "List 3 test cases for a login feature in JSON format."

try:
    print(f"   Sending test prompt to OpenAI...")
    response = openai_client.generate_content(test_prompt, temperature=0.3, max_tokens=500)
    
    if response:
        print(f"   ✓ API Call Successful!")
        print(f"   Response length: {len(response)} characters")
        print(f"\n   Response Preview:")
        print(f"   {response[:300]}...")
    else:
        print(f"   ✗ API returned empty response")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ API Call Failed: {str(e)}")
    sys.exit(1)

# Test extract_test_cases specifically
print("\n4. Testing Test Case Extraction:")
test_doc = """
Feature: User Login
- Users should be able to login with valid credentials
- Users should see error message with invalid credentials
- Users should be locked after 3 failed attempts

Test Cases:
TC-001: Valid Login
- Username: testuser
- Password: Test@123
- Expected: Login successful

TC-002: Invalid Password
- Username: testuser
- Password: wrong
- Expected: Error message shown
"""

try:
    print(f"   Sending test document to extract_test_cases...")
    response = openai_client.extract_test_cases(test_doc)
    
    if response:
        print(f"   ✓ Test Case Extraction Successful!")
        print(f"   Response length: {len(response)} characters")
        print(f"\n   Response Preview:")
        print(f"   {response[:300]}...")
    else:
        print(f"   ✗ Extraction returned empty response")
        
except Exception as e:
    print(f"   ✗ Extraction Failed: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - Azure OpenAI is working correctly!")
print("=" * 60)
