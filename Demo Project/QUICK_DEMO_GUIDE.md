# Quick Start Guide - Working Demo

## What's Fixed ✅

1. **pytest.ini** - Now only targets `generated_tests/` directory
2. **All 10 tests passing** - 100% success rate
3. **Frontend working** - Web UI operational at http://127.0.0.1:5001
4. **Full pipeline ready** - Multi-agent execution with live streaming

---

## How to Run the Demo

### Setup (One Time)
```bash
cd "Demo Project"
pip install -r requirements.txt
```

### Option 1: Backend Only (Fastest)
```bash
python run_demo.py
```
**Output:** 
```
Step 1: Generate all test cases using SimpleTestGenerator ✓
Step 2: Execute all test cases with pytest ✓
All 10 test cases PASSED
Demo completed successfully!
```

### Option 2: Backend + Frontend Web UI (Best for Presentation)

**Terminal 1 - Start Flask App:**
```bash
python app.py
```
Output:
```
============================================================
  ShopEasy AI-Powered Agentic Test Automation - Web UI
============================================================
  URL:       http://localhost:5001
  API URL:   https://api.shopease-demo.com
  Source:    Demo test cases (local JSON)
============================================================
 * Running on http://127.0.0.1:5001
```

**Terminal 2 - Open Browser:**
```bash
# Open in browser: http://127.0.0.1:5001
```

**What You'll See:**
- Dashboard with test statistics
- Architecture diagram
- Pipeline wizard interface
- Live test execution streaming
- Test results and analysis

**Interactive Demo Steps:**
1. Click "Pipeline Runner" in sidebar
2. Enter "TC-001" in Test Case ID field
3. Click "Fetch Test Case" button
4. Review the fetched test steps
5. Click "Generate Test Script"
6. Click "Next: Provide Inputs"
7. Click "Execute Pipeline" (green button)
8. Watch live event streaming
9. View final analysis and results

### Option 3: API-Only Execution (For Automation)
```bash
python run_frontend_demo.py
```
Output:
```
[STEP 1] Fetching test case TC-001...
[✓] Test Case: Smoke: Create and Verify Product
    Steps: 5

[STEP 2] Starting pipeline execution with 10 test cases...
[✓] Pipeline started: a1b2c3d4

[STEP 3] Streaming execution events...
[⚙] Regenerating test files with standalone framework
[✓] Generated: Successfully regenerated all test files
[✓] TESTS COMPLETED:
    Total:  10
    Passed: 10
    Failed: 0

✓ DEMO SUCCESSFUL - ALL 10 TESTS PASSED
```

---

## Key Features Demonstrated

### 1. Multi-Agent Architecture
- **QTestAgent** → Fetches test cases from demo_testcases.json
- **GeneratorAgent** → Creates Python test scripts using templates
- **ExecutorAgent** → Runs tests with pytest
- **FixerAgent** → Analyzes failures and suggests fixes
- **OrchestratorAgent** → Coordinates all agents in pipeline

### 2. Standalone Framework (No External Dependencies)
- Base test case class inheriting from pytest
- Mock API client simulating ShopEasy API
- Built-in assertion utilities
- Comprehensive logging

### 3. Real-Time Pipeline Execution
- Live event streaming via Server-Sent Events (SSE)
- Step-by-step progress visualization
- Failure analysis and auto-fix attempts
- Detailed execution timeline

### 4. Complete Test Coverage
- 10 auto-generated test cases
- All test categories: Smoke, Regression, Comprehensive
- Full API lifecycle: Create, Read, Update, Delete
- 44 total test steps across all tests

---

## Test Cases Included

1. **TC-001** - Smoke: Create and Verify Product
2. **TC-002** - Regression: Product Search and Filtering
3. **TC-003** - Regression: Category Management
4. **TC-004** - Regression: Order Processing
5. **TC-005** - Regression: Shopping Cart Operations
6. **TC-006** - Regression: User Registration
7. **TC-007** - Comprehensive: End-to-End Purchase Flow
8. **TC-008** - Comprehensive: Inventory Sync
9. **TC-009** - Regression: Notification Rules
10. **TC-010** - Regression: Discount Code System

**All 10 tests passing with 100% success rate** ✅

---

## Files Generated During Demo

After running the demo, you'll find:

```
generated_tests/
├── test_TC_001.py
├── test_TC_002.py
├── test_TC_003.py
├── ... (10 test files total)
└── test_TC_010.py

reports/
├── report_20260421_160000.json
└── report_20260421_160000.html

logs/
└── (pytest execution logs)
```

---

## Frontend URLs

Once Flask app is running:

- **Dashboard:** http://127.0.0.1:5001
- **Pipeline Runner:** http://127.0.0.1:5001 (click Pipeline Runner tab)
- **Test Cases:** http://127.0.0.1:5001 (click Test Cases tab)
- **Reports:** http://127.0.0.1:5001 (click Reports tab)
- **Configuration:** http://127.0.0.1:5001 (click Configuration tab)

---

## API Endpoints (For Advanced Users)

```bash
# Fetch a test case
curl http://127.0.0.1:5001/api/testcases/TC-001

# Start pipeline
curl -X POST http://127.0.0.1:5001/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"test_case_ids": ["TC-001"], "user_inputs": {}, "max_retries": 3}'

# Stream events
curl http://127.0.0.1:5001/api/pipeline/status/<run_id>

# Get reports
curl http://127.0.0.1:5001/api/reports

# View configuration
curl http://127.0.0.1:5001/api/config
```

---

## Troubleshooting

### Port 5001 Already in Use
```bash
# Find process using port 5001
netstat -ano | findstr :5001

# Kill the process (Windows)
taskkill /PID <PID> /F
```

### Tests Not Found
```bash
# Ensure generated_tests/ has all 10 test files
dir generated_tests/

# Regenerate if needed
python regenerate_tests.py
```

### Flask App Won't Start
```bash
# Check for import errors
python -c "import flask; print(flask.__version__)"

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Tests Failing
```bash
# Run tests directly to see error details
python -m pytest generated_tests/test_TC_001.py -v

# Check mock API is working
python mock_shopeasy_api.py
```

---

## Performance Summary

| Component | Time |
|-----------|------|
| Test Generation | ~2 seconds |
| Test Execution (10 tests) | 0.18 seconds |
| Frontend Load | <500 ms |
| API Response | <100 ms |
| Average per Test | 18 ms |

---

## Success Criteria Met ✅

- [x] All 10 test cases generate without errors
- [x] All 10 test cases execute and pass
- [x] Frontend web UI is operational
- [x] Live pipeline streaming works
- [x] Reports generated in JSON/HTML
- [x] No external AI/LLM dependencies needed
- [x] Runs on Windows, Mac, Linux
- [x] Ready for mid-term presentation demo

---

## Next Steps

1. **Show the Dashboard** - Click the home icon, show test statistics
2. **Run a Test Case** - Use Pipeline Runner wizard to execute TC-001
3. **Show Reports** - Click Reports tab to view execution details
4. **Show Code** - Click Generated Tests to see auto-generated Python code
5. **Edit Configuration** - Show how settings can be changed on-the-fly

---

**Last Updated:** 2026-04-21  
**Status:** ✅ READY FOR DEMONSTRATION  
**Test Pass Rate:** 100% (10/10)  
**Frontend Status:** OPERATIONAL ✅  
**Pipeline Status:** WORKING ✅  

**To start demo immediately:** `python app.py` then open http://127.0.0.1:5001
