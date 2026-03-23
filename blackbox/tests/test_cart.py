"""
test_cart.py — Tests for Cart API.

Endpoints:
  GET    /api/v1/cart
  POST   /api/v1/cart/add
  POST   /api/v1/cart/update
  POST   /api/v1/cart/remove
  DELETE /api/v1/cart/clear

Test Cases:
  TC-CART-01: Get empty cart returns 200 and empty items             → 200
  TC-CART-02: Add valid product with qty=2                           → 200/201
  TC-CART-03: Add qty=0 must be rejected                            → 400
  TC-CART-04: Add negative quantity must be rejected                 → 400
  TC-CART-05: Add non-existent product returns 404                  → 404
  TC-CART-06: Add same product twice ACCUMULATES (not replaces)     → verify
  TC-CART-07: Each cart item shows correct subtotal (qty × price)   → verify
  TC-CART-08: Cart total = sum of ALL item subtotals                 → verify (off-by-one bug)
  TC-CART-09: Remove item not in cart returns 404                    → 404
  TC-CART-10: Update cart item with qty=0 must be rejected           → 400
  TC-CART-11: Add more than stock quantity returns 400               → 400
  TC-CART-12: Clear cart empties the cart                            → verify

Justification: Cart is the core of the system. Off-by-one errors in
totals and incorrect quantity accumulation directly cause wrong charges.
"""

import requests
import pytest
from conftest import (
    BASE_URL, PRODUCT_APPLE, PRODUCT_BANANA, PRODUCT_MANGO,
    user_headers, json_headers
)

CART_URL    = f"{BASE_URL}/cart"
ADD_URL     = f"{BASE_URL}/cart/add"
UPDATE_URL  = f"{BASE_URL}/cart/update"
REMOVE_URL  = f"{BASE_URL}/cart/remove"
CLEAR_URL   = f"{BASE_URL}/cart/clear"

# Use a dedicated user to isolate cart tests (user 10)
UID = 10
H   = user_headers(UID)
JH  = json_headers(UID)


@pytest.fixture(autouse=True)
def clean_cart():
    """Always start and end each test with an empty cart."""
    requests.delete(CLEAR_URL, headers=H)
    yield
    requests.delete(CLEAR_URL, headers=H)


class TestCartView:

    def test_TC_CART_01_get_empty_cart_returns_200(self):
        """GET /cart on an empty cart must return 200."""
        r = requests.get(CART_URL, headers=H)
        assert r.status_code == 200


class TestCartAdd:

    def test_TC_CART_02_add_valid_product(self):
        """Adding a valid product with qty=2 must succeed."""
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": PRODUCT_APPLE, "quantity": 2})
        assert r.status_code in (200, 201), (
            f"Expected 200/201 when adding valid product, got {r.status_code}: {r.text}"
        )

    def test_TC_CART_03_add_zero_quantity_rejected(self):
        """Adding qty=0 must return 400 — zero items makes no sense."""
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": PRODUCT_APPLE, "quantity": 0})
        assert r.status_code == 400, (
            f"Expected 400 for qty=0, got {r.status_code}"
        )

    def test_TC_CART_04_add_negative_quantity_rejected(self):
        """Adding qty=-1 must return 400."""
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": PRODUCT_APPLE, "quantity": -1})
        assert r.status_code == 400, (
            f"Expected 400 for negative qty, got {r.status_code}"
        )

    def test_TC_CART_05_add_nonexistent_product_returns_404(self):
        """Adding a product_id that doesn't exist must return 404."""
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": 999999, "quantity": 1})
        assert r.status_code == 404, (
            f"Expected 404 for non-existent product, got {r.status_code}"
        )

    def test_TC_CART_06_adding_same_product_twice_accumulates(self):
        """
        Adding the same product twice must ACCUMULATE quantities.
        Doc says: 'quantities are added together. The existing cart
        quantity is not replaced.'
        Add 2, then add 3 → total must be 5, not 3.
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_BANANA, "quantity": 2})
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_BANANA, "quantity": 3})
        r = requests.get(CART_URL, headers=H)
        items = r.json().get("items", r.json())
        if isinstance(items, list):
            item = next((i for i in items if i["product_id"] == PRODUCT_BANANA), None)
        else:
            item = None
        assert item is not None, "Product not found in cart after add"
        assert item["quantity"] == 5, (
            f"BUG: Expected accumulated qty=5, got {item['quantity']}. "
            "Cart replaced qty instead of adding!"
        )

    def test_TC_CART_11_add_more_than_stock_returns_400(self):
        """
        Adding a quantity higher than available stock must return 400.
        Product 5 (Mango) has stock_quantity=56. Request 999 units.
        """
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": PRODUCT_MANGO, "quantity": 999})
        assert r.status_code == 400, (
            f"Expected 400 for out-of-stock request, got {r.status_code}"
        )


class TestCartTotals:

    def test_TC_CART_07_item_subtotal_is_qty_times_price(self):
        """
        Each cart item subtotal must equal quantity × unit price.
        Add 3 × Apple (price=120), expect subtotal=360.
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 3})
        r = requests.get(CART_URL, headers=H)
        data = r.json()
        items = data.get("items", data)
        if isinstance(items, list):
            item = next((i for i in items if i["product_id"] == PRODUCT_APPLE), None)
            assert item is not None
            expected_subtotal = item["quantity"] * item["unit_price"] if "unit_price" in item else item["quantity"] * 120
            assert item.get("subtotal") == expected_subtotal, (
                f"BUG: Subtotal {item.get('subtotal')} != qty×price {expected_subtotal}"
            )

    def test_TC_CART_08_cart_total_includes_all_items(self):
        """
        Cart total must equal the sum of ALL item subtotals.
        This tests for the known off-by-one bug where the last item
        might be excluded from the total.
        Add 2 × Apple (120 each = 240) + 3 × Banana (40 each = 120)
        → total must be 360.
        """
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 2})
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_BANANA, "quantity": 3})
        r = requests.get(CART_URL, headers=H)
        data = r.json()

        items = data.get("items", [])
        cart_total = data.get("total", data.get("cart_total"))
        computed   = sum(i.get("subtotal", 0) for i in items)

        assert cart_total == computed, (
            f"BUG: Cart total {cart_total} != sum of subtotals {computed}. "
            "Possible off-by-one — last item excluded from total!"
        )


class TestCartRemoveUpdate:

    def test_TC_CART_09_remove_item_not_in_cart_returns_404(self):
        """Removing a product that is not in the cart must return 404."""
        r = requests.post(REMOVE_URL, headers=JH,
                          json={"product_id": 999999})
        assert r.status_code == 404, (
            f"Expected 404 for removing non-existent cart item, got {r.status_code}"
        )

    def test_TC_CART_10_update_with_zero_quantity_rejected(self):
        """Updating cart item quantity to 0 must be rejected with 400."""
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 2})
        r = requests.post(UPDATE_URL, headers=JH,
                          json={"product_id": PRODUCT_APPLE, "quantity": 0})
        assert r.status_code == 400, (
            f"Expected 400 for update qty=0, got {r.status_code}"
        )

    def test_TC_CART_12_clear_empties_cart(self):
        """After clearing, cart must be empty."""
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 1})
        requests.delete(CLEAR_URL, headers=H)
        r = requests.get(CART_URL, headers=H)
        data = r.json()
        items = data.get("items", data if isinstance(data, list) else [])
        assert len(items) == 0, (
            f"BUG: Cart not empty after clear. Still has {len(items)} items."
        )
