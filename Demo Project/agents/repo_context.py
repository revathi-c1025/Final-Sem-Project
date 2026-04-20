"""
Reference Repository Context Scanner
=====================================
Scans a local (or future: GitHub-cloned) test repository to extract:
  - Similar test files (by keyword matching against test case step descriptions)
  - Library / utility modules available for import
  - conftest.py fixtures and patterns
  - Common import patterns used across the repo

This context is fed to the TestGeneratorAgent (both LLM and template modes)
so generated code references real libraries, follows real patterns, and produces
complete, correct test scripts.
"""

import os
import re
import logging
from pathlib import Path
from difflib import SequenceMatcher

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keywords to ignore when matching (too common to be useful)
# ---------------------------------------------------------------------------
_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "and", "but", "or",
    "nor", "not", "so", "yet", "for", "of", "in", "to", "on", "at",
    "by", "with", "from", "as", "into", "through", "during", "before",
    "after", "above", "below", "between", "under", "over", "that",
    "this", "these", "those", "it", "its", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "no",
    "test", "step", "verify", "check", "ensure", "validate", "confirm",
}


class RepoContext:
    """Scans and caches reference-repo information for code generation."""

    def __init__(self, repo_path=None):
        self._repo_path = repo_path or self._get_configured_path()
        self._test_files_cache = None
        self._library_modules_cache = None
        self._conftest_cache = None
        self._import_map_cache = None

    @staticmethod
    def _get_configured_path():
        try:
            from config import REFERENCE_REPO_LOCAL_PATH
            return REFERENCE_REPO_LOCAL_PATH
        except ImportError:
            return ""

    @property
    def available(self):
        return bool(self._repo_path) and os.path.isdir(self._repo_path)

    # ------------------------------------------------------------------
    # 1.  Discover test files
    # ------------------------------------------------------------------
    def get_test_files(self):
        """Return list of (relative_path, abs_path) for all test_*.py files."""
        if self._test_files_cache is not None:
            return self._test_files_cache
        if not self.available:
            return []

        result = []
        for root, _dirs, files in os.walk(self._repo_path):
            # skip hidden / pycache / dev-tests dirs
            rel = os.path.relpath(root, self._repo_path)
            if any(part.startswith(".") or part == "__pycache__"
                   for part in Path(rel).parts):
                continue
            for f in files:
                if f.startswith("test_") and f.endswith(".py"):
                    abs_p = os.path.join(root, f)
                    result.append((os.path.relpath(abs_p, self._repo_path), abs_p))
        self._test_files_cache = result
        return result

    # ------------------------------------------------------------------
    # 2.  Discover library modules (shopease_framework)
    # ------------------------------------------------------------------
    def get_library_modules(self):
        """Return dict {module_dotted_name: abs_path} for framework *.py files."""
        if self._library_modules_cache is not None:
            return self._library_modules_cache

        result = {}
        # Check for shopease_framework directory
        framework_dir = os.path.join(self._repo_path, "shopease_framework")
        if not os.path.isdir(framework_dir):
            self._library_modules_cache = result
            return result

        for root, _dirs, files in os.walk(framework_dir):
            for f in files:
                if f.endswith(".py") and f != "__init__.py":
                    abs_p = os.path.join(root, f)
                    rel = os.path.relpath(abs_p, self._repo_path).replace(os.sep, "/")
                    dotted = rel.replace("/", ".").replace(".py", "")
                    result[dotted] = abs_p
        self._library_modules_cache = result
        return result

    # ------------------------------------------------------------------
    # 3.  Get conftest.py contents
    # ------------------------------------------------------------------
    def get_conftest(self):
        """Return the root conftest.py content, or '' if absent."""
        if self._conftest_cache is not None:
            return self._conftest_cache
        # Check tests directory first, then root
        for subdir in ["tests", ""]:
            path = os.path.join(self._repo_path, subdir, "conftest.py")
            if os.path.isfile(path):
                with open(path, encoding="utf-8", errors="replace") as f:
                    self._conftest_cache = f.read()
                return self._conftest_cache
        self._conftest_cache = ""
        return self._conftest_cache

    # ------------------------------------------------------------------
    # 4.  Build import-pattern map (which imports are used across tests)
    # ------------------------------------------------------------------
    def get_common_imports(self):
        """Return a dict {import_line: count} of the most common import lines."""
        if self._import_map_cache is not None:
            return self._import_map_cache

        counter = {}
        for _rel, abs_p in self.get_test_files()[:60]:  # sample first 60 files
            try:
                with open(abs_p, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith("from ") or stripped.startswith("import "):
                            # Normalize whitespace
                            norm = re.sub(r'\s+', ' ', stripped)
                            counter[norm] = counter.get(norm, 0) + 1
            except OSError:
                continue

        # Sort by frequency descending
        self._import_map_cache = dict(
            sorted(counter.items(), key=lambda x: -x[1])
        )
        return self._import_map_cache

    # ------------------------------------------------------------------
    # 5.  Find similar test files to the given test-case description
    # ------------------------------------------------------------------
    def find_similar_tests(self, test_case_data, top_n=3):
        """
        Given a parsed test-case dict, find the most similar
        existing test files by keyword overlap.

        Returns list of dicts:
          [{"file": relative_path, "score": float, "code": str (first 200 lines)}, ...]
        """
        if not self.available:
            return []

        # Build keyword set from test-case steps + name + description
        tc_text = self._tc_to_text(test_case_data).lower()
        tc_words = self._extract_keywords(tc_text)

        if not tc_words:
            return []

        scored = []
        for rel, abs_p in self.get_test_files():
            try:
                with open(abs_p, encoding="utf-8", errors="replace") as f:
                    code = f.read()
            except OSError:
                continue

            file_text = code.lower()
            file_words = self._extract_keywords(file_text)

            # Jaccard-like score weighted by keyword matches
            if not file_words:
                continue
            common = tc_words & file_words
            score = len(common) / max(len(tc_words | file_words), 1)

            # Boost if filename has matching service keyword
            name_lower = rel.lower()
            for kw in tc_words:
                if kw in name_lower and len(kw) > 4:
                    score += 0.15

            scored.append((score, rel, code))

        scored.sort(key=lambda x: -x[0])
        results = []
        for score, rel, code in scored[:top_n]:
            if score < 0.02:
                break
            lines = code.split("\n")
            preview = "\n".join(lines[:200])
            results.append({
                "file": rel,
                "score": round(score, 3),
                "code": preview,
            })
        return results

    # ------------------------------------------------------------------
    # 6.  Get library module summaries (docstrings + class/function names)
    # ------------------------------------------------------------------
    def get_library_summaries(self):
        """Return dict {module_name: summary_string} for library modules."""
        summaries = {}
        for dotted, abs_p in self.get_library_modules().items():
            try:
                with open(abs_p, encoding="utf-8", errors="replace") as f:
                    code = f.read()
                # Extract class names
                classes = re.findall(r'^class\s+(\w+)', code, re.MULTILINE)
                # Extract function names (top-level and static methods)
                funcs = re.findall(r'def\s+(\w+)\s*\(', code)
                # Module docstring
                doc_match = re.match(r'^(?:#.*\n)*\s*(?:"""(.*?)"""|\'\'\'(.*?)\'\'\')',
                                     code, re.DOTALL)
                docstring = ""
                if doc_match:
                    docstring = (doc_match.group(1) or doc_match.group(2) or "").strip()

                summary = f"Module: {dotted}\n"
                if docstring:
                    summary += f"  Description: {docstring[:200]}\n"
                if classes:
                    summary += f"  Classes: {', '.join(classes)}\n"
                if funcs:
                    # Filter out dunder methods
                    pub_funcs = [f for f in funcs if not f.startswith("_")]
                    if pub_funcs:
                        summary += f"  Functions: {', '.join(pub_funcs[:20])}\n"
                summaries[dotted] = summary
            except OSError:
                continue
        return summaries

    # ------------------------------------------------------------------
    # 7.  Build full context string for the generator
    # ------------------------------------------------------------------
    def build_generation_context(self, test_case_data):
        """
        Build a comprehensive context string that the generator can use
        to produce correct, complete test code.

        Returns a dict with:
          - similar_tests: code snippets of similar test files
          - library_summary: available library modules and their APIs
          - common_imports: most-used import lines
          - conftest_excerpt: relevant conftest patterns
        """
        if not self.available:
            return {
                "similar_tests": [],
                "library_summary": "",
                "common_imports": [],
                "conftest_excerpt": "",
                "repo_available": False,
            }

        similar = self.find_similar_tests(test_case_data, top_n=3)
        lib_sums = self.get_library_summaries()
        imports = self.get_common_imports()
        conftest = self.get_conftest()

        # Top 15 most common imports
        top_imports = list(imports.keys())[:15]

        # Library summary text
        lib_text = "\n".join(lib_sums.values())

        # Conftest excerpt (first 100 lines)
        conf_lines = conftest.split("\n")[:100]
        conf_excerpt = "\n".join(conf_lines)

        return {
            "similar_tests": similar,
            "library_summary": lib_text,
            "common_imports": top_imports,
            "conftest_excerpt": conf_excerpt,
            "repo_available": True,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _tc_to_text(tc):
        """Flatten test-case dict into a single searchable text."""
        parts = [
            tc.get("name", ""),
            tc.get("description", ""),
            tc.get("precondition", ""),
        ]
        for step in tc.get("steps", []):
            parts.append(step.get("description", ""))
            parts.append(step.get("expected_result", ""))
        return " ".join(parts)

    @staticmethod
    def _extract_keywords(text):
        """Extract meaningful keywords from text."""
        words = re.findall(r'[a-z_]{3,}', text)
        return {w for w in words if w not in _STOP_WORDS and len(w) > 2}
