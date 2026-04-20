# Known Issues and Limitations

## Web UI Framework Issue

**Status:** Known limitation - to be fixed for final demo

**Description:**
The web UI (`http://localhost:5001`) currently generates test cases using the old Atlas framework (`shopease_framework`) instead of the new standalone framework, despite code changes to use `SimpleTestGenerator`.

**Root Cause:**
Python module caching in Flask is preventing code changes from taking effect. Multiple cache clearing mechanisms were attempted but the issue persists.

**Workaround:**
Use the standalone framework directly via command line:

```bash
# Generate all test cases with standalone framework
py regenerate_tests.py

# Run all tests with pytest
py -m pytest generated_tests/ -v

# Run specific test case
py -m pytest generated_tests/test_TC_001.py -v
```

**Current Status:**
- ✅ Standalone framework is fully functional
- ✅ Direct pytest execution works perfectly (all 10 tests pass)
- ✅ Manual test regeneration via `regenerate_tests.py` works correctly
- ❌ Web UI still uses old framework due to caching issue

**Planned Fix for Final Demo:**
- Investigate Flask module caching in more depth
- Consider using a fresh Python virtual environment
- Implement a more robust cache clearing mechanism
- Potentially refactor the web UI to use subprocess exclusively

## RAG System Memory Issue

**Status:** Temporary workaround implemented

**Description:**
The RAG system initialization fails with "The paging file is too small for this operation to complete" error on Windows.

**Workaround:**
RAG system is temporarily disabled in `app.py` to allow the web UI to start. This does not affect the core test generation functionality.

**Planned Fix:**
- Increase system page file size
- Optimize RAG system memory usage
- Consider using a lighter-weight embedding model
