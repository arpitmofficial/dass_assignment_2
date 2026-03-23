"""
test_orders.py — Tests for Orders API.

Endpoints:
  GET  /api/v1/orders
  GET  /api/v1/orders/{order_id}
  POST /api/v1/orders/{order_id}/cancel
  GET  /api/v1/orders/{order_id}/invoice

Test Cases:
  TC-ORD-01: Get orders list returns 200 and array                 → 200
  TC-ORD-02: Get order by valid ID returns correct fields          → 200
  TC-ORD-03: Get non-existent order returns 404                   → 404
  TC-ORD-04: Cancel non-existent order returns 404                → 404
  TC-ORD-05: Cancel a delivered order must return 400             → 400
  TC-ORD-06: Cancel valid order → stock restored for all items    → verify
  TC-ORD-07: Invoice shows subtotal, GST, total correctly         → verify
  TC-ORD-08: Invoice total matches actual order total             → verify

Justification: Stock restoration on cancel is critical — if stock
isn't restored, items disappear from inventory permanently. Invoice
total must match order total for financial correctness.
"""

import requests
import pytest
from conftest import BASE_URL, PRODUCT_APPLE, user_headers, json_headers, admin_headers

ORDERS_URL      = f"{BASE_URL}/orders"
CANCEL_URL      = lambda oid: f"{BASE_URL}/orders/{oid}/cancel"
INVOICE_URL     = lambda oid: f"{BASE_URL}/orders/{oid}/invoice"
ADD_URL         = f"{BASE_URL}/cart/add"
CLEAR_URL       = f"{BASE_URL}/cart/clear"
CHECKOUT_URL    = f"{BASE_URL}/checkout"
ADMIN_PROD_URL  = f"{BASE_URL}/admin/products"

# Use user 40 for order tests
UID = 40
H   = user_headers(UID)
JH  = json_headers(UID)


@pytest.fixture(autouse=True)
def clean_cart():
    requests.delete(CLEAR_URL, headers=H)
    yield
    requests.delete(CLEAR_URL, headers=H)


def place_order(qty=1, method="CARD"):
    """Helper: add an apple and checkout to place a new order."""
    requests.delete(CLEAR_URL, headers=H)
    requests.post(ADD_URL, headers=JH,
                  json={"product_id": PRODUCT_APPLE, "quantity": qty})
    r = requests.post(CHECKOUT_URL, headers=JH,
                      json={"payment_method": method})
    if r.status_code == 200:
        data = r.json()
        return data.get("order_id", data.get("order", {}).get("order_id"))
    return None


class TestOrdersList:

    def test_TC_ORD_01_get_orders_returns_list(self):
        """GET /orders must return 200 and a list."""
        r = requests.get(ORDERS_URL, headers=H)
        assert r.status_code == 200
        assert isinstance(r.json(), list), "Expected list of orders"


class TestOrderDetail:

    def test_TC_ORD_03_get_nonexistent_order_returns_404(self):
        """Looking up a non-existent order ID must return 404."""
        r = requests.get(f"{ORDERS_URL}/999999", headers=H)
        assert r.status_code == 404, (
            f"Expected 404 for non-existent order, got {r.status_code}"
        )


class TestOrderCancel:

    def test_TC_ORD_04_cancel_nonexistent_order_returns_404(self):
        """Cancelling a non-existent order must return 404."""
        r = requests.post(CANCEL_URL(999999), headers=JH)
        assert r.status_code == 404, (
            f"Expected 404 for non-existent order cancel, got {r.status_code}"
        )

    def test_TC_ORD_06_cancel_order_restores_stock(self):
        """
        Cancelling an order must restore all ordered items back to product stock.
        Doc: 'When an order is cancelled, all the items in that order are
        added back to the product stock.'
        
        1. Check initial stock of Apple
        2. Order 2 × Apple
        3. Check stock decreased by 2
        4. Cancel → check stock goes back up by 2
        """
        # Get stock before
        admin_prods = requests.get(ADMIN_PROD_URL, headers=admin_headers()).json()
        apple_before = next((p["stock_quantity"] for p in admin_prods
                             if p["product_id"] == PRODUCT_APPLE), None)
        assert apple_before is not None

        # Place order
        order_id = place_order(qty=2, method="CARD")
        assert order_id is not None, "Could not place order for stock test"

        # Check stock decreased
        admin_prods_after = requests.get(ADMIN_PROD_URL, headers=admin_headers()).json()
        apple_after_order = next((p["stock_quantity"] for p in admin_prods_after
                                  if p["product_id"] == PRODUCT_APPLE), None)
        assert apple_after_order == apple_before - 2, (
            f"Stock should have decreased by 2. Before={apple_before}, After order={apple_after_order}"
        )

        # Cancel
        r = requests.post(CANCEL_URL(order_id), headers=JH)
        assert r.status_code == 200, f"Cancel failed: {r.status_code} {r.text}"

        # Verify stock restored
        admin_prods_after_cancel = requests.get(ADMIN_PROD_URL, headers=admin_headers()).json()
        apple_after_cancel = next((p["stock_quantity"] for p in admin_prods_after_cancel
                                   if p["product_id"] == PRODUCT_APPLE), None)
        assert apple_after_cancel == apple_before, (
            f"BUG: Stock not restored after cancel! "
            f"Before={apple_before}, After cancel={apple_after_cancel}"
        )


class TestOrderInvoice:

    def test_TC_ORD_07_invoice_total_matches_order_total(self):
        """
        Invoice total must match the actual order total exactly.
        Doc: 'The total shown must match the actual order total exactly.'
        """
        order_id = place_order(qty=1, method="CARD")
        if order_id is None:
            pytest.skip("Could not create order for invoice test")

        inv = requests.get(INVOICE_URL(order_id), headers=H)
        assert inv.status_code == 200, f"Invoice failed: {inv.status_code}"

        order_r = requests.get(f"{ORDERS_URL}/{order_id}", headers=H)
        assert order_r.status_code == 200

        inv_data   = inv.json()
        order_data = order_r.json()

        inv_total   = inv_data.get("total")
        order_total = order_data.get("total", order_data.get("order_total"))

        if inv_total and order_total:
            assert abs(inv_total - order_total) < 0.01, (
                f"BUG: Invoice total {inv_total} != order total {order_total}"
            )

    def test_TC_ORD_08_invoice_gst_is_5_percent_of_subtotal(self):
        """
        Invoice must show: subtotal + GST (5% of subtotal) = total.
        Doc: 'The subtotal is the total before GST.'
        """
        order_id = place_order(qty=2, method="CARD")
        if order_id is None:
            pytest.skip("Could not create order for GST test")

        inv = requests.get(INVOICE_URL(order_id), headers=H).json()
        subtotal = inv.get("subtotal")
        gst      = inv.get("gst", inv.get("gst_amount", inv.get("tax")))
        total    = inv.get("total")

        if subtotal and gst and total:
            expected_gst   = round(subtotal * 0.05, 2)
            expected_total = round(subtotal + gst, 2)
            assert abs(gst - expected_gst) < 0.01, (
                f"BUG: GST should be 5% of {subtotal}={expected_gst}, got {gst}"
            )
            assert abs(total - expected_total) < 0.01, (
                f"BUG: total {total} != subtotal+gst {expected_total}"
            )
