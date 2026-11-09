import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_cli_recommend():
    result = subprocess.run(
        [sys.executable, "cli.py", "recommend"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=BASE_DIR
    )
    assert result.returncode == 0
    assert "EDCA" in (result.stdout or "")

def test_cli_portfolio():
    result = subprocess.run(
        [sys.executable, "cli.py", "portfolio"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=BASE_DIR
    )
    assert result.returncode == 0
    assert "TSM" in (result.stdout or "")
    assert "SCB" in (result.stdout or "")

def test_cli_scan():
    result = subprocess.run(
        [sys.executable, "cli.py", "scan"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=BASE_DIR
    )
    assert result.returncode == 0
    assert "Opportunity" in (result.stdout or "") or "Scanner" in (result.stdout or "")
