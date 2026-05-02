# AI-Powered Agentic Test Automation System - Demo Project

## Overview

This is a demonstration project for an AI-powered agentic test automation system. The system automatically generates executable test scripts from test case descriptions, executes them, and provides intelligent failure analysis and auto-fixing capabilities.

### Key Features

- **Automated Test Generation**: Converts test case descriptions into executable Python test scripts
- **Intelligent Execution**: Runs tests with automatic retry logic and failure analysis
- **Root Cause Analysis**: Classifies failures as script issues, product issues, or environment issues
- **Auto-Fixing**: Automatically attempts to fix script-level failures
- **Web Interface**: Professional web UI for monitoring and managing test automation
- **Portable**: Works on any system without external AI/LLM dependencies (demo mode)

## Architecture

The system uses a multi-agent architecture:

1. **QTestAgent**: Fetches test cases from test management system (local JSON in demo mode)
2. **SimpleTestGenerator**: Generates executable test code using standalone framework (no Atlas dependencies)
3. **TestExecutorAgent**: Executes tests using pytest and captures results
4. **FixerAgent**: Analyzes failures and generates fix strategies
5. **OrchestratorAgent**: Coordinates all agents in the pipeline

**Standalone Framework:**
The system now includes a standalone test framework (`standalone_framework.py`) that:
- Provides mock API client for ShopEasy API simulation
- Includes base test case class and assertion utilities
- Works with standard pytest (no Atlas framework dependencies)
- Is fully self-contained and portable

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this project**

```bash
cd "Demo Project"
```

2. **Install dependencies**

**Quick single command:**
```bash
pip install -r requirements.txt
```

**For detailed installation instructions, see `INSTALLATION.md`**

### Running Tests (Recommended for Demo)

**For the mid-term demo, we recommend using the standalone framework directly via command line:**

**Option 1: Quick Demo Script**
```bash
py run_demo.py
```

This script automatically:
- Generates all 10 test cases using the standalone framework
- Executes all tests with pytest
- Displays a summary of results

**Option 2: Manual Steps**
```bash
# Generate all test cases with standalone framework
py regenerate_tests.py

# Run all tests with pytest
py -m pytest generated_tests/ -v

# Run specific test case
py -m pytest generated_tests/test_TC_001.py -v
```

This approach:
- ✅ Uses the new standalone framework (no Atlas dependencies)
- ✅ All 10 test cases pass successfully
- ✅ No caching issues
- ✅ Simple and reliable for demo

### Running Web Interface (Known Limitations)

**Note:** The web UI has a known framework caching issue (see KNOWN_ISSUES.md for details).

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Or directly with Python:**
```bash
python app.py
```

**Access the web interface:** `http://localhost:5001`

## Usage

### Demo Mode (Default)

The system runs in demo mode by default, which:
- Uses local test case data from `demo_testcases.json`
- Generates tests using template-based generation (no AI required)
- Simulates the ShopEasy API for demonstration
- Works entirely offline

## Git Workflow

To make changes safely, create a child branch from `main`, work there, and push your changes back to the remote repository.

```bash
# 1. Ensure you are on the main branch and up to date
git checkout main
git pull origin main

# 2. Create a new child branch for your work
git checkout -b feature/your-feature-name

# 3. Make your code changes and commit them
git add .
git commit -m "Add requested UI enhancements and Git workflow docs"

# 4. Push the new branch to the remote repository
git push -u origin feature/your-feature-name

# 5. Open a pull request on GitHub from the child branch into main
```

If you need to update the branch later, repeat:

```bash
git add .
git commit -m "Update feature implementation"
git push
```

When your PR is approved, merge it into `main` using GitHub or the command line.

### Git Operations via Web UI

The web interface now includes a **Git Operations** page that provides easy access to common Git commands:

- **Git Status**: View current repository status (modified, staged, untracked files)
- **Git Add**: Stage all changes for commit
- **Git Pull**: Pull latest changes from a specified branch
- **Git Commit**: Commit staged changes with a custom message
- **Git Push**: Push committed changes to a specified branch

**Usage:**
1. Navigate to the "Git Operations" page in the sidebar
2. Enter the branch name you want to work with
3. Enter a commit message if committing changes
4. Use the buttons to perform Git operations
5. View the output in the results area below

**Note:** Git operations require proper authentication for remote repositories. For local development, ensure your Git user identity is configured.

### Running Tests

1. **Fetch Test Cases**: Click "Fetch Test Cases" to load available test cases
2. **Generate Tests**: Select test cases and click "Generate" to create test scripts
3. **Execute Tests**: Click "Run Pipeline" to execute the generated tests
4. **View Results**: Check the reports section for detailed results

### Configuration

Edit `config.py` to customize:
- Test case source (local JSON or qTest)
- API endpoints and credentials
- LLM settings (optional, for AI-powered generation)
- Retry limits and timeouts
- Directory paths

## Project Structure

```
Demo Project/
├── agents/                    # Agent implementations
│   ├── orchestrator_agent.py
│   ├── qtest_agent.py
│   ├── test_generator_agent.py
│   ├── test_executor_agent.py
│   └── fixer_agent.py
├── demo_reference_tests/      # Reference test framework
│   └── shopease_framework/    # ShopEasy test framework
├── generated_tests/           # Auto-generated test scripts
├── logs/                      # Execution logs
├── reports/                   # Test execution reports
├── templates/                 # Web UI templates
│   └── index.html
├── app.py                     # Flask web application
├── config.py                  # Configuration settings
├── demo_testcases.json        # Demo test case data
├── requirements.txt           # Python dependencies
├── run.bat                    # Windows startup script
├── run.sh                     # Linux/Mac startup script
└── README.md                  # This file
```

