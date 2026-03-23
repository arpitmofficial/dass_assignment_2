"""
test_admin_users.py — Tests for Admin User Detail API.

Endpoint: GET /api/v1/admin/users/{user_id}

Test Cases:
  TC-ADM-01: Valid user_id returns 200 and matches requested stats
  TC-ADM-02: Non-existent user_id returns 404
  TC-ADM-03: Non-integer user_id returns 400
  TC-ADM-04: Working without X-User-ID header (admin route)
  TC-ADM-05: Missing X-Roll-Number returns 401

Justification: Ensures that the admin lookup rule works robustly
and validates the data boundary conditions.
"""

import requests
import pytest
from conftest import BASE_URL, PRIMARY_USER_ID, admin_headers

ADMIN_DETAIL_URL = f"{BASE_URL}/admin/users"

class TestAdminUserDetail:

    def test_TC_ADM_01_valid_user_id_returns_200(self):
        """GET /admin/users/{user_id} returns 200 for valid user."""
        r = requests.get(f"{ADMIN_DETAIL_URL}/{PRIMARY_USER_ID}", headers=admin_headers())
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get("user_id") == PRIMARY_USER_ID, "Returned wrong user_id"

    def test_TC_ADM_02_nonexistent_user_returns_404(self):
        """GET /admin/users/999999 returns 404."""
        r = requests.get(f"{ADMIN_DETAIL_URL}/999999", headers=admin_headers())
        assert r.status_code == 404, f"Expected 404 for non-existent user, got {r.status_code}"

    def test_TC_ADM_03_non_integer_user_id_returns_400(self):
        """GET /admin/users/abc returns 400."""
        r = requests.get(f"{ADMIN_DETAIL_URL}/abc", headers=admin_headers())
        assert r.status_code == 400, f"Expected 400 for string user_id, got {r.status_code}"

    def test_TC_ADM_04_works_without_x_user_id(self):
        """Admin endpoints should NOT require X-User-ID."""
        r = requests.get(f"{ADMIN_DETAIL_URL}/{PRIMARY_USER_ID}", headers=admin_headers())
        assert r.status_code == 200, "Should permit access without X-User-ID"

    def test_TC_ADM_05_missing_roll_number_returns_401(self):
        """Missing X-Roll-Number entirely returns 401."""
        r = requests.get(f"{ADMIN_DETAIL_URL}/{PRIMARY_USER_ID}")
        assert r.status_code == 401, f"Expected 401 for missing roll number, got {r.status_code}"
