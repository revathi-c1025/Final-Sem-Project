# Demo Execution Guide - Complete Setup and Run Instructions

This guide provides step-by-step instructions to run the AI-Powered Agentic Test Automation System demo on a completely fresh system with no prior installation.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Running the Demo](#running-the-demo)
5. [Expected Output](#expected-output)
6. [Troubleshooting](#troubleshooting)
7. [Demo Script Details](#demo-script-details)

---

## System Requirements

### Hardware Requirements
- **Processor**: Any modern CPU (Intel i3/AMD Ryzen 3 or better)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: Minimum 500MB free space
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Software Requirements
- **Python**: Version 3.8 or higher (3.9+ recommended)
- **Internet Connection**: Required only for initial dependency installation
- **Administrator Rights**: May be required for Python installation

---

## Pre-Installation Checklist

Before starting, verify your system:

### For Windows Users
1. Open Command Prompt (cmd) or PowerShell
2. Check if Python is installed:
   ```cmd
   python --version
   ```
   or
   ```cmd
   py --version
   ```
3. If Python is not installed, proceed to [Python Installation](#python-installation)

### For macOS Users
1. Open Terminal (Cmd + Space, type "Terminal")
2. Check if Python is installed:
   ```bash
   python3 --version
   ```
3. If Python is not installed, proceed to [Python Installation](#python-installation)

### For Linux Users
1. Open Terminal (Ctrl + Alt + T)
2. Check if Python is installed:
   ```bash
   python3 --version
   ```
3. If Python is not installed, proceed to [Python Installation](#python-installation)

---

## Step-by-Step Setup

### Step 1: Python Installation (If Not Already Installed)

#### Windows Installation

1. **Download Python:**
   - Visit: https://www.python.org/downloads/
   - Download the latest Python 3.x installer (recommended: 3.11 or 3.12)
   - Choose "Windows installer (64-bit)" for most modern systems

2. **Install Python:**
   - Run the downloaded installer
   - **CRITICAL**: Check the box "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close" when done

3. **Verify Installation:**
   ```cmd
   py --version
   ```
   You should see output like: `Python 3.12.0`

#### macOS Installation

1. **Install Homebrew (if not already installed):**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python using Homebrew:**
   ```bash
   brew install python
   ```

3. **Verify Installation:**
   ```bash
   python3 --version
   ```
   You should see output like: `Python 3.12.0`

#### Linux Installation (Ubuntu/Debian)

1. **Update Package List:**
   ```bash
   sudo apt update
   ```

2. **Install Python:**
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

3. **Verify Installation:**
   ```bash
   python3 --version
   ```
   You should see output like: `Python 3.12.0`

---

### Step 2: Obtain the Project Files

1. **Download/Clone the Project:**
   - If you have the project as a ZIP file, extract it to your desired location
   - If using Git, clone the repository:
     ```bash
     git clone <repository-url>
     cd <project-directory>
     ```

2. **Navigate to Project Directory:**
   ```bash
   cd "Demo Project"
   ```
   (Adjust the path if your project folder has a different name)

3. **Verify Project Structure:**
   You should see these key files:
   - `app.py`
   - `config.py`
   - `requirements.txt`
   - `run_demo.py`
   - `standalone_framework.py`
   - `regenerate_tests.py`
   - `simple_test_generator.py`

---

### Step 3: Install Python Dependencies

**QUICK METHOD - Single Command:**

#### Windows
```cmd
pip install -r requirements.txt
```

#### macOS and Linux
```bash
pip3 install -r requirements.txt
```

**That's it!** This single command will install all required packages.

---

**DETAILED METHOD - If you want to see what's being installed:**

See `INSTALLATION.md` for detailed installation instructions and troubleshooting.

The `requirements.txt` file contains:
- Flask 3.0.0 (web framework)
- pytest 7.4.3 (testing framework)
- pytest-html 3.2.0 (HTML reports)
- requests 2.31.0 (HTTP library)
- python-dateutil 2.8.2 (date processing)

**Installation Time:** 2-5 minutes on first run (downloads from internet)

#### Verification

After installation, verify packages are installed:
```cmd
pip list
```

You should see the packages listed above.

---

## Running the Demo

### Option 1: Automated Demo Script (Recommended)

This is the simplest way to run the demo with a single command.

#### Windows

1. **Open Command Prompt or PowerShell**
2. **Navigate to Project Directory:**
   ```cmd
   cd "C:\path\to\Demo Project"
   ```
3. **Run Demo Script:**
   ```cmd
   py run_demo.py
   ```

#### macOS and Linux

1. **Open Terminal**
2. **Navigate to Project Directory:**
   ```bash
   cd /path/to/Demo\ Project
   ```
3. **Run Demo Script:**
   ```bash
   python3 run_demo.py
   ```

---

### Option 2: Manual Step-by-Step Execution

If you prefer to run each step manually for demonstration purposes.

#### Step 1: Generate Test Cases

**Windows:**
```cmd
py regenerate_tests.py
```

**macOS/Linux:**
```bash
python3 regenerate_tests.py
```

**Expected Output:**
```
DEBUG: Python executable: C:\Python312\python.exe
DEBUG: Current working directory: C:\path\to\Demo Project
DEBUG: Script directory: C:\path\to\Demo Project
Regenerating all test files using SimpleTestGenerator...
[OK] Generated TC-001: generated_tests\test_TC_001.py
[OK] Generated TC-002: generated_tests\test_TC_002.py
[OK] Generated TC-003: generated_tests\test_TC_003.py
[OK] Generated TC-004: generated_tests\test_TC_004.py
[OK] Generated TC-005: generated_tests\test_TC_005.py
[OK] Generated TC-006: generated_tests\test_TC_006.py
[OK] Generated TC-007: generated_tests\test_TC_007.py
[OK] Generated TC-008: generated_tests\test_TC_008.py
[OK] Generated TC-009: generated_tests\test_TC_009.py
[OK] Generated TC-010: generated_tests\test_TC_010.py

All test files regenerated successfully!
Run tests with: py -m pytest generated_tests/ -v
```

#### Step 2: Execute Tests

**Windows:**
```cmd
py -m pytest generated_tests/ -v
```

**macOS/Linux:**
```bash
python3 -m pytest generated_tests/ -v
```

**Expected Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.12.0 -- pytest-7.4.3
collected 10 items

generated_tests/test_TC_001.py::TestTC_001::test_tc_001 PASSED      [ 10%]
generated_tests/test_TC_002.py::TestTC_002::test_tc_002 PASSED      [ 20%]
generated_tests/test_TC_003.py::TestTC_003::test_tc_003 PASSED      [ 30%]
generated_tests/test_TC_004.py::TestTC_004::test_tc_004 PASSED      [ 40%]
generated_tests/test_TC_005.py::TestTC_005::test_tc_005 PASSED      [ 50%]
generated_tests/test_TC_006.py::TestTC_006::test_tc_006 PASSED      [ 60%]
generated_tests/test_TC_007.py::TestTC_007::test_tc_007 PASSED      [ 70%]
generated_tests/test_TC_008.py::TestTC_008::test_tc_008 PASSED      [ 80%]
generated_tests/test_TC_009.py::TestTC_009::test_tc_009 PASSED      [ 90%]
generated_tests/test_TC_010.py::TestTC_010::test_tc_010 PASSED      [100%]

============================= 10 passed in 0.19s ==============================
```

#### Step 3: Run Specific Test (Optional)

To run a single test case:

**Windows:**
```cmd
py -m pytest generated_tests/test_TC_001.py -v
```

**macOS/Linux:**
```bash
python3 -m pytest generated_tests/test_TC_001.py -v
```

---

## Expected Output

### Demo Script Output

When you run `py run_demo.py`, you should see:

```
======================================================================
AI-Powered Agentic Test Automation System - Demo
======================================================================

This demo showcases the standalone test framework
which generates and executes test cases without Atlas dependencies.

Recommended for mid-term demo presentation.

======================================================================

======================================================================
Step 1: Generate all test cases using SimpleTestGenerator
======================================================================
Command: py regenerate_tests.py
----------------------------------------------------------------------
[Output from regenerate_tests.py]
[OK] Success

======================================================================
Step 2: Execute all test cases with pytest
======================================================================
Command: py -m pytest generated_tests/ -v
----------------------------------------------------------------------
[Output from pytest]
[OK] Success

======================================================================
Demo Summary
======================================================================
[OK] All 10 test cases generated successfully
[OK] All 10 test cases passed
[OK] Using standalone framework (no Atlas dependencies)
[OK] System is ready for demonstration

Generated test files are in: generated_tests/
Each test uses the standalone framework with mock API client

======================================================================
Demo completed successfully!
======================================================================
```

### Generated Test Files

After running the demo, you will find 10 test files in the `generated_tests/` directory:
- `test_TC_001.py` - Smoke test for product creation
- `test_TC_002.py` - Product search and filtering
- `test_TC_003.py` - Category management
- `test_TC_004.py` - Shopping cart functionality
- `test_TC_005.py` - Order processing
- `test_TC_006.py` - User registration
- `test_TC_007.py` - Product updates
- `test_TC_008.py` - Inventory management
- `test_TC_009.py` - Catalog synchronization
- `test_TC_010.py` - Regression test

Each test file:
- Uses the standalone framework (no Atlas dependencies)
- Imports from `standalone_framework.py`
- Uses mock API client for ShopEasy simulation
- Can be executed independently with pytest

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Python is not recognized"

**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
- Windows: Use `py` instead of `python`
- Mac/Linux: Use `python3` instead of `python`
- Reinstall Python and ensure "Add to PATH" is checked

#### Issue 2: "No module named 'pytest'"

**Symptom:**
```
ModuleNotFoundError: No module named 'pytest'
```

**Solution:**
```bash
pip install pytest
```
or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

#### Issue 3: "Permission denied"

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
- Windows: Run Command Prompt as Administrator
- Mac/Linux: Use `sudo` before the command
- Check file permissions on the project directory

#### Issue 4: "Port already in use" (if using web UI)

**Symptom:**
```
OSError: [WinError 10048] Address already in use
```

**Solution:**
- Change the port in `app.py` from 5001 to 5002
- Or close the application using port 5001

#### Issue 5: Import errors for standalone framework

**Symptom:**
```
ModuleNotFoundError: No module named 'standalone_framework'
```

**Solution:**
- Ensure you're in the correct project directory
- The test files automatically add the parent directory to Python path
- Verify `standalone_framework.py` exists in the project root

#### Issue 6: Tests fail with assertion errors

**Symptom:**
```
FAILED - assert_equals failed
```

**Solution:**
- Ensure `mock_shopeasy_api.py` exists in the project directory
- Check that the mock API is running correctly
- Verify all dependencies are installed

#### Issue 7: Slow test execution

**Symptom:**
Tests take more than 30 seconds to complete

**Solution:**
- This is unusual for this demo (should complete in <5 seconds)
- Check system resources (CPU, RAM)
- Close other applications
- Restart the system if needed

---

## Demo Script Details

### What the Demo Script Does

The `run_demo.py` script performs the following steps:

1. **Initializes the demo environment**
   - Sets up logging and display formatting
   - Displays introduction and purpose

2. **Step 1: Test Generation**
   - Calls `regenerate_tests.py`
   - Uses SimpleTestGenerator to create all 10 test cases
   - Displays generation progress for each test case
   - Reports success or failure

3. **Step 2: Test Execution**
   - Runs pytest on all generated tests
   - Displays detailed test output
   - Shows pass/fail status for each test
   - Reports overall success or failure

4. **Summary**
   - Displays final results
   - Confirms all tests passed
   - Shows framework information
   - Provides location of generated files

### Customization Options

You can modify the demo behavior by editing `run_demo.py`:

**To run specific test cases only:**
```python
# Change this line in run_demo.py:
py -m pytest generated_tests/ -v
# To:
py -m pytest generated_tests/test_TC_001.py generated_tests/test_TC_002.py -v
```

**To show more verbose output:**
```python
# Add -s flag to show print statements:
py -m pytest generated_tests/ -v -s
```

**To generate HTML report:**
```python
# Add --html flag:
py -m pytest generated_tests/ -v --html=report.html
```

---

## Quick Reference Commands

### Windows
```cmd
# Check Python version
py --version

# Install dependencies
py -m pip install -r requirements.txt

# Run demo
py run_demo.py

# Manual test generation
py regenerate_tests.py

# Manual test execution
py -m pytest generated_tests/ -v

# Run specific test
py -m pytest generated_tests/test_TC_001.py -v
```

### macOS/Linux
```bash
# Check Python version
python3 --version

# Install dependencies
pip3 install -r requirements.txt

# Run demo
python3 run_demo.py

# Manual test generation
python3 regenerate_tests.py

# Manual test execution
python3 -m pytest generated_tests/ -v

# Run specific test
python3 -m pytest generated_tests/test_TC_001.py -v
```

---

## Verification Checklist

After completing the setup, verify:

- [ ] Python 3.8+ is installed
- [ ] All dependencies from requirements.txt are installed
- [ ] `regenerate_tests.py` runs without errors
- [ ] All 10 test files are generated in `generated_tests/`
- [ ] `pytest` runs without errors
- [ ] All 10 tests pass
- [ ] Demo script completes successfully
- [ ] Generated test files use standalone framework
- [ ] No Atlas framework imports in test files

---

## Additional Resources

### Project Documentation
- `README.md` - Main project documentation
- `KNOWN_ISSUES.md` - Known limitations and workarounds
- `DEMO_PREPARATION.md` - Demo preparation details

### Key Project Files
- `standalone_framework.py` - Standalone test framework
- `simple_test_generator.py` - Test generation logic
- `regenerate_tests.py` - Test generation script
- `mock_shopeasy_api.py` - Mock API for ShopEasy simulation

### Test Files
- `generated_tests/` - Directory containing all generated test cases
- Each test file is independent and can be run separately

---

## Support and Contact

If you encounter issues not covered in this guide:

1. Check the error message carefully
2. Review the troubleshooting section above
3. Verify all steps in the setup process
4. Ensure Python and all dependencies are correctly installed
5. Check that you're in the correct project directory

---

## Next Steps After Demo

After successfully running the demo:

1. **Review Generated Tests**
   - Open `generated_tests/test_TC_001.py` to see the test structure
   - Examine how the standalone framework is used
   - Review the mock API calls

2. **Customize Test Cases**
   - Edit `demo_testcases.json` to add new test cases
   - Run `regenerate_tests.py` to generate new tests
   - Execute with pytest

3. **Explore the Framework**
   - Read `standalone_framework.py` to understand the architecture
   - Review `simple_test_generator.py` for generation logic
   - Examine agent implementations in `agents/` directory

---

## System Cleanup (Optional)

If you want to remove the demo after presentation:

### Windows
```cmd
# Delete project directory
rmdir /s /q "Demo Project"

# Uninstall Python packages (optional)
py -m pip freeze > packages.txt
py -m pip uninstall -r packages.txt -y
```

### macOS/Linux
```bash
# Delete project directory
rm -rf Demo\ Project

# Uninstall Python packages (optional)
pip3 freeze > packages.txt
pip3 uninstall -r packages.txt -y
```

---

**End of Demo Execution Guide**

For questions or issues, refer to the project documentation or contact the development team.
