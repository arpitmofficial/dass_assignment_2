"""
test_loyalty.py — Tests for Loyalty Points API.

Endpoints:
  GET  /api/v1/loyalty
  POST /api/v1/loyalty/redeem

Test Cases:
  TC-LOY-01: GET loyalty returns 200 with loyalty_points field            → 200
  TC-LOY-02: Redeem points=1 (min valid)                                  → 200
  TC-LOY-03: Redeem points=0 (below min) rejected                        → 400
  TC-LOY-04: Redeem negative points rejected                              → 400
  TC-LOY-05: Redeem more than available rejected                          → 400
  TC-LOY-06: Redeem with wrong data type (string) rejected                → 400

Justification: Loyalty points are a financial reward — redemption must be
precisely validated to prevent fraud or negative balances.
"""

import requests
import pytest
from conftest import BASE_URL, user_headers, json_headers

LOYALTY_URL = f"{BASE_URL}/loyalty"
REDEEM_URL  = f"{BASE_URL}/loyalty/redeem"

# Use user 443 who has 500 loyalty points
UID = 443
H  = user_headers(UID)
JH = json_headers(UID)


class TestLoyaltyView:

    def test_TC_LOY_01_get_loyalty_returns_200(self):
        """GET /loyalty must return 200 with loyalty_points field."""
        r = requests.get(LOYALTY_URL, headers=H)
        assert r.status_code == 200
        data = r.json()
        assert "loyalty_points" in data, f"Missing loyalty_points field. Keys: {list(data.keys())}"


class TestLoyaltyRedeem:

    def test_TC_LOY_02_redeem_min_valid(self):
        """Redeeming points=1 (minimum valid) must succeed."""
        r = requests.post(REDEEM_URL, headers=JH, json={"points": 1})
        assert r.status_code == 200, (
            f"Expected 200 for redeem points=1, got {r.status_code}: {r.text}"
        )

    def test_TC_LOY_03_redeem_zero_rejected(self):
        """Redeeming points=0 must return 400."""
        r = requests.post(REDEEM_URL, headers=JH, json={"points": 0})
        assert r.status_code == 400, (
            f"Expected 400 for redeem points=0, got {r.status_code}"
        )

    def test_TC_LOY_04_redeem_negative_rejected(self):
        """Redeeming negative points must return 400."""
        r = requests.post(REDEEM_URL, headers=JH, json={"points": -5})
        assert r.status_code == 400, (
            f"Expected 400 for negative points, got {r.status_code}"
        )

    def test_TC_LOY_05_redeem_more_than_available_rejected(self):
        """Redeeming more points than available must return 400."""
        r = requests.post(REDEEM_URL, headers=JH, json={"points": 999999})
        assert r.status_code == 400, (
            f"Expected 400 when redeeming more than available, got {r.status_code}"
        )

    def test_TC_LOY_06_redeem_wrong_type_rejected(self):
        """Redeeming with string value must return 400."""
        r = requests.post(REDEEM_URL, headers=JH, json={"points": "five"})
        assert r.status_code == 400, (
            f"Expected 400 for string points value, got {r.status_code}"
        )
