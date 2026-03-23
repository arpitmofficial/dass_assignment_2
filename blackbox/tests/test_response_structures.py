"""
test_response_structures.py — JSON response structure verification.

The assignment requires: 'Your automated tests should verify:
  - Proper JSON response structures'

These tests verify that every major endpoint returns a proper JSON response 
with the expected fields. They do NOT check values — only that the shape
of the response matches what the API documentation describes.

Test Cases:
  TC-STR-01: GET /admin/users returns list of objects with required user fields
  TC-STR-02: GET /admin/products returns list with product fields
  TC-STR-03: GET /admin/coupons returns list with coupon fields
  TC-STR-04: GET /admin/orders returns list with order fields
  TC-STR-05: GET /profile returns user object with expected fields
  TC-STR-06: GET /products returns list of products with correct fields
  TC-STR-07: GET /products/{id} returns single product with all fields
  TC-STR-08: GET /cart returns object with 'items' and 'total' fields
  TC-STR-09: GET /wallet returns object with balance field
  TC-STR-10: GET /loyalty returns object with points field
  TC-STR-11: GET /orders returns a list (possibly empty)
  TC-STR-12: GET /addresses returns a list
  TC-STR-13: GET /support/tickets returns a list
  TC-STR-14: GET /products/{id}/reviews returns object with average_rating
  TC-STR-15: POST /cart/add returns success response (200/201)
  TC-STR-16: POST /addresses returns response with address_id

Justification: Even when status code is 200, if the JSON structure is wrong
(missing fields, wrong field names), clients will crash. These tests catch
structural regressions where an endpoint changes its response format.
"""

import requests
import pytest
from conftest import (
    BASE_URL, PRODUCT_APPLE, PRODUCT_BANANA,
    admin_headers, user_headers, json_headers
)

# Use user 80 for structure tests (isolated, no side effects)
UID = 80
H   = user_headers(UID)
JH  = json_headers(UID)
AH  = admin_headers()


class TestAdminResponseStructures:

    def test_TC_STR_01_admin_users_has_user_fields(self):
        """
        GET /admin/users must return a list where each user object has:
        user_id, name, email, phone, wallet_balance, loyalty_points
        """
        r = requests.get(f"{BASE_URL}/admin/users", headers=AH)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0
        user = data[0]
        for field in ["user_id", "name", "email", "phone", "wallet_balance", "loyalty_points"]:
            assert field in user, f"Missing field '{field}' in admin user response"

    def test_TC_STR_02_admin_products_has_product_fields(self):
        """
        GET /admin/products must return a list where each product has:
        product_id, name, category, price, stock_quantity, is_active
        """
        r = requests.get(f"{BASE_URL}/admin/products", headers=AH)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0
        prod = data[0]
        for field in ["product_id", "name", "category", "price", "stock_quantity", "is_active"]:
            assert field in prod, f"Missing field '{field}' in admin product response"

    def test_TC_STR_03_admin_coupons_has_coupon_fields(self):
        """
        GET /admin/coupons must return a list with:
        coupon_code, discount_type, discount_value, min_cart_value, expiry_date
        """
        r = requests.get(f"{BASE_URL}/admin/coupons", headers=AH)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0
        coupon = data[0]
        for field in ["coupon_code", "discount_type", "discount_value",
                      "min_cart_value", "expiry_date"]:
            assert field in coupon, f"Missing field '{field}' in coupon response"

    def test_TC_STR_04_admin_orders_returns_list(self):
        """GET /admin/orders must return a JSON list."""
        r = requests.get(f"{BASE_URL}/admin/orders", headers=AH)
        assert r.status_code == 200
        assert isinstance(r.json(), list), "Expected list of orders"


