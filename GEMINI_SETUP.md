# Gemini API Integration Setup

This guide explains how to set up Google Gemini API for the QA AI Automation Platform.

## Prerequisites

- Google account
- Access to Google Cloud Console

## Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click on "Create API Key"
3. Select or create a Google Cloud project
4. Copy your API key

## Step 2: Configure Environment Variable

1. Open `backend/.env` file
2. Replace `your_google_api_key` with your actual API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

3. Save the file

## Step 3: Install Dependencies

The required package is already in `pyproject.toml`:

```bash
pip install google-generativeai>=0.3.0
```

Or if using `uv`:

```bash
uv pip install google-generativeai>=0.3.0
```

## Step 4: Verify Installation

Test the Gemini client by running:

```bash
cd backend
python -c "from utils.gemini_client import gemini_client; print('Gemini client initialized successfully')"
```

## How It Works

The Gemini integration is used in the following agents:

### 1. **Requirement Extraction Agent**
- Analyzes functional specification documents
- Extracts requirements and business rules
- Uses Gemini to intelligently parse complex documents

### 2. **Test Case Extraction Agent**
- Parses test case documents
- Extracts test scenarios, steps, and expected results
- Leverages Gemini for intelligent test case identification

### 3. **BDD Generator Agent**
- Converts test cases to Gherkin feature files
- Uses Gemini to generate natural language scenarios

### 4. **Page Object Agent**
- Generates page object models
- Creates locators and interaction methods
- Uses Gemini to structure code properly

### 5. **Step Definition Agent**
- Generates step definitions from feature files
- Creates implementation code
- Uses Gemini for code generation

### 6. **Test Data Agent**
- Generates realistic test data
- Creates positive and negative test scenarios
- Uses Gemini for intelligent data generation

### 7. **Automation Framework Agent**
- Recommends best automation framework
- Provides setup instructions
- Uses Gemini for framework selection logic

## API Limits

Google Gemini API has the following limits (as of 2024):

- **Free tier**: 60 requests per minute
- **Paid tier**: Higher limits available

For production use, consider upgrading to a paid plan.

## Troubleshooting

### Issue: "API key not configured"

**Solution**: Ensure `GOOGLE_API_KEY` is set in `.env` file and the backend is restarted.

### Issue: "Quota exceeded"

**Solution**: You've hit the API rate limit. Wait a few minutes before retrying.

### Issue: "Invalid API key"

**Solution**: Double-check your API key in the `.env` file. Make sure there are no extra spaces or characters.

### Issue: Gemini client not initialized

**Solution**: Check the logs for detailed error messages. Ensure the `google-generativeai` package is installed.

## Features Enabled by Gemini

With Gemini API configured, the platform can:

✅ Intelligently parse complex documents
✅ Extract requirements and test cases automatically
✅ Generate production-ready test code
✅ Create BDD feature files
✅ Generate page object models
✅ Create step definitions
✅ Generate realistic test data
✅ Recommend automation frameworks

## Performance Tips

1. **Batch Processing**: Process multiple documents in sequence to stay within rate limits
2. **Caching**: Consider caching Gemini responses for similar documents
3. **Temperature Settings**: Lower temperature (0.3) for extraction, higher (0.7) for generation

## Next Steps

1. Set up your Gemini API key
2. Restart the backend server
3. Upload your 3 input files (feature spec, test cases, expected output)
4. Generate automation code
5. Download the generated test scripts

## Support

For issues with Gemini API:
- [Google AI Studio Help](https://support.google.com/ai-studio)
- [Gemini API Documentation](https://ai.google.dev/docs)

For issues with the QA AI Platform:
- Check the logs in `backend/logs/`
- Review the error messages in the UI
