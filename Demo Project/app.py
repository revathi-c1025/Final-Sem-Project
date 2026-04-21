#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web Frontend for the AI-Powered Agentic Test Automation System
==============================================================
Flask application that wraps the existing pipeline with a REST API
and serves a professional single-page frontend for demo / presentation.

Pipeline workflow exposed to the UI:
  Step 1  Fetch test-case steps from test case source (JSON / qTest)
  Step 2  Generate executable pytest script (AI / template)
  Step 3  Collect required user inputs (ShopEasy API, credentials ...)
  Step 4  Execute with user inputs
  Step 5  Analyse failures ->  Script issue  -> auto-fix & retry
                             ->  Product issue -> show expected vs actual

Start:  python app.py
Open:   http://localhost:5000
"""

import json
import os
import queue
import sys
import importlib
import logging
import re
import threading
import time
import uuid
from datetime import datetime

from flask import Flask, render_template, jsonify, request, Response

# ---- project imports -------------------------------------------------------
from config import (
    QTEST_BASE_URL, PROJECT_ID, API_VERSION,
    SHOPEASE_API_URL, SHOPEASE_API_KEY, SHOPEASE_ADMIN_USER, SHOPEASE_ADMIN_PASS,
    LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    MAX_RETRIES, RETRY_DELAY_SECONDS, TEST_TIMEOUT_SECONDS,
    OUTPUT_DIR, LOGS_DIR, GENERATED_TESTS_DIR, REPORTS_DIR, BASE_DIR,
)
from agents.orchestrator_agent import OrchestratorAgent

# RAG System
rag_system = None
# Temporarily disable RAG to debug Flask startup issue
# try:
#     from rag_system import get_rag_system, initialize_rag_with_sample_data
#     rag_system = get_rag_system()
#     initialize_rag_with_sample_data()
#     print("RAG system initialized successfully")
# except Exception as e:
#     print(f"RAG system initialization failed: {e}")
#     rag_system = None

# ---- Flask setup -----------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "agentic-test-auto-demo"

# ---------------------------------------------------------------------------
# Global state for pipeline runs
# ---------------------------------------------------------------------------
_runs = {}          # run_id -> {status, results, events_queue, ...}
_run_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("webapp")


# ===========================================================================
#  Failure analysis helpers - classify as Script / Product / Environment
# ===========================================================================
_SCRIPT_ERRORS = {"import_error", "syntax_error", "attribute_error", "type_error"}
_ENV_ERRORS    = {"connection_error", "ssl_error", "auth_error", "timeout_error"}
_PRODUCT_ERRORS = {"assertion_error"}

def _classify_root_cause(error_type, error_message, traceback_text, stderr):
    """Return (category, detail_dict).

    Categories: 'script_issue', 'product_issue', 'environment_issue', 'unknown'.
    """
    combined = f"{error_type} {error_message} {traceback_text} {stderr}"

    # --- script issue ---
    if "ModuleNotFoundError" in combined or "ImportError" in combined:
        mod = ""
        m = re.search(r"No module named '([^']+)'", combined)
        if m: mod = m.group(1)
        return "script_issue", {
            "sub_type": "import_error",
            "detail": f"Missing module: {mod}" if mod else "Import error in generated script",
            "auto_fixable": True,
        }
    if "SyntaxError" in combined or "IndentationError" in combined:
        loc = ""
        m = re.search(r'File "([^"]+)", line (\d+)', combined)
        if m: loc = f"{m.group(1)}:{m.group(2)}"
        return "script_issue", {
            "sub_type": "syntax_error",
            "detail": f"Syntax/indentation error{(' at ' + loc) if loc else ''}",
            "auto_fixable": True,
        }
    if "AttributeError" in combined:
        m = re.search(r"'(\w+)' object has no attribute '(\w+)'", combined)
        detail = f"{m.group(1)} has no attribute {m.group(2)}" if m else "Attribute error"
        return "script_issue", {
            "sub_type": "attribute_error",
            "detail": detail,
            "auto_fixable": True,
        }
    if "TypeError" in combined and "argument" in combined.lower():
        return "script_issue", {
            "sub_type": "type_error",
            "detail": error_message[:200],
            "auto_fixable": True,
        }

    # --- environment / configuration issue ---
    if "ConnectionError" in combined or "ConnectTimeout" in combined or "ConnectionRefused" in combined:
        return "environment_issue", {
            "sub_type": "connection_error",
            "detail": "Cannot reach the ShopEasy API - check SHOPEASE_API_URL and network",
            "auto_fixable": False,
        }
    if "SSLError" in combined or "CERTIFICATE_VERIFY_FAILED" in combined:
        return "environment_issue", {
            "sub_type": "ssl_error",
            "detail": "SSL certificate verification failed against ShopEasy API",
            "auto_fixable": True,
        }
    if "401" in combined or "403" in combined or "Unauthorized" in combined:
        return "environment_issue", {
            "sub_type": "auth_error",
            "detail": "Authentication failed - check SHOPEASE_API_KEY / credentials",
            "auto_fixable": False,
        }
    if "TimeoutError" in combined or "timeout" in error_type.lower():
        return "environment_issue", {
            "sub_type": "timeout_error",
            "detail": "Test timed out - ShopEasy API operation took too long",
            "auto_fixable": True,
        }

    # --- product issue (assertion = expected vs actual mismatch) ---
    if "AssertionError" in combined or "assert" in combined.lower():
        expected = actual = ""
        m = re.search(r"assert\s+(.+?)\s*==\s*(.+)", combined)
        if m:
            actual = m.group(1).strip()
            expected = m.group(2).strip()
        else:
            m = re.search(r"AssertionError:\s*(.+)", combined)
            if m:
                expected = m.group(1).strip()
        return "product_issue", {
            "sub_type": "assertion_error",
            "detail": error_message[:300],
            "expected": expected,
            "actual": actual,
            "auto_fixable": False,
        }

    return "unknown", {
        "sub_type": "unknown_error",
        "detail": error_message[:300] if error_message else "Unknown failure - see logs",
        "auto_fixable": False,
    }


def _extract_required_inputs(code):
    """Parse generated test code and return a list of required user inputs."""
    inputs = []
    # Look for env var reads
    env_pattern = re.compile(r'os\.environ\.get\(\s*["\'](\w+)["\']')
    found = set(env_pattern.findall(code))
    # Also check the docstring "Required User Inputs" block
    doc_pattern = re.compile(r'- (\w+):\s*(.+)')
    for m in doc_pattern.finditer(code):
        found.add(m.group(1))

    # Group them by category
    groups = {
        "ShopEasy API": [
            {"key": "SHOPEASE_API_URL",    "label": "ShopEasy API URL",       "required": True,  "type": "text",     "default": "https://api.shopease-demo.com"},
            {"key": "SHOPEASE_API_KEY",    "label": "API Key",                "required": True,  "type": "password", "default": "demo-api-key-12345"},
            {"key": "SHOPEASE_ADMIN_USER", "label": "Admin Username",         "required": True,  "type": "text",     "default": "admin"},
            {"key": "SHOPEASE_ADMIN_PASS", "label": "Admin Password",         "required": True,  "type": "password", "default": ""},
        ],
        "Database": [
            {"key": "DB_HOST",          "label": "Database Host",              "required": False, "type": "text",     "default": "localhost"},
            {"key": "DB_PORT",          "label": "Database Port",              "required": False, "type": "number",   "default": "5432"},
            {"key": "DB_NAME",          "label": "Database Name",              "required": False, "type": "text",     "default": "shopease_test"},
            {"key": "DB_USERNAME",      "label": "DB Username",                "required": False, "type": "text",     "default": "postgres"},
            {"key": "DB_PASSWORD",      "label": "DB Password",                "required": False, "type": "password", "default": ""},
        ],
        "Payment Gateway": [
            {"key": "STRIPE_TEST_KEY",  "label": "Stripe Test API Key",       "required": False, "type": "password", "default": ""},
            {"key": "PAYPAL_SANDBOX",   "label": "PayPal Sandbox Mode",       "required": False, "type": "text",     "default": "true"},
        ],
        "Email / Notifications": [
            {"key": "SMTP_HOST",        "label": "SMTP Host",                 "required": False, "type": "text",     "default": ""},
            {"key": "SMTP_PORT",        "label": "SMTP Port",                 "required": False, "type": "number",   "default": "587"},
            {"key": "NOTIFICATION_WEBHOOK", "label": "Webhook URL",           "required": False, "type": "text",     "default": ""},
        ],
    }

    result = []
    for group_name, fields in groups.items():
        relevant = [f for f in fields if f["key"] in found or f.get("required")]
        if relevant:
            result.append({"group": group_name, "fields": relevant})
    return result


# ===========================================================================
#   API  - Configuration (read + edit)
# ===========================================================================

# Full schema for the editable configuration form.
_CONFIG_SCHEMA = [
    # Test Case Source
    {"key": "TESTCASE_SOURCE",     "group": "Test Case Source", "label": "Source (local/qtest)",  "type": "text",     "editable": True},
    {"key": "TESTCASE_JSON_PATH",  "group": "Test Case Source", "label": "JSON File Path",        "type": "text",     "editable": True},
    {"key": "QTEST_BASE_URL",     "group": "Test Case Source", "label": "qTest Base URL",        "type": "text",     "editable": True},
    {"key": "QTEST_API_TOKEN",    "group": "Test Case Source", "label": "qTest API Token",       "type": "password", "editable": True},
    {"key": "PROJECT_ID",         "group": "Test Case Source", "label": "Project ID",            "type": "number",   "editable": True},
    {"key": "API_VERSION",        "group": "Test Case Source", "label": "API Version",           "type": "text",     "editable": True},
    # ShopEasy API
    {"key": "SHOPEASE_API_URL",    "group": "ShopEasy API",  "label": "API URL",             "type": "text",     "editable": True},
    {"key": "SHOPEASE_API_KEY",    "group": "ShopEasy API",  "label": "API Key",             "type": "password", "editable": True},
    {"key": "SHOPEASE_ADMIN_USER", "group": "ShopEasy API",  "label": "Admin Username",      "type": "text",     "editable": True},
    {"key": "SHOPEASE_ADMIN_PASS", "group": "ShopEasy API",  "label": "Admin Password",      "type": "password", "editable": True},
    # LLM
    {"key": "LLM_PROVIDER",    "group": "LLM / AI",  "label": "Provider (openai / azure)", "type": "text",     "editable": True},
    {"key": "LLM_API_KEY",     "group": "LLM / AI",  "label": "API Key",                   "type": "password", "editable": True},
    {"key": "LLM_MODEL",       "group": "LLM / AI",  "label": "Model",                     "type": "text",     "editable": True},
    {"key": "LLM_BASE_URL",    "group": "LLM / AI",  "label": "Base URL (Azure / local)",  "type": "text",     "editable": True},
    {"key": "LLM_TEMPERATURE", "group": "LLM / AI",  "label": "Temperature",               "type": "number",   "editable": True},
    {"key": "LLM_MAX_TOKENS",  "group": "LLM / AI",  "label": "Max Tokens",                "type": "number",   "editable": True},
    # Execution
    {"key": "MAX_RETRIES",          "group": "Execution",  "label": "Max Retries",           "type": "number", "editable": True},
    {"key": "RETRY_DELAY_SECONDS",  "group": "Execution",  "label": "Retry Delay (sec)",     "type": "number", "editable": True},
    {"key": "TEST_TIMEOUT_SECONDS", "group": "Execution",  "label": "Test Timeout (sec)",    "type": "number", "editable": True},
    # Reference Repository
    {"key": "REFERENCE_REPO_LOCAL_PATH", "group": "Reference Repository",  "label": "Local Repo Path",       "type": "text",     "editable": True},
    {"key": "GITHUB_REPO_URL",          "group": "Reference Repository",  "label": "GitHub Repo URL",       "type": "text",     "editable": True},
    {"key": "GITHUB_TOKEN",             "group": "Reference Repository",  "label": "GitHub Token (PAT)",    "type": "password", "editable": True},
    {"key": "GITHUB_BRANCH",            "group": "Reference Repository",  "label": "Branch",                "type": "text",     "editable": True},
    # Paths
    {"key": "OUTPUT_DIR",          "group": "Paths",  "label": "Output Dir",          "type": "text", "editable": True},
    {"key": "LOGS_DIR",            "group": "Paths",  "label": "Logs Dir",            "type": "text", "editable": True},
    {"key": "GENERATED_TESTS_DIR", "group": "Paths",  "label": "Generated Tests Dir", "type": "text", "editable": True},
    {"key": "REPORTS_DIR",         "group": "Paths",  "label": "Reports Dir",         "type": "text", "editable": True},
]


def _read_live_config():
    """Read the current live values from the config module."""
    import config as cfg
    values = {}
    for field in _CONFIG_SCHEMA:
        k = field["key"]
        values[k] = getattr(cfg, k, "")
    return values


@app.route("/api/config")
def api_config():
    """Return current configuration with full schema for the edit form."""
    values = _read_live_config()
    # Build grouped output
    groups = {}
    for field in _CONFIG_SCHEMA:
        g = field["group"]
        if g not in groups:
            groups[g] = []
        val = values.get(field["key"], "")
        groups[g].append({**field, "value": val})
    return jsonify({"groups": groups, "values": values})


@app.route("/api/config", methods=["POST"])
def api_config_save():
    """Save configuration changes."""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    import config as cfg
    config_path = os.path.join(BASE_DIR, "config.py")

    # Read current file content
    with open(config_path, encoding="utf-8") as f:
        content = f.read()

    changed = []
    for field in _CONFIG_SCHEMA:
        k = field["key"]
        if k not in data:
            continue
        new_val = data[k]
        old_val = getattr(cfg, k, None)

        # Skip if unchanged
        if str(new_val) == str(old_val):
            continue

        # Cast to the right type
        if field["type"] == "number":
            if "." in str(new_val):
                new_val = float(new_val)
            else:
                new_val = int(new_val)

        # 1. Update live module
        setattr(cfg, k, new_val)

        # 2. Update config.py on disk
        if isinstance(new_val, str):
            new_literal = f'"{new_val}"'
        else:
            new_literal = str(new_val)

        # Pattern for: KEY = os.environ.get("...", "default")
        env_pat = re.compile(
            rf'^({k}\s*=\s*(?:int|float)?\(?\s*os\.environ\.get\(\s*"[^"]*"\s*,\s*)"([^"]*)"\s*\)?\)?',
            re.MULTILINE,
        )
        m = env_pat.search(content)
        if m:
            content = env_pat.sub(rf'\g<1>"{new_val}")', content)
        else:
            # Pattern for: KEY = "literal"  or  KEY = 123
            lit_pat = re.compile(rf'^({k}\s*=\s*)(.+)$', re.MULTILINE)
            if lit_pat.search(content):
                content = lit_pat.sub(rf'\g<1>{new_literal}', content)

        changed.append(k)

    if changed:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Config updated: %s", changed)

    return jsonify({"ok": True, "changed": changed})


# ===========================================================================
#   API  - Reports
# ===========================================================================
@app.route("/api/reports")
def api_reports_list():
    """List available JSON reports."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    files = sorted(
        [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")],
        reverse=True,
    )
    return jsonify(files)