class TestUserEndpointStructures:

    def test_TC_STR_05_profile_has_expected_fields(self):
        """
        GET /profile must return user object with at minimum:
        user_id, name, email, phone
        """
        r = requests.get(f"{BASE_URL}/profile", headers=H)
        assert r.status_code == 200
        data = r.json()
        for field in ["user_id", "name", "email", "phone"]:
            assert field in data, f"Missing field '{field}' in profile response"

    def test_TC_STR_06_products_list_has_correct_fields(self):
        """
        GET /products must return a list where each item has:
        product_id, name, category, price, stock_quantity
        """
        r = requests.get(f"{BASE_URL}/products", headers=H)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0
        for field in ["product_id", "name", "category", "price", "stock_quantity"]:
            assert field in data[0], f"Missing field '{field}' in product list item"

    def test_TC_STR_07_product_detail_has_all_fields(self):
        """
        GET /products/{id} must return a single product object with all fields.
        """
        r = requests.get(f"{BASE_URL}/products/{PRODUCT_APPLE}", headers=H)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict), "Expected a product object (dict)"
        for field in ["product_id", "name", "category", "price", "stock_quantity"]:
            assert field in data, f"Missing field '{field}' in product detail"

    def test_TC_STR_08_cart_has_items_and_total(self):
        """
        GET /cart must return an object that contains 'items' (a list)
        and some form of total field.
        """
        r = requests.get(f"{BASE_URL}/cart", headers=H)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict), "Cart response should be an object"
        # Items field should be a list
        items = data.get("items", None)
        assert items is not None, "Cart response missing 'items' field"
        assert isinstance(items, list), "'items' should be a list"
        # Total should exist (either 'total' or 'cart_total')
        has_total = "total" in data or "cart_total" in data
        assert has_total, "Cart response missing 'total' or 'cart_total' field"

    def test_TC_STR_09_wallet_has_balance_field(self):
        """GET /wallet must return an object with a balance field."""
        r = requests.get(f"{BASE_URL}/wallet", headers=H)
        assert r.status_code == 200
        data = r.json()
        has_balance = "balance" in data or "wallet_balance" in data
        assert has_balance, "Wallet response missing balance field"

    def test_TC_STR_10_loyalty_has_points_field(self):
        """GET /loyalty must return an object with a loyalty points field."""
        r = requests.get(f"{BASE_URL}/loyalty", headers=H)
        assert r.status_code == 200
        data = r.json()
        has_points = "points" in data or "loyalty_points" in data
        assert has_points, f"Loyalty response missing points field. Got: {list(data.keys())}"

    def test_TC_STR_11_orders_returns_list(self):
        """GET /orders must return a JSON list (may be empty)."""
        r = requests.get(f"{BASE_URL}/orders", headers=H)
        assert r.status_code == 200
        assert isinstance(r.json(), list), "Orders response should be a list"

    def test_TC_STR_12_addresses_returns_list(self):
        """GET /addresses must return a JSON list (may be empty)."""
        r = requests.get(f"{BASE_URL}/addresses", headers=H)
        assert r.status_code == 200
        assert isinstance(r.json(), list), "Addresses response should be a list"

    def test_TC_STR_13_support_tickets_returns_list(self):
        """GET /support/tickets must return a JSON list."""
        r = requests.get(f"{BASE_URL}/support/tickets", headers=H)
        assert r.status_code == 200
        assert isinstance(r.json(), list), "Tickets response should be a list"

    def test_TC_STR_14_reviews_has_average_rating(self):
        """
        GET /products/{id}/reviews must return an object with
        'average_rating' and 'reviews' (a list).
        """
        r = requests.get(f"{BASE_URL}/products/{PRODUCT_APPLE}/reviews", headers=H)
        assert r.status_code == 200
        data = r.json()
        has_avg = "average_rating" in data or "avg_rating" in data
        assert has_avg, f"Reviews response missing average_rating. Got keys: {list(data.keys())}"
        reviews = data.get("reviews", data.get("data"))
        assert isinstance(reviews, list), "Reviews field should be a list"

    def test_TC_STR_15_cart_add_returns_success_message(self):
        """POST /cart/add success response must be a JSON object (not empty)."""
        r = requests.post(f"{BASE_URL}/cart/add", headers=JH,
                          json={"product_id": PRODUCT_APPLE, "quantity": 1})
        assert r.status_code in (200, 201)
        assert r.headers.get("Content-Type", "").startswith("application/json"), (
            "Response must be JSON"
        )
        data = r.json()
        assert isinstance(data, dict), "Cart add response should be a JSON object"
        requests.delete(f"{BASE_URL}/cart/clear", headers=H)

    def test_TC_STR_16_post_address_returns_address_id(self):
        """POST /addresses success response must include an address_id."""
        r = requests.post(f"{BASE_URL}/addresses", headers=JH, json={
            "label": "OTHER",
            "street": "Structure Test Street",
            "city": "Pune",
            "pincode": "411001",
            "is_default": False
        })
        assert r.status_code in (200, 201)
        data = r.json()
        addr = data.get("address", data)
        assert "address_id" in addr, (
            f"POST /addresses response must include address_id. Got: {list(addr.keys())}"
        )