## Features in Detail

### Test Generation

The system generates test scripts in two modes:
- **Template Mode**: Uses predefined templates based on test case keywords (default)
- **AI Mode**: Uses LLM to generate context-aware test code (requires API key)

### Execution Pipeline

1. **Fetch**: Load test case from source
2. **Generate**: Create executable test script
3. **Execute**: Run the test with pytest
4. **Analyze**: Classify failures if any
5. **Fix**: Attempt to fix script issues
6. **Retry**: Re-execute with fixed code
7. **Report**: Generate comprehensive report

### Failure Classification

- **Script Issues**: Import errors, syntax errors, attribute errors (auto-fixable)
- **Product Issues**: Assertion failures, expected vs actual mismatches
- **Environment Issues**: Connection errors, authentication failures, timeouts

### Reports

The system generates:
- **JSON Reports**: Machine-readable detailed results
- **HTML Reports**: Human-readable summary with pass/fail status
- **Execution Logs**: Detailed logs for each test attempt

## Security Considerations

This demo project:
- Does not use external AI/LLM services by default
- Runs entirely locally without external API calls
- Uses simulated/mock data for demonstration
- Does not store or transmit sensitive information

## Development Workflow - Git Branching

### Creating a Child Branch and Pushing to Main

When working on new features or fixes, follow this Git workflow:

1. **Check Current Status**
   ```bash
   git status
   git branch -a  # See all branches
   ```

2. **Create a New Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # Or for bug fixes:
   git checkout -b bugfix/issue-description
   ```

3. **Make Your Changes**
   ```bash
   # Edit files, add features, fix bugs
   git add .
   git commit -m "Description of changes"
   ```

4. **Push Your Branch to Remote**
   ```bash
   git push -u origin feature/your-feature-name
   ```

5. **Create a Pull Request (PR)**
   - Go to GitHub/GitLab and create a PR from your branch to `main`
   - Add description of changes
   - Request review if needed

6. **Merge to Main (After Review)**
   ```bash
   # After PR is approved and merged via GitHub/GitLab:
   git checkout main
   git pull origin main
   ```

### Branch Naming Conventions
- `feature/feature-name` - New features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes
- `refactor/component-name` - Code refactoring

### Best Practices
- Always create branches from `main`
- Keep branches focused on single features/issues
- Write clear commit messages
- Pull latest changes before starting work
- Delete branches after merging

To enable AI features, you must explicitly configure LLM credentials in `config.py`.

## Troubleshooting

### Known Issues

Please refer to `KNOWN_ISSUES.md` for a list of known limitations and their workarounds, including:
- Web UI framework caching issue
- RAG system memory limitations

### Port Already in Use

If port 5001 is already in use, edit `app.py` and change the port number:

```python
app.run(host="0.0.0.0", port=5002, debug=True, threaded=True, use_reloader=False)
```

### Missing Dependencies

If you encounter import errors, reinstall dependencies:

```bash
pip install -r requirements.txt --force-reinstall
```

### Python Not Found

If `python` command is not found, try:
- Windows: Use `py` command
- Linux/Mac: Use `python3` command

### Logs Not Visible

Logs are stored in the `logs/` directory. You can view them through the web interface under the "Logs" section.

## Advanced Configuration

### Enabling AI Features

To enable AI-powered test generation:

1. Edit `config.py`
2. Set `LLM_API_KEY` to your OpenAI or Azure API key
3. Configure `LLM_PROVIDER` as "openai" or "azure"
4. Set `LLM_MODEL` to your preferred model (e.g., "gpt-4")

### Connecting to Real qTest

To use real qTest instead of demo JSON:

1. Edit `config.py`
2. Set `TESTCASE_SOURCE = "qtest"`
3. Configure `QTEST_BASE_URL` and `QTEST_API_TOKEN`
4. Set `PROJECT_ID` to your qTest project ID

### Custom Test Framework

To use your own test framework:

1. Place your framework in a directory
2. Update `REFERENCE_REPO_LOCAL_PATH` in `config.py`
3. The system will scan your framework for context-aware generation

## Development

### Adding New Test Cases

Edit `demo_testcases.json` to add new test cases following the existing format:

```json
{
  "id": 90001,
  "pid": "TC-001",
  "name": "Test Case Name",
  "description": "Test case description",
  "precondition": "Preconditions",
  "properties": {
    "Automation Status": "",
    "Priority": "High",
    "Type": "Functional"
  },
  "steps": [
    {
      "order": 1,
      "description": "Step description",
      "expected": "Expected result"
    }
  ]
}
```

### Extending Agents

To add custom functionality:
1. Extend the appropriate agent class in `agents/`
2. Implement the required methods
3. Update the `OrchestratorAgent` to use your custom agent

## Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review the configuration in `config.py`
3. Ensure all dependencies are installed
4. Verify Python version (3.8+)

## License

This is a demonstration project for educational purposes.

## Acknowledgments

This project demonstrates agentic AI principles for test automation, inspired by modern AI-powered development tools.
