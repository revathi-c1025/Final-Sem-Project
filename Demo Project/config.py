"""
Configuration for the Slack-Based Conversational AI DevOps Assistant (AIOps Demo).
Integrates with Kubernetes, Prometheus, and Slack for cloud automation.

DEMO MODE:
- This configuration is set up for demo mode by default
- Simulates Kubernetes cluster operations safely
- Uses mock Prometheus metrics for demonstration
- Slack bot integration in sandbox mode
- RBAC and audit logging enabled for all operations

TO ENABLE PRODUCTION FEATURES:
- Set KUBERNETES_CLUSTER_URL to your actual cluster endpoint
- Configure PROMETHEUS_URL to your metrics server
- Set SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET from your Slack app
- Enable RBAC_ENFORCEMENT and AUDIT_LOGGING for compliance
"""
import os

# =============================================================================
# Slack Integration Configuration (Conversational AI)
# =============================================================================
SLACK_CHANNEL = "devops-automation"  # Primary Slack channel for bot
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "demo-bot-token")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "demo-signing-secret")
NLP_CONFIDENCE_THRESHOLD = float(os.environ.get("NLP_CONFIDENCE_THRESHOLD", "0.75"))

# Kubernetes Configuration (Cloud Orchestration)
# =============================================================================
KUBERNETES_CLUSTER_URL = os.environ.get("KUBERNETES_CLUSTER_URL", "https://localhost:6443")
KUBERNETES_API_TOKEN = os.environ.get("KUBERNETES_API_TOKEN", "demo-k8s-token")
KUBERNETES_NAMESPACE = os.environ.get("KUBERNETES_NAMESPACE", "default")
KUBERNETES_CONTEXT = os.environ.get("KUBERNETES_CONTEXT", "docker-desktop")

# =============================================================================
# Prometheus Configuration (Monitoring & Alerting)
# =============================================================================
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://localhost:9090")
PROMETHEUS_QUERY_TIMEOUT = int(os.environ.get("PROMETHEUS_QUERY_TIMEOUT", "30"))
ALERT_MANAGER_URL = os.environ.get("ALERT_MANAGER_URL", "http://localhost:9093")

# =============================================================================
# AI / NLP Configuration (Natural Language Processing Engine)
# =============================================================================
# NOTE: Leave LLM_API_KEY empty to use rule-based intent detection (demo mode)
# Rule-based mode works offline and requires no external AI dependencies
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")  # openai, azure, local
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")  # Leave empty for demo mode
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4")  # Used only if LLM_API_KEY is set
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")  # For Azure or local LLM
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "4096"))

# =============================================================================
# Security & Compliance Configuration
# =============================================================================
RBAC_ENFORCEMENT = os.environ.get("RBAC_ENFORCEMENT", "true").lower() == "true"
AUDIT_LOGGING = os.environ.get("AUDIT_LOGGING", "true").lower() == "true"
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "demo-encryption-key")
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_DELAY_SECONDS = int(os.environ.get("RETRY_DELAY_SECONDS", "5"))
OPERATION_TIMEOUT_SECONDS = int(os.environ.get("OPERATION_TIMEOUT_SECONDS", "300"))

# =============================================================================
# Git Configuration (for version control and repository management)
# =============================================================================
# Project repository information
GIT_PROJECT_REPO_URL = os.environ.get("GIT_PROJECT_REPO_URL", "https://github.com/revathi-c1025/Final-Sem-Project.git")
GIT_PROJECT_TOKEN = os.environ.get("GIT_PROJECT_TOKEN", "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")  # GitHub Personal Access Token
GIT_PROJECT_DEFAULT_BRANCH = os.environ.get("GIT_PROJECT_DEFAULT_BRANCH", "main")

# =============================================================================
# Reference Cloud Infrastructure Repository
# =============================================================================
REFERENCE_REPO_LOCAL_PATH = os.environ.get(
    "REFERENCE_REPO_LOCAL_PATH",
    os.path.join(os.path.dirname(__file__), "demo_infrastructure"),
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

# =============================================================================
# QTest Integration Configuration
# =============================================================================
QTEST_BASE_URL = os.environ.get("QTEST_BASE_URL", "http://localhost:8080")
PROJECT_ID = os.environ.get("PROJECT_ID", "1")
API_VERSION = os.environ.get("API_VERSION", "v3")

# =============================================================================
# ShopEase API Configuration
# =============================================================================
SHOPEASE_API_URL = os.environ.get("SHOPEASE_API_URL", "http://localhost:5000")
SHOPEASE_API_KEY = os.environ.get("SHOPEASE_API_KEY", "demo-api-key")
SHOPEASE_ADMIN_USER = os.environ.get("SHOPEASE_ADMIN_USER", "admin")
SHOPEASE_ADMIN_PASS = os.environ.get("SHOPEASE_ADMIN_PASS", "admin123")

# =============================================================================
# Test Execution Configuration
# =============================================================================
TEST_TIMEOUT_SECONDS = int(os.environ.get("TEST_TIMEOUT_SECONDS", "300"))