@app.route("/api/reports/<filename>")
def api_report_detail(filename):
    """Return a specific report's JSON data."""
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "Not found"}), 404
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Enrich each execution result with root-cause analysis
    for tc in data.get("test_cases", []):
        for ex in tc.get("execution_results", []):
            if ex.get("status") not in ("passed",):
                cat, detail = _classify_root_cause(
                    ex.get("error_type", ""), ex.get("error_message", ""),
                    ex.get("traceback", ""), ex.get("stderr_tail", ""))
                ex["root_cause_category"] = cat
                ex["root_cause_detail"] = detail
            else:
                ex["root_cause_category"] = "none"
                ex["root_cause_detail"] = {}

    return jsonify(data)


# ===========================================================================
#   API  - Generated Tests
# ===========================================================================
@app.route("/api/generated-tests")
def api_generated_tests_list():
    """List generated test files."""
    os.makedirs(GENERATED_TESTS_DIR, exist_ok=True)
    files = sorted([
        f for f in os.listdir(GENERATED_TESTS_DIR)
        if f.endswith(".py") and f != "__init__.py"
    ])
    result = []
    for f in files:
        fp = os.path.join(GENERATED_TESTS_DIR, f)
        stat = os.stat(fp)
        result.append({
            "name": f,
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return jsonify(result)


@app.route("/api/generated-tests/<filename>")
def api_generated_test_detail(filename):
    """Return a generated test file's source code."""
    path = os.path.join(GENERATED_TESTS_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "Not found"}), 404
    with open(path, encoding="utf-8") as f:
        return jsonify({"filename": filename, "code": f.read()})


# ===========================================================================
#   API  - Logs
# ===========================================================================
@app.route("/api/logs")
def api_logs_list():
    """List log files."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    files = sorted(
        [f for f in os.listdir(LOGS_DIR) if f.endswith(".log")],
        reverse=True,
    )
    return jsonify(files)


@app.route("/api/logs/<filename>")
def api_log_detail(filename):
    """Return a log file's content (last 500 lines)."""
    path = os.path.join(LOGS_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "Not found"}), 404
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    tail = lines[-500:] if len(lines) > 500 else lines
    return jsonify({"filename": filename, "content": "".join(tail)})


