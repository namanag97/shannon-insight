"""Tests for git rename detection."""
import sys
sys.path.insert(0, "src")

import os
import tempfile
import subprocess
import pytest
from shannon_insight.diff.rename import detect_renames


class TestDetectRenames:
    def test_no_git_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_renames(tmpdir, "abc123", "def456")
            assert result == {}

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/git") and not os.path.exists("/usr/local/bin/git") and not os.path.exists("/opt/homebrew/bin/git"),
        reason="git not found"
    )
    def test_detect_renames_in_temp_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up a temp git repo
            subprocess.run(["git", "init", tmpdir], capture_output=True)
            subprocess.run(["git", "-C", tmpdir, "config", "user.email", "test@test.com"], capture_output=True)
            subprocess.run(["git", "-C", tmpdir, "config", "user.name", "Test"], capture_output=True)

            # Create initial file
            open(os.path.join(tmpdir, "old_name.py"), "w").write("content here\n")
            subprocess.run(["git", "-C", tmpdir, "add", "."], capture_output=True)
            subprocess.run(["git", "-C", tmpdir, "commit", "-m", "init"], capture_output=True)
            old_sha = subprocess.run(["git", "-C", tmpdir, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

            # Rename file
            subprocess.run(["git", "-C", tmpdir, "mv", "old_name.py", "new_name.py"], capture_output=True)
            subprocess.run(["git", "-C", tmpdir, "commit", "-m", "rename"], capture_output=True)
            new_sha = subprocess.run(["git", "-C", tmpdir, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

            renames = detect_renames(tmpdir, old_sha, new_sha)
            assert renames.get("old_name.py") == "new_name.py"
