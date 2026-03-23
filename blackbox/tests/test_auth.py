"""
test_auth.py — Tests for mandatory header validation.

Every endpoint requires X-Roll-Number header (valid integer).
User endpoints also require X-User-ID header (positive integer, existing user).

Test Cases:
  TC-AUTH-01: Missing X-Roll-Number on admin endpoint     → 401
  TC-AUTH-02: Non-integer X-Roll-Number (letters)         → 400
  TC-AUTH-03: Non-integer X-Roll-Number (symbols)         → 400
  TC-AUTH-04: Valid X-Roll-Number on admin endpoint       → 200
  TC-AUTH-05: Missing X-User-ID on user endpoint          → 400
  TC-AUTH-06: Non-integer X-User-ID                       → 400
  TC-AUTH-07: X-User-ID for non-existent user             → 400
  TC-AUTH-08: Valid headers on user endpoint              → 200

Justification: Authentication is the first gate for every request.
Failures here mean the entire API is unsecured — all tests depend on
correct header handling.
"""

import requests
import pytest
from conftest import BASE_URL, ROLL_NUMBER, PRIMARY_USER_ID, admin_headers, user_headers

ADMIN_URL = f"{BASE_URL}/admin/users"
USER_URL  = f"{BASE_URL}/profile"


class TestRollNumberHeader:

    def test_TC_AUTH_01_missing_roll_number_returns_401(self):
        """Missing X-Roll-Number must return 401 Unauthorized."""
        r = requests.get(ADMIN_URL)
        assert r.status_code == 401, (
            f"Expected 401 when X-Roll-Number is missing, got {r.status_code}"
        )

    def test_TC_AUTH_02_alpha_roll_number_returns_400(self):
        """Alphabetical X-Roll-Number must return 400 Bad Request."""
        r = requests.get(ADMIN_URL, headers={"X-Roll-Number": "abc"})
        assert r.status_code == 400, (
            f"Expected 400 for non-integer X-Roll-Number 'abc', got {r.status_code}"
        )

    def test_TC_AUTH_03_symbol_roll_number_returns_400(self):
        """Symbol X-Roll-Number must return 400 Bad Request."""
        r = requests.get(ADMIN_URL, headers={"X-Roll-Number": "!@#"})
        assert r.status_code == 400, (
            f"Expected 400 for symbol X-Roll-Number '!@#', got {r.status_code}"
        )

    def test_TC_AUTH_04_valid_roll_number_returns_200(self):
        """Valid X-Roll-Number must allow the request through."""
        r = requests.get(ADMIN_URL, headers=admin_headers())
        assert r.status_code == 200, (
            f"Expected 200 with valid X-Roll-Number, got {r.status_code}"
        )


class TestUserIDHeader:

    def test_TC_AUTH_05_missing_user_id_returns_400(self):
        """Missing X-User-ID on a user endpoint must return 400."""
        r = requests.get(USER_URL, headers={"X-Roll-Number": ROLL_NUMBER})
        assert r.status_code == 400, (
            f"Expected 400 when X-User-ID is missing, got {r.status_code}"
        )

    def test_TC_AUTH_06_non_integer_user_id_returns_400(self):
        """Non-integer X-User-ID must return 400."""
        r = requests.get(USER_URL, headers={
            "X-Roll-Number": ROLL_NUMBER,
            "X-User-ID": "abc"
        })
        assert r.status_code == 400, (
            f"Expected 400 for non-integer X-User-ID 'abc', got {r.status_code}"
        )

    def test_TC_AUTH_07_nonexistent_user_id_returns_400(self):
        """X-User-ID pointing to a non-existent user must return 400."""
        r = requests.get(USER_URL, headers={
            "X-Roll-Number": ROLL_NUMBER,
            "X-User-ID": "999999"
        })
        assert r.status_code == 400, (
            f"Expected 400 for non-existent X-User-ID 999999, got {r.status_code}"
        )

    def test_TC_AUTH_08_valid_user_id_returns_200(self):
        """Valid X-User-ID must allow the request through."""
        r = requests.get(USER_URL, headers=user_headers(PRIMARY_USER_ID))
        assert r.status_code == 200, (
            f"Expected 200 with valid X-User-ID, got {r.status_code}"
        )
