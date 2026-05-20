# Slack-Based Conversational AI DevOps Assistant - AIOps Demo Project

## Overview

This is a demonstration project for a Slack-based conversational AI assistant that enables DevOps and SRE teams to manage cloud services through natural language. Built with an NLP engine, FastAPI orchestration, and integrations to Prometheus and Kubernetes, it automates monitoring and alerting with secure role-based access control and comprehensive audit logging for cloud environments.

### Key Features

- **Conversational NLP Engine**: Processes natural language commands for cloud resource management
- **Cloud Automation**: Automates Kubernetes deployments, scaling, and orchestration tasks
- **Monitoring & Alerting**: Integrates with Prometheus for real-time metrics and intelligent alerting
- **Role-Based Access Control**: Enforces RBAC policies ensuring secure team-based operations
- **Audit Logging**: Comprehensive logging of all actions with compliance and security tracking
- **Slack Integration**: Native Slack bot for seamless team communication and DevOps workflows
- **AIOps Enhancement**: Improves agility, reliability, and operational efficiency in cloud environments

## Architecture

The system uses a multi-agent architecture:

1. **NLPParserAgent**: Processes Slack messages and extracts intent with natural language understanding
2. **CloudOrchestratorAgent**: Plans and executes cloud automation tasks across Kubernetes clusters
3. **MonitoringAgent**: Queries Prometheus and manages alerting rules dynamically
4. **RBACEnforcementAgent**: Validates user permissions and enforces role-based access policies
5. **AuditLoggingAgent**: Records all operations for compliance, security, and troubleshooting

**Integrated Framework:**
The system includes a cloud integration framework (`cloud_automation.py`) that:
- Provides Kubernetes API client wrapper for cluster management
- Includes Prometheus query interface for metrics retrieval
- Manages RBAC configurations and permission validation
- Maintains comprehensive audit trails with timestamps and user tracking

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Slack workspace with admin access for bot installation
- Kubernetes cluster access (local or cloud)

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

### Starting the AIOps Assistant (Recommended for Demo)

**For the mid-term demo, we recommend using the integrated framework directly via command line:**

**Option 1: Quick Demo Script**
```bash
py run_demo.py
```

This script automatically:
- Initializes Slack bot connection
- Connects to Kubernetes cluster
- Establishes Prometheus connection
- Demonstrates conversational commands
- Displays audit logging and RBAC validation

**Option 2: Manual Steps**
```bash
# Start the NLP engine and Slack bot
py agents/nlp_parser_agent.py

# Initialize cloud orchestration
py agents/cloud_orchestrator_agent.py

# Activate monitoring integration
py agents/monitoring_agent.py
```

This approach:
- ✅ Uses the integrated cloud framework
- ✅ All cloud operations execute successfully
- ✅ Real-time Slack notifications enabled
- ✅ RBAC and audit logging active for security

### Running Web Dashboard (Live Monitoring)

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

**Access the dashboard:** `http://localhost:5001`

## Usage

### Demo Mode (Default)

The system runs in demo mode by default, which:
- Simulates Slack workspace integration for testing
- Connects to demo Kubernetes cluster with safe operations
- Uses mock Prometheus metrics for demonstration
- Applies RBAC policies without affecting production
- Logs all operations for audit trail verification

### Example Slack Commands

Once deployed, DevOps teams use natural language commands in Slack:

```
@DevOpsBot deploy latest application-name to staging
@DevOpsBot what is the CPU usage of production cluster
@DevOpsBot create alert for pod crashes exceeding 5 per hour
@DevOpsBot rollback last deployment to previous version
@DevOpsBot scale deployment api-service to 10 replicas
```

The NLP engine interprets intent, validates RBAC permissions, and executes cloud operations automatically with full audit logging.

### Monitoring & Alerting

The Monitoring Agent provides:
- Real-time Prometheus integration for metrics collection
- Intelligent alert generation based on thresholds
- Historical trend analysis for capacity planning
- Automatic incident notifications to Slack

### Security & Compliance

- **RBAC Enforcement**: Role-based access control ensures only authorized teams perform operations
- **Audit Logging**: Complete action history with timestamps, users, and operation details
- **Compliance Tracking**: Meet regulatory requirements with comprehensive operation logs
- **Secure Integration**: Encrypted connections to Kubernetes and Prometheus APIs

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

The web interface includes a **Git Operations** page for managing version control directly from the browser.

#### Setup: GitHub Authentication

To use push operations, you need to configure your GitHub Personal Access Token (PAT):

**Step 1: Generate a GitHub PAT**
1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "Test Automation")
4. Select scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub workflows)
5. Copy the generated token (you won't be able to see it again)

**Step 2: Configure the Token in the Web UI**
1. Click on "Configuration" in the sidebar
2. Scroll to the "Git Configuration" section
3. Paste your token in the "GitHub Personal Access Token" field
4. Update "Project Repository URL" if needed (default: your fork/repo)
5. Click "Save Changes"

#### Features

- **Git Status**: View current repository status (modified, staged, untracked files)
- **Git Add**: Stage all changes for commit
- **Git Pull**: Pull latest changes from a specified branch
- **Git Commit**: Commit staged changes with a custom message
- **Git Push**: Push committed changes to a specified branch
  - Automatically creates the branch if it doesn't exist
  - Requires GitHub token for authentication

#### Usage

1. Navigate to the "Git Operations" page in the sidebar
2. Enter the branch name you want to work with (e.g., `feature/new-tests`)
3. For commits, enter a descriptive commit message
4. Click the appropriate button:
   - **📊 Git Status**: See what files have changed
   - **➕ Git Add**: Stage all changes
   - **⬇️ Git Pull**: Pull latest from remote branch
   - **✓ Git Commit**: Create a commit with your message
   - **⬆️ Git Push**: Push to remote (requires token)
5. View the output/results below

#### Example Workflow

```
1. Click "📊 Git Status" → See your changes
2. Click "➕ Git Add" → Stage all files
3. Enter commit message → Click "✓ Git Commit" → Committed!
4. Enter branch name "feature/my-update" → Click "⬆️ Git Push" → Branch created and pushed!
5. Go to GitHub → Create a Pull Request from your branch to main
```

#### Troubleshooting

**Error: "GitHub token not configured"**
- Go to Configuration → Git Configuration
- Add your GitHub PAT in the "GitHub Personal Access Token" field
- Click "Save Changes"

**Error: "failed to push some refs"**
- Ensure your token has `repo` scope permissions
- Check that the target repository URL is correct
- Verify you have push access to the repository

**Error: "src refspec does not match"**
- The branch name may contain special characters
- Try using a simpler branch name (e.g., `feature-update` instead of `usr/r_c/test1`)
- Git branch names should only contain alphanumeric, hyphens, underscores, dots, and slashes

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
