"""
Automated security tests for secret scanning and exclusion hygiene.
"""

import os
import glob
import re

def test_no_hardcoded_secrets_in_tracked_code():
    """Verify no hardcoded private keys or live secret tokens exist in python files."""
    secret_patterns = [
        r"BEGIN\s+(RSA|OPENSSH|EC|DSA)\s+PRIVATE\s+KEY",
        r"ghp_[0-9a-zA-Z]{36}",
        r"sk_[live|test]_[0-9a-zA-Z]{24}"
    ]

    matched_files = []
    for fpath in glob.glob("**/*.py", recursive=True):
        if ".venv" in fpath or "__pycache__" in fpath or "scratch" in fpath or "tests" in fpath:
            continue
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for pattern in secret_patterns:
                if re.search(pattern, content):
                    matched_files.append((fpath, pattern))

    assert len(matched_files) == 0, f"Potential secrets detected: {matched_files}"

def test_gitignore_protects_secrets_and_caches():
    """Verify that .gitignore contains explicit rules for secrets and environments."""
    assert os.path.exists(".gitignore"), ".gitignore file must exist"
    with open(".gitignore", "r", encoding="utf-8") as f:
        gitignore_content = f.read()

    assert ".streamlit/secrets.toml" in gitignore_content
    assert ".env" in gitignore_content
    assert ".venv/" in gitignore_content
    assert "__pycache__/" in gitignore_content