@app.route("/api/reload", methods=["POST"])
def api_reload():
    """Force reload the Flask application."""
    try:
        # Clear all modules
        modules_to_clear = list(sys.modules.keys())
        for module_name in modules_to_clear:
            if module_name.startswith('simple_test_generator') or \
               module_name.startswith('agents') or \
               module_name == 'app':
                del sys.modules[module_name]
        
        # Force garbage collection
        import gc
        gc.collect()
        
        return jsonify({
            "status": "success",
            "message": "Application reloaded. Please restart the server manually.",
            "note": "For best results, stop and restart the server"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ===========================================================================
#   API  - Fetch test cases
# ===========================================================================
@app.route("/api/testcases/fetch-empty")
def api_fetch_empty_testcases():
    """Fetch non-automated test cases from the configured source."""
    limit = request.args.get("limit", 10, type=int)
    try:
        from agents.qtest_agent import QTestAgent
        agent = QTestAgent()
        tcs = agent.fetch_non_automated_test_cases(limit=limit)
        return jsonify({"test_cases": tcs, "count": len(tcs)})
    except Exception as e:
        return jsonify({"error": str(e), "test_cases": [], "count": 0}), 500


@app.route("/api/testcases/<tc_id>")
def api_fetch_testcase(tc_id):
    """Fetch a single test case by PID."""
    try:
        from agents.qtest_agent import QTestAgent
        agent = QTestAgent()
        tc = agent.fetch_test_case(tc_id)
        return jsonify(tc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===========================================================================
#   API  - Step-by-step pipeline (wizard mode)
# ===========================================================================
@app.route("/api/pipeline/generate", methods=["POST"])
def api_pipeline_generate():
    """Step 2: Generate test script from fetched test-case data.

    Expects JSON body with test_case_id.
    Returns generated code + list of required user inputs.
    """
    logger.info("DEBUG: api_pipeline_generate called")
    data = request.get_json(force=True)
    tc_id = data.get("test_case_id", "").strip()
    logger.info(f"DEBUG: tc_id = {tc_id}")
    if not tc_id:
        return jsonify({"error": "test_case_id required"}), 400

    try:
        # Directly use SimpleTestGenerator to generate test
        from simple_test_generator import SimpleTestGenerator
        from agents.qtest_agent import QTestAgent

        qtest = QTestAgent()
        gen = SimpleTestGenerator()

        tc = qtest.fetch_test_case(tc_id)
        result = gen.generate_test(tc)

        # Read the generated file
        with open(result["file_path"], 'r', encoding='utf-8') as f:
            code = f.read()

        # Determine required inputs
        required_inputs = _extract_required_inputs(code)

        return jsonify({
            "test_case_id": tc_id,
            "test_case_data": tc,
            "generated_file": result["filename"],
            "generated_file_path": result["file_path"],
            "generation_method": "template",
            "code_preview": code[:3000],
            "code_lines": code.count("\n") + 1,
            "required_inputs": required_inputs,
            "repo_context_used": False,
        })
    except Exception as e:
        logger.exception("Generate failed for %s", tc_id)
        return jsonify({"error": str(e)}), 500


# ===========================================================================
#   API  - Full pipeline execution (with live SSE)
# ===========================================================================
def _run_pipeline(run_id, test_case_ids, extra_env, max_retries):
    """Background worker that runs the full pipeline and pushes events."""
    run = _runs[run_id]
    eq = run["events"]

    def push(event_type, data=None):
        eq.put(json.dumps({"type": event_type, "ts": datetime.now().isoformat(),
                           **(data or {})}))

    try:
        push("started", {"test_case_ids": test_case_ids})

        # Create orchestrator (disable RAG for speed in pipeline runs)
        orchestrator = OrchestratorAgent(enable_rag=False)

        # Forward orchestrator log events to SSE stream
        def _flush_agent_events():
            for ev in orchestrator.get_events():
                push("agent_event", {
                    "agent": ev.get("agent", "Orchestrator"),
                    "event": ev.get("type", ""),
                    "message": ev.get("message", ""),
                })

        all_cycles = []
        for tc_id in test_case_ids:
            push("phase", f"Running test case: {tc_id}")
            cycle = orchestrator.run_test_case(tc_id, extra_env=extra_env)
            all_cycles.append(cycle)
            _flush_agent_events()
            push("tc_complete", {
                "test_case_id": tc_id,
                "status": cycle.final_status,
                "attempts": cycle.total_attempts,
            })

        # Generate report via orchestrator (produces proper JSON + HTML)
        report = orchestrator.generate_report(all_cycles)
        report_data = report["data"]

        # Build per-test-case failure analysis for the UI wizard
        analysis = []
        for cycle in all_cycles:
            failures = []
            for exec_result in cycle.execution_results:
                if exec_result.status != "passed":
                    cat, detail = _classify_root_cause(
                        exec_result.error_type,
                        exec_result.error_message,
                        exec_result.traceback,
                        exec_result.stderr,
                    )
                    failures.append({
                        "attempt": exec_result.attempt,
                        "category": cat,
                        "sub_type": detail.get("sub_type", ""),
                        "detail": detail.get("detail", ""),
                        "auto_fixable": detail.get("auto_fixable", False),
                        "expected": detail.get("expected", ""),
                        "actual": detail.get("actual", ""),
                    })
            analysis.append({
                "test_case_id": cycle.test_case_id,
                "final_status": cycle.final_status,
                "total_attempts": cycle.total_attempts,
                "failures": failures,
            })

        run["results"] = report_data
        run["report_json"] = os.path.basename(report["json"])
        run["report_html"] = os.path.basename(report["html"])
        run["status"] = "completed"

        push("completed", {
            "summary": report_data.get("summary", {}),
            "analysis": analysis,
            "report_json": os.path.basename(report["json"]),
            "report_html": os.path.basename(report["html"]),
        })

    except Exception as e:
        logger.exception("Pipeline run %s failed", run_id)
        run["status"] = "error"
        run["error"] = str(e)
        push("error", {"message": str(e)})
    finally:
        push("done", {})


@app.route("/api/pipeline/run", methods=["POST"])
def api_pipeline_run():
    """Start the full pipeline (returns run_id for SSE tracking).

    Body: {test_case_ids, user_inputs:{...env vars...}, max_retries}
    """
    data = request.get_json(force=True)
    tc_ids = data.get("test_case_ids", [])
    if isinstance(tc_ids, str):
        tc_ids = [t.strip() for t in tc_ids.replace(",", " ").split() if t.strip()]
    if not tc_ids:
        return jsonify({"error": "No test case IDs provided"}), 400

    # Build extra_env from user_inputs (flat dict of env var key -> value)
    user_inputs = data.get("user_inputs", {})
    extra_env = {k: v for k, v in user_inputs.items() if v}

    max_retries = data.get("max_retries", MAX_RETRIES)

    run_id = str(uuid.uuid4())[:8]
    with _run_lock:
        _runs[run_id] = {
            "status": "running",
            "events": queue.Queue(),
            "results": None,
            "analysis": None,
            "error": None,
            "started": datetime.now().isoformat(),
            "test_case_ids": tc_ids,
        }

    t = threading.Thread(target=_run_pipeline, daemon=True,
                         args=(run_id, tc_ids, extra_env, max_retries))
    t.start()

    return jsonify({"run_id": run_id, "status": "running"})


@app.route("/api/pipeline/status/<run_id>")
def api_pipeline_status_sse(run_id):
    """Server-Sent Events stream for a pipeline run."""
    run = _runs.get(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404

    def stream():
        eq = run["events"]
        while True:
            try:
                msg = eq.get(timeout=30)
                yield f"data: {msg}\n\n"
                if '"type": "done"' in msg or '"type":"done"' in msg:
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no"})


@app.route("/api/pipeline/runs")
def api_pipeline_runs():
    """List all pipeline runs."""
    out = []
    for rid, r in _runs.items():
        out.append({
            "run_id": rid,
            "status": r["status"],
            "started": r["started"],
            "test_case_ids": r["test_case_ids"],
        })
    return jsonify(sorted(out, key=lambda x: x["started"], reverse=True))


# ===========================================================================
#   API  - RAG Document Search
# ===========================================================================
@app.route("/api/rag/search", methods=["POST"])
def api_rag_search():
    """Search the knowledge base using RAG."""
    if rag_system is None:
        return jsonify({
            "error": "RAG system not available",
            "message": "RAG system failed to initialize or is disabled"
        }), 503

    try:
        data = request.get_json()
        query = data.get("query", "")
        k = data.get("k", 5)

        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        results = rag_system.search(query, k=k)

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })

    except Exception as e:
        return jsonify({
            "error": "Search failed",
            "message": str(e)
        }), 500


@app.route("/api/rag/stats")
def api_rag_stats():
    """Get RAG system statistics."""
    if rag_system is None:
        return jsonify({
            "error": "RAG system not available",
            "message": "RAG system failed to initialize or is disabled"
        }), 503

    try:
        stats = rag_system.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            "error": "Failed to get stats",
            "message": str(e)
        }), 500


