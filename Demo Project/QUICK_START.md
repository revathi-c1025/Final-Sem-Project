# Quick Start Commands - Slack-Based DevOps AI Assistant Demo

## Complete Setup (3 Commands)

These are the only 3 commands needed to set up and run the demo on a fresh system:

### 1. Install Python Dependencies
```cmd
pip install -r requirements.txt
```

### 2. Initialize Cloud Integration
```cmd
py agents/cloud_orchestrator_agent.py
```

### 3. Start Slack Bot & NLP Engine
```cmd
py agents/nlp_parser_agent.py
```

---

## OR Use the Demo Script (1 Command)

### Single Command Demo
```cmd
py run_demo.py
```

This single command will:
- Initialize Slack bot connection
- Connect to Kubernetes cluster
- Establish Prometheus monitoring
- Validate RBAC policies
- Demonstrate conversational commands
- Display audit logs

---

## Platform-Specific Commands

### Windows
```cmd
pip install -r requirements.txt
py run_demo.py
```

### macOS/Linux
```bash
pip3 install -r requirements.txt
python3 run_demo.py
```

---

## That's It!

Just these commands and your demo is ready to run.

For detailed instructions, see:
- `INSTALLATION.md` - Detailed installation guide
- `DEMO_EXECUTION_GUIDE.md` - Complete demo execution guide
- `README.md` - Project overview
