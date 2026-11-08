import subprocess
import sys

def test_cli_recommend():
    result = subprocess.run(
        [sys.executable, "cli.py", "recommend"],
        capture_output=True,
        text=True,
        cwd="/Users/up-mac/wokrspace/mind/trader/edca"
    )
    assert result.returncode == 0
    assert "EDCA" in result.stdout

def test_cli_portfolio():
    result = subprocess.run(
        [sys.executable, "cli.py", "portfolio"],
        capture_output=True,
        text=True,
        cwd="/Users/up-mac/wokrspace/mind/trader/edca"
    )
    assert result.returncode == 0
    assert "TSM" in result.stdout
    assert "SCB" in result.stdout