@app.route("/api/rag/context", methods=["POST"])
def api_rag_context():
    """Get RAG context for test generation."""
    if rag_system is None:
        return jsonify({
            "error": "RAG system not available",
            "message": "RAG system failed to initialize or is disabled"
        }), 503

    try:
        data = request.get_json()
        test_case = data.get("test_case", {})
        k = data.get("k", 3)

        if not test_case:
            return jsonify({"error": "test_case parameter is required"}), 400

        context = rag_system.get_context_for_test_generation(test_case, k=k)

        return jsonify({
            "context": context,
            "test_case": test_case.get("pid", "unknown")
        })

    except Exception as e:
        return jsonify({
            "error": "Failed to get context",
            "message": str(e)
        }), 500


# ===========================================================================
#   Frontend
# ===========================================================================
@app.route("/")
def index():
    return render_template("index.html")


# ===========================================================================
#   Main
# ===========================================================================
if __name__ == "__main__":
    for d in [OUTPUT_DIR, LOGS_DIR, GENERATED_TESTS_DIR, REPORTS_DIR]:
        os.makedirs(d, exist_ok=True)

    print("=" * 60)
    print("  ShopEasy AI-Powered Agentic Test Automation - Web UI")
    print("=" * 60)
    print(f"  URL:       http://localhost:5001")
    print(f"  API URL:   {SHOPEASE_API_URL}")
    print(f"  Source:    Demo test cases (local JSON)")
    print("=" * 60)

    # use_reloader=False is critical: the stat-reloader watches ALL files
    # under the project root.  When the pipeline writes a generated test,
    # log, or report the reloader would restart the server, killing the
    # running pipeline thread and wiping the in-memory _runs dict.
    # debug=True still gives us nice tracebacks; we just skip auto-reload.
    app.run(host="0.0.0.0", port=5001, debug=True, threaded=True,
            use_reloader=False)
