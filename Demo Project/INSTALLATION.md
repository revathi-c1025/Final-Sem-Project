# Quick Installation Guide

## Single Command Installation

Install all required packages with one command:

### Windows
```cmd
pip install -r requirements.txt
```

### macOS and Linux
```bash
pip3 install -r requirements.txt
```

## What Gets Installed

The `requirements.txt` file will install these essential packages:

1. **Flask 3.0.0** - Web framework (for web UI, optional for demo)
2. **pytest 7.4.3** - Testing framework (REQUIRED)
3. **pytest-html 3.2.0** - HTML test reports (optional)
4. **requests 2.31.0** - HTTP library (REQUIRED for mock API)
5. **python-dateutil 2.8.2** - Date processing (REQUIRED)

## Installation Time

- **First time**: 2-5 minutes (downloads packages from internet)
- **If already cached**: 30-60 seconds

## Verification

After installation, verify with:
```cmd
pip list
```

You should see the packages listed above.

## Troubleshooting

### If pip is not recognized:
```cmd
python -m pip install -r requirements.txt
```
or
```cmd
py -m pip install -r requirements.txt
```

### If you get permission errors:
- Windows: Run Command Prompt as Administrator
- Mac/Linux: Use `sudo pip3 install -r requirements.txt`

### If installation fails:
1. Check your internet connection
2. Try upgrading pip first:
   ```cmd
   pip install --upgrade pip
   ```
3. Then retry the installation

## After Installation

Once installed, you can run the demo:
```cmd
py run_demo.py
```

That's it! All dependencies are now installed and ready to use.
