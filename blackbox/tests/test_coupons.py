"""
test_coupons.py — Tests for Coupon Apply/Remove API.

Endpoints:
  POST /api/v1/coupon/apply
  POST /api/v1/coupon/remove

Test Cases:
  TC-CPN-01: Apply valid FIXED coupon (BONUS75) when cart ≥ min    → 200, discount=75
  TC-CPN-02: Apply PERCENT coupon (FIRSTORDER) — verify 15% calc   → 200
  TC-CPN-03: Apply expired coupon (EXPIRED100) must fail            → 400
  TC-CPN-04: Apply coupon when cart < min_cart_value must fail      → 400
  TC-CPN-05: PERCENT coupon discount must be capped at max_discount → verify
  TC-CPN-06: Apply non-existent coupon code must fail               → 400/404
  TC-CPN-07: Remove applied coupon restores original total          → verify

Justification: Coupon bugs directly cause financial loss — customers
get too big a discount or an expired code goes through. The discount cap
is especially important to prevent abuse.
"""

import requests
import pytest
from conftest import (
    BASE_URL, PRODUCT_APPLE, PRODUCT_BANANA, PRODUCT_MANGO,
    COUPON_VALID_FIXED, COUPON_VALID_PERCENT, COUPON_VALID_CAP,
    COUPON_EXPIRED, user_headers, json_headers
)

APPLY_URL  = f"{BASE_URL}/coupon/apply"
REMOVE_URL = f"{BASE_URL}/coupon/remove"
ADD_URL    = f"{BASE_URL}/cart/add"
CART_URL   = f"{BASE_URL}/cart"
CLEAR_URL  = f"{BASE_URL}/cart/clear"

# Use user 11 for coupon tests
UID = 11
H   = user_headers(UID)
JH  = json_headers(UID)


@pytest.fixture(autouse=True)
def clean_cart():
    requests.delete(CLEAR_URL, headers=H)
    yield
    requests.delete(CLEAR_URL, headers=H)


def add_items_worth(target_value):
    """Helper: add enough apples (price=120) to reach target_value."""
    qty = max(1, int(target_value / 120) + 1)
    requests.post(ADD_URL, headers=JH,
                  json={"product_id": PRODUCT_APPLE, "quantity": qty})


class TestCouponApply:

    def test_TC_CPN_01_valid_fixed_coupon(self):
        """
        BONUS75: FIXED $75 off when cart ≥ $750.
        Add ~7 apples (7×120=840). Apply BONUS75. Discount must be exactly 75.
        """
        add_items_worth(800)
        r = requests.post(APPLY_URL, headers=JH,
                          json={"coupon_code": COUPON_VALID_FIXED})
        assert r.status_code == 200, (
            f"Expected 200 for valid coupon, got {r.status_code}: {r.text}"
        )
        data = r.json()
        discount = data.get("discount", data.get("discount_amount"))
        assert discount == 75, (
            f"BUG: Expected FIXED discount of 75, got {discount}"
        )

    def test_TC_CPN_02_valid_percent_coupon(self):
        """
        FIRSTORDER: 15% off, min $200, max $150.
        Add 3 apples (360). Expected discount = 360 × 0.15 = 54 (under cap).
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 3})
        r = requests.post(APPLY_URL, headers=JH,
                          json={"coupon_code": COUPON_VALID_PERCENT})
        assert r.status_code == 200, (
            f"Expected 200 for valid percent coupon, got {r.status_code}: {r.text}"
        )
        data = r.json()
        discount = data.get("discount", data.get("discount_amount"))
        expected = round(360 * 0.15, 2)  # 54.0
        assert discount == expected, (
            f"BUG: Expected 15% of 360 = {expected}, got {discount}"
        )

    def test_TC_CPN_03_expired_coupon_rejected(self):
        """
        EXPIRED100 expired on Feb 28 2026. Applying it must be rejected.
        If the server accepts it, expired coupons are not validated.
        """
        add_items_worth(1100)
        r = requests.post(APPLY_URL, headers=JH,
                          json={"coupon_code": COUPON_EXPIRED})
        assert r.status_code == 400, (
            f"BUG: Expired coupon EXPIRED100 was accepted! Got {r.status_code}"
        )

    def test_TC_CPN_04_cart_below_minimum_value_rejected(self):
        """
        BONUS75 requires min cart = $750.
        Add only 1 apple ($120) → must be rejected.
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 1})
        r = requests.post(APPLY_URL, headers=JH,
                          json={"coupon_code": COUPON_VALID_FIXED})
        assert r.status_code == 400, (
            f"Expected 400 when cart < min_cart_value, got {r.status_code}"
        )

    def test_TC_CPN_05_percent_coupon_discount_capped(self):
        """
        LOYALTY20: 20% off, min $600, max discount = $180.
        Add 10 apples (10×120=1200). 20% of 1200 = 240 → must be capped at 180.
        If discount comes out as 240, the cap is not enforced.
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 10})
        r = requests.post(APPLY_URL, headers=JH,
                          json={"coupon_code": COUPON_VALID_CAP})
        assert r.status_code == 200, (
            f"Expected 200 for LOYALTY20, got {r.status_code}: {r.text}"
        )
        data = r.json()
        discount = data.get("discount", data.get("discount_amount"))
        assert discount <= 180, (
            f"BUG: Discount cap not enforced! Got {discount}, max should be 180"
        )
        assert discount == 180, (
            f"Expected capped discount of 180, got {discount}"
        )

    def test_TC_CPN_06_invalid_coupon_code_rejected(self):
        """Applying a coupon code that doesn't exist must fail."""
        add_items_worth(500)
        r = requests.post(APPLY_URL, headers=JH,
                          json={"coupon_code": "NOTAREALCODE123"})
        assert r.status_code in (400, 404), (
            f"Expected 400/404 for invalid coupon code, got {r.status_code}"
        )
