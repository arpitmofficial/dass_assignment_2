"""
test_products.py — Tests for the Products API.

Endpoints:
  GET /api/v1/products                    → list all active products
  GET /api/v1/products/{product_id}       → get one product by ID

Test Cases:
  TC-PROD-01: List products returns only active products            → 200
  TC-PROD-02: Inactive product must NOT appear in the list          → verify
  TC-PROD-03: Get product by valid ID returns correct fields        → 200
  TC-PROD-04: Get product by non-existent ID returns 404           → 404
  TC-PROD-05: Price returned is exact (not rounded)                → verify
  TC-PROD-06: Filter by category=Fruits returns only Fruits        → verify
  TC-PROD-07: Filter by invalid category returns empty or 200      → no crash
  TC-PROD-08: Sort by price_asc returns ascending order            → verify
  TC-PROD-09: Sort by price_desc returns descending order          → verify
  TC-PROD-10: Search by name returns only matching products        → verify

Justification: Products are the foundation of the shopping system. If
inactive products are shown, users can add unavailable items to cart.
Price accuracy directly affects checkout totals.
"""

import requests
import pytest
from conftest import BASE_URL, PRODUCT_APPLE, PRODUCT_INACTIVE, admin_headers, user_headers

LIST_URL   = f"{BASE_URL}/products"
DETAIL_URL = lambda pid: f"{BASE_URL}/products/{pid}"
H = user_headers()


class TestProductList:

    def test_TC_PROD_01_list_returns_200_and_is_list(self):
        """Product list endpoint returns 200 and a JSON array."""
        r = requests.get(LIST_URL, headers=H)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list), "Expected a JSON array"
        assert len(data) > 0, "Product list must not be empty"

    def test_TC_PROD_02_inactive_product_not_in_list(self):
        """
        Inactive products must NOT appear in the public product list.
        Product 214 is marked is_active=False.
        If it appears in the list, it's a bug — users could add it to cart.
        """
        r = requests.get(LIST_URL, headers=H)
        assert r.status_code == 200
        ids = [p["product_id"] for p in r.json()]
        assert PRODUCT_INACTIVE not in ids, (
            f"BUG: Inactive product {PRODUCT_INACTIVE} appeared in the product list!"
        )

    def test_TC_PROD_03_all_active_in_list_have_correct_fields(self):
        """Every product in the list must have required fields."""
        r = requests.get(LIST_URL, headers=H)
        assert r.status_code == 200
        for p in r.json():
            assert "product_id" in p
            assert "name" in p
            assert "price" in p
            assert "category" in p
            assert "stock_quantity" in p

    def test_TC_PROD_05_price_is_exact_not_rounded(self):
        """
        Prices must be exact decimal values, not rounded integers.
        We cross-reference the public list price against the admin view.
        If admin shows 120.5 but list shows 120, that's a precision bug.
        """
        admin_r = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers())
        list_r  = requests.get(LIST_URL, headers=H)
        admin_map = {p["product_id"]: p["price"] for p in admin_r.json()}
        for p in list_r.json():
            pid = p["product_id"]
            if pid in admin_map:
                assert p["price"] == admin_map[pid], (
                    f"BUG: Product {pid} price mismatch — "
                    f"admin shows {admin_map[pid]}, list shows {p['price']}"
                )

    def test_TC_PROD_06_filter_by_category_fruits(self):
        """Filtering by category=Fruits returns only Fruits products."""
        r = requests.get(LIST_URL, headers=H, params={"category": "Fruits"})
        assert r.status_code == 200
        for p in r.json():
            assert p["category"] == "Fruits", (
                f"BUG: Product {p['product_id']} has category {p['category']}, expected Fruits"
            )

    def test_TC_PROD_07_filter_invalid_category_no_crash(self):
        """Filtering by a non-existent category must not crash the server."""
        r = requests.get(LIST_URL, headers=H, params={"category": "INVALID_CATEGORY_XYZ"})
        assert r.status_code in (200, 404), (
            f"Unexpected status {r.status_code} for invalid category filter"
        )

    def test_TC_PROD_08_sort_price_asc(self):
        """Products sorted by price ascending must be in non-decreasing order."""
        r = requests.get(LIST_URL, headers=H, params={"sort": "price_asc"})
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices), (
            f"BUG: Products not sorted ascending. Got: {prices[:5]}..."
        )

    def test_TC_PROD_09_sort_price_desc(self):
        """Products sorted by price descending must be in non-increasing order."""
        r = requests.get(LIST_URL, headers=H, params={"sort": "price_desc"})
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices, reverse=True), (
            f"BUG: Products not sorted descending. Got: {prices[:5]}..."
        )


class TestProductDetail:

    def test_TC_PROD_03_get_product_by_valid_id_returns_200(self):
        """Looking up an existing product by ID returns 200 with correct data."""
        r = requests.get(DETAIL_URL(PRODUCT_APPLE), headers=H)
        assert r.status_code == 200
        data = r.json()
        assert data["product_id"] == PRODUCT_APPLE
        assert "name" in data
        assert "price" in data

    def test_TC_PROD_04_get_nonexistent_product_returns_404(self):
        """Looking up a product ID that doesn't exist must return 404."""
        r = requests.get(DETAIL_URL(999999), headers=H)
        assert r.status_code == 404, (
            f"Expected 404 for non-existent product, got {r.status_code}"
        )
