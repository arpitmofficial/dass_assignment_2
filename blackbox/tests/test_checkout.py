"""
test_checkout.py — Tests for Checkout API.

Endpoint:
  POST /api/v1/checkout   Body: {"payment_method": "COD"|"WALLET"|"CARD"}

Test Cases:
  TC-CHK-01: Checkout with CARD → payment_status=PAID               → 200
  TC-CHK-02: Checkout with COD → payment_status=PENDING             → 200
  TC-CHK-03: Checkout with WALLET → payment_status=PENDING          → 200
  TC-CHK-04: Checkout with invalid method (CASH) → 400              → 400
  TC-CHK-05: Checkout with empty cart → 400                         → 400
  TC-CHK-06: COD blocked when order total > 5000                    → 400
  TC-CHK-07: GST is exactly 5% and added only once                  → verify

Justification: Checkout is the final, irreversible step. Wrong payment
status, incorrect GST, or allowing COD on large orders are revenue bugs.
"""

import requests
import pytest
from conftest import (
    BASE_URL, PRODUCT_APPLE, PRODUCT_MANGO,
    user_headers, json_headers
)

CHECKOUT_URL = f"{BASE_URL}/checkout"
ADD_URL      = f"{BASE_URL}/cart/add"
CLEAR_URL    = f"{BASE_URL}/cart/clear"
CART_URL     = f"{BASE_URL}/cart"

# Use a dedicated user for checkout (user 20)
UID = 20
H   = user_headers(UID)
JH  = json_headers(UID)


@pytest.fixture(autouse=True)
def clean_cart():
    requests.delete(CLEAR_URL, headers=H)
    yield
    requests.delete(CLEAR_URL, headers=H)


class TestCheckoutPaymentMethods:

    def test_TC_CHK_01_card_payment_status_is_paid(self):
        """
        CARD payments must result in order with payment_status=PAID immediately.
        Doc: 'When paying with CARD, it starts as PAID.'
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 1})
        r = requests.post(CHECKOUT_URL, headers=JH,
                          json={"payment_method": "CARD"})
        assert r.status_code == 200, f"Checkout failed: {r.status_code} {r.text}"
        data = r.json()
        order = data.get("order", data)
        assert order.get("payment_status") == "PAID", (
            f"BUG: CARD checkout should set payment_status=PAID, "
            f"got {order.get('payment_status')}"
        )

    def test_TC_CHK_02_cod_payment_status_is_pending(self):
        """COD payments must result in order with payment_status=PENDING."""
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 1})
        r = requests.post(CHECKOUT_URL, headers=JH,
                          json={"payment_method": "COD"})
        assert r.status_code == 200, f"COD checkout failed: {r.status_code}"
        data = r.json()
        order = data.get("order", data)
        assert order.get("payment_status") == "PENDING", (
            f"BUG: COD should have payment_status=PENDING, got {order.get('payment_status')}"
        )

    def test_TC_CHK_04_invalid_payment_method_rejected(self):
        """Unknown payment method 'CASH' must return 400."""
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 1})
        r = requests.post(CHECKOUT_URL, headers=JH,
                          json={"payment_method": "CASH"})
        assert r.status_code == 400, (
            f"Expected 400 for invalid payment_method CASH, got {r.status_code}"
        )

    def test_TC_CHK_05_empty_cart_checkout_rejected(self):
        """Checking out with an empty cart must return 400."""
        r = requests.post(CHECKOUT_URL, headers=JH,
                          json={"payment_method": "CARD"})
        assert r.status_code == 400, (
            f"Expected 400 for empty cart checkout, got {r.status_code}"
        )

    def test_TC_CHK_06_cod_blocked_above_5000(self):
        """
        Doc: 'COD is not allowed if the order total is more than 5000.'
        Add enough items to exceed 5000: 43 × Mango (250) = 10,750. 
        With 5% GST: 10,750 × 1.05 = 11,287.5 — well over 5000.
        COD must be rejected.
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_MANGO, "quantity": 21})
        r = requests.post(CHECKOUT_URL, headers=JH,
                          json={"payment_method": "COD"})
        assert r.status_code == 400, (
            f"BUG: COD was allowed on order > 5000! Got {r.status_code}"
        )

    def test_TC_CHK_07_gst_is_5_percent(self):
        """
        GST must be exactly 5% of the subtotal and added only once.
        Add 2 × Apple (price=120) → subtotal = 240, GST = 12, total = 252.
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 2})
        r = requests.post(CHECKOUT_URL, headers=JH,
                          json={"payment_method": "CARD"})
        assert r.status_code == 200
        data = r.json()
        order = data.get("order", data)
        subtotal = order.get("subtotal", order.get("cart_total"))
        total    = order.get("total", order.get("order_total"))
        if subtotal and total:
            expected_total = round(subtotal * 1.05, 2)
            assert abs(total - expected_total) < 0.01, (
                f"BUG: GST calculation wrong. Subtotal={subtotal}, "
                f"expected total={expected_total}, got total={total}. "
                "GST may be wrong or applied multiple times!"
            )
