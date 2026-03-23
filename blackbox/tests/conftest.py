"""
conftest.py — Shared configuration and fixtures for QuickCart API tests.

Every test module imports BASE_URL, HEADERS, and USER_HEADERS from here.
The server must be running at localhost:8080 before executing the suite.
    docker run -d -p 8080:8080 quickcart

To run all tests:
    pip install pytest requests
    pytest tests/ -v --tb=short

Roll number used: 2024101112
Primary test user: user_id=1 (Anita Johnson)
"""

import pytest
import requests

# ─── Constants ───────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8080/api/v1"
ROLL_NUMBER = "2024101112"

# Primary user for most tests
PRIMARY_USER_ID = 1

# A second, separate user so cart/order tests don't collide
SECONDARY_USER_ID = 2

# A user with a high wallet balance for wallet/checkout tests
RICH_USER_ID = 3   # Bob Wilson — wallet: 578.96

# Known product IDs (active)
PRODUCT_APPLE = 1      # Apple - Red, price=120, stock=195
PRODUCT_BANANA = 3     # Banana - Robusta, price=40, stock=282
PRODUCT_MANGO = 5      # Mango - Alphonso, price=250, stock=56

# Known inactive product
PRODUCT_INACTIVE = 214   # is_active=False (from admin products list)

# Coupon codes (from admin/coupons)
COUPON_VALID_FIXED   = "BONUS75"      # FIXED $75 off, min $750, expires Apr 2026
COUPON_VALID_PERCENT = "FIRSTORDER"   # 15% off, min $200, max $150, expires Jun 2026
COUPON_VALID_CAP     = "LOYALTY20"    # 20% off, min $600, max $180, expires May 2026
COUPON_EXPIRED       = "EXPIRED100"   # expired Feb 2026
COUPON_EXPIRED2      = "DEAL5"        # expired Mar 15 2026


# ─── Header helpers ───────────────────────────────────────────────────────────

def admin_headers():
    """Headers for admin endpoints (no X-User-ID required)."""
    return {"X-Roll-Number": ROLL_NUMBER}


def user_headers(user_id=PRIMARY_USER_ID):
    """Headers for user-scoped endpoints."""
    return {
        "X-Roll-Number": ROLL_NUMBER,
        "X-User-ID": str(user_id),
    }


def json_headers(user_id=PRIMARY_USER_ID):
    """Headers for POST/PUT requests with JSON body."""
    return {
        "X-Roll-Number": ROLL_NUMBER,
        "X-User-ID": str(user_id),
        "Content-Type": "application/json",
    }


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def server_is_up():
    """Fail the whole suite early if the server is not reachable."""
    try:
        r = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers(), timeout=5)
        assert r.status_code == 200, "Server returned non-200 on startup check"
    except Exception as e:
        pytest.fail(f"QuickCart server is not reachable at {BASE_URL}: {e}")


@pytest.fixture
def clear_cart(request):
    """Clear the cart for a given user before and after a test."""
    uid = getattr(request, "param", PRIMARY_USER_ID)
    requests.delete(f"{BASE_URL}/cart/clear", headers=user_headers(uid))
    yield uid
    requests.delete(f"{BASE_URL}/cart/clear", headers=user_headers(uid))
