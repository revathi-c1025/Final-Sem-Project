"""
Configuration for the AI-Powered Agentic Test Automation System (Demo).
Uses ShopEasy E-Commerce Platform as the demo target.

DEMO MODE:
- This configuration is set up for demo mode by default
- No external AI/LLM dependencies required
- Uses local test case data from JSON file
- Template-based test generation (no API keys needed)
- Works entirely offline for demonstration

TO ENABLE AI FEATURES:
- Set LLM_API_KEY to your OpenAI or Azure API key
- Configure LLM_PROVIDER as "openai" or "azure"
- Set LLM_MODEL to your preferred model
"""
import os

# =============================================================================
# Test Case Source Configuration (Demo: local JSON file)
# =============================================================================
TESTCASE_SOURCE = "local"  # "local" for demo JSON, "qtest" for real qTest
TESTCASE_JSON_PATH = os.path.join(os.path.dirname(__file__), "demo_testcases.json")

# qTest settings (unused in demo mode, kept for compatibility)
QTEST_BASE_URL = "https://testmanager.example.com"
QTEST_API_TOKEN = ""
PROJECT_ID = 100
API_VERSION = "v3"

# =============================================================================
# ShopEasy API Configuration (Demo Target System)
# =============================================================================
SHOPEASE_API_URL = os.environ.get("SHOPEASE_API_URL", "https://api.shopease-demo.com")
SHOPEASE_API_KEY = os.environ.get("SHOPEASE_API_KEY", "demo-api-key-12345")
SHOPEASE_ADMIN_USER = os.environ.get("SHOPEASE_ADMIN_USER", "admin")
SHOPEASE_ADMIN_PASS = os.environ.get("SHOPEASE_ADMIN_PASS", "")

# =============================================================================
# AI / LLM Configuration (OPTIONAL - for AI-powered test generation)
# =============================================================================
# NOTE: Leave LLM_API_KEY empty to use template-based generation (demo mode)
# Template mode works offline and requires no external dependencies
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")  # openai, azure, local
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")  # Leave empty for demo mode
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4")  # Used only if LLM_API_KEY is set
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")  # For Azure or local LLM
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "4096"))

# =============================================================================
# Execution Configuration
# =============================================================================
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_DELAY_SECONDS = int(os.environ.get("RETRY_DELAY_SECONDS", "5"))
TEST_TIMEOUT_SECONDS = int(os.environ.get("TEST_TIMEOUT_SECONDS", "300"))

# =============================================================================
# Git Configuration (for version control and repository management)
# =============================================================================
# Project repository information
GIT_PROJECT_REPO_URL = os.environ.get("GIT_PROJECT_REPO_URL", "https://github.com/revathi-c1025/Final-Sem-Project.git")
GIT_PROJECT_TOKEN = os.environ.get("GIT_PROJECT_TOKEN", "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")  # GitHub Personal Access Token
GIT_PROJECT_DEFAULT_BRANCH = os.environ.get("GIT_PROJECT_DEFAULT_BRANCH", "main")

# =============================================================================
# Reference Test Repository (for context-aware code generation)
# =============================================================================
REFERENCE_REPO_LOCAL_PATH = os.environ.get(
    "REFERENCE_REPO_LOCAL_PATH",
    os.path.join(os.path.dirname(__file__), "demo_reference_tests"),
)
GITHUB_REPO_URL = os.environ.get("GITHUB_REPO_URL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

# =============================================================================
# Paths
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
GENERATED_TESTS_DIR = os.path.join(BASE_DIR, "generated_tests")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
