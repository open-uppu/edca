import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

edca_dir = Path(__file__).resolve().parent.parent
if str(edca_dir) not in sys.path:
    sys.path.insert(0, str(edca_dir))

from server import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "edca-advisor"

def test_portfolio_endpoint():
    res = client.get("/api/v1/portfolio")
    assert res.status_code == 200
    data = res.json()
    assert "holdings" in data
    assert len(data["holdings"]) > 0

def test_recommend_endpoint():
    res = client.get("/api/v1/recommend")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "trading_day" in data
    assert "execution_plan" in data
    assert "allocations" in data
    assert len(data["allocations"]) > 0
    assert "advisory" in data

def test_backtest_endpoint():
    res = client.get("/api/v1/backtest")
    assert res.status_code == 200
    data = res.json()
    assert "strategies" in data
    assert len(data["strategies"]) == 3
