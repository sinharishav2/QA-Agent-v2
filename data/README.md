# Sample Test Data

This folder contains sample input documents for testing the QA AI Automation Platform.

## Files

### 1. **feature_specification.txt**
Complete functional specification for an E-Commerce Platform.

**Contains:**
- Overview and functional requirements
- Business rules
- User workflows
- System constraints
- Acceptance criteria

**Use Case:** Upload as "functional_specification" document type

---

### 2. **test_cases.txt**
Comprehensive test cases for the E-Commerce Platform.

**Contains:**
- 17 test cases across 5 modules
- Test case structure: Title, Priority, Preconditions, Steps, Expected Results
- Modules: Authentication, Product Browsing, Shopping Cart, Checkout, Order Management

**Use Case:** Upload as "test_cases" document type

---

### 3. **expected_output.txt**
Expected outputs and validations for all test cases.

**Contains:**
- HTTP responses for each test
- UI display expectations
- Email notifications
- Error scenarios
- Performance expectations

**Use Case:** Upload as "expected_output" document type

---

## How to Use

### Step 1: Add Gemini API Key

Edit `backend/.env`:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

### Step 2: Start Backend

```powershell
cd backend
python main.py
```

### Step 3: Start Frontend

```powershell
cd frontend
npm run dev
```

### Step 4: Create a Project

1. Open http://localhost:5173
2. Click "New Conversation"
3. Enter project name: "E-Commerce Testing"
4. Click "Create"

### Step 5: Upload Sample Documents

1. Click "Upload Documents"
2. Upload in this order:
   - **feature_specification.txt** → Select "functional_specification"
   - **test_cases.txt** → Select "test_cases"
   - **expected_output.txt** → Select "expected_output"

### Step 6: Generate Automation

1. Click "Generate" button
2. Wait for Gemini to process the documents
3. System will generate:
   - Test scripts
   - Page objects
   - Feature files
   - Step definitions
   - Test data

### Step 7: Download Results

Download from the right panel:
- 📄 Test Scripts
- 📊 Test Report
- 🔧 Configuration
- 📦 Full Package

---

## Expected Output

The system should generate:

```
Generated Files:
├── test_scripts/
│   ├── test_authentication.py
│   ├── test_product_browsing.py
│   ├── test_shopping_cart.py
│   ├── test_checkout.py
│   └── test_order_management.py
├── page_objects/
│   ├── login_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   ├── checkout_page.py
│   └── order_page.py
├── features/
│   ├── authentication.feature
│   ├── product_browsing.feature
│   ├── shopping_cart.feature
│   ├── checkout.feature
│   └── order_management.feature
├── step_definitions/
│   └── steps.py
├── test_data/
│   └── test_data.json
└── config/
    └── config.py
```

---

## Test Coverage

| Module | Test Cases | Coverage |
|--------|-----------|----------|
| Authentication | 5 | 100% |
| Product Browsing | 3 | 100% |
| Shopping Cart | 4 | 100% |
| Checkout | 3 | 100% |
| Order Management | 2 | 100% |
| **Total** | **17** | **100%** |

---

## Key Features Tested

✅ User Registration & Login
✅ Product Search & Browsing
✅ Shopping Cart Management
✅ Checkout Process
✅ Payment Processing
✅ Order Tracking
✅ Error Handling
✅ Input Validation

---

## Troubleshooting

### Issue: "Missing required documents"
**Solution:** Ensure all 3 files are uploaded with correct document types.

### Issue: Gemini API errors
**Solution:** Check your API key in `.env` and verify quota limits.

### Issue: Generated code has issues
**Solution:** Review the expected output document for reference implementations.

---

## Next Steps

1. Review generated test scripts
2. Customize for your specific application
3. Run tests against your application
4. Integrate with CI/CD pipeline
5. Monitor test execution and results

---

## Notes

- These are sample documents for demonstration
- Customize the content based on your actual application
- The generated code is a starting point - refine as needed
- Expected outputs show what the system should generate

---

## Support

For issues or questions:
1. Check the backend logs: `backend/logs/`
2. Review the generated code
3. Verify API key configuration
4. Check Gemini API status

---

**Happy Testing! 🚀**
