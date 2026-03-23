"""
test_admin_collections.py — Tests for Admin Collection Endpoints.

Endpoints:
  GET /api/v1/admin/carts
  GET /api/v1/admin/orders
  GET /api/v1/admin/products
  GET /api/v1/admin/coupons
  GET /api/v1/admin/tickets
  GET /api/v1/admin/addresses

For each endpoint, three equivalence classes are tested:
  EC1 — Valid request with correct X-Roll-Number           → 200
  EC2 — Missing X-Roll-Number header                       → 401
  EC3 — Invalid (non-integer) X-Roll-Number header         → 400

Additionally, data-specific assertions verify:
  - admin/products includes inactive products
  - admin/coupons includes expired coupons
  - admin/orders includes payment_status and order_status fields
  - admin/tickets includes tickets of all statuses (OPEN/IN_PROGRESS/CLOSED)
  - admin/addresses includes all label types (HOME/OFFICE/OTHER)
  - admin/carts includes items list and total field
"""

import requests
import pytest
from conftest import BASE_URL, admin_headers


# ─── Parametrised equivalence-class tests ─────────────────────────────────────

ADMIN_ENDPOINTS = [
    "admin/carts",
    "admin/orders",
    "admin/products",
    "admin/coupons",
    "admin/tickets",
    "admin/addresses",
]


class TestAdminCollectionsAuth:
    """EC1/EC2/EC3 for every admin collection endpoint."""

    @pytest.mark.parametrize("ep", ADMIN_ENDPOINTS)
    def test_valid_request_returns_200(self, ep):
        """EC1: Valid X-Roll-Number → 200 and JSON array."""
        r = requests.get(f"{BASE_URL}/{ep}", headers=admin_headers())
        assert r.status_code == 200, f"{ep}: expected 200, got {r.status_code}"
        assert isinstance(r.json(), list), f"{ep}: expected list, got {type(r.json()).__name__}"

    @pytest.mark.parametrize("ep", ADMIN_ENDPOINTS)
    def test_missing_roll_number_returns_401(self, ep):
        """EC2: No X-Roll-Number header → 401."""
        r = requests.get(f"{BASE_URL}/{ep}")
        assert r.status_code == 401, f"{ep}: expected 401, got {r.status_code}"

    @pytest.mark.parametrize("ep", ADMIN_ENDPOINTS)
    def test_invalid_roll_number_returns_400(self, ep):
        """EC3: Non-integer X-Roll-Number → 400."""
        r = requests.get(f"{BASE_URL}/{ep}", headers={"X-Roll-Number": "abc"})
        assert r.status_code == 400, f"{ep}: expected 400, got {r.status_code}"


# ─── Data-specific assertions ─────────────────────────────────────────────────

class TestAdminProducts:

    def test_includes_inactive_products(self):
        """admin/products must return inactive products (is_active=false)."""
        r = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers())
        products = r.json()
        inactive = [p for p in products if not p.get("is_active", True)]
        assert len(inactive) > 0, "No inactive products returned — admin should see all"

    def test_product_has_required_fields(self):
        """Each product must include product_id, name, category, price, stock_quantity, is_active."""
        r = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers())
        sample = r.json()[0]
        for field in ("product_id", "name", "category", "price", "stock_quantity", "is_active"):
            assert field in sample, f"Missing field '{field}' in admin product"


class TestAdminCoupons:

    def test_includes_expired_coupons(self):
        """admin/coupons must return expired coupons."""
        r = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers())
        coupons = r.json()
        expired = [c for c in coupons if c.get("expiry_date", "9999") < "2026-03-23"]
        assert len(expired) > 0, "No expired coupons returned — admin should see all"

    def test_coupon_has_required_fields(self):
        """Each coupon must include coupon_code, discount_type, discount_value, min_cart_value, expiry_date."""
        r = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers())
        sample = r.json()[0]
        for field in ("coupon_code", "discount_type", "discount_value", "min_cart_value", "expiry_date"):
            assert field in sample, f"Missing field '{field}' in admin coupon"


class TestAdminOrders:

    def test_order_has_payment_and_order_status(self):
        """Each order must include payment_status and order_status."""
        r = requests.get(f"{BASE_URL}/admin/orders", headers=admin_headers())
        sample = r.json()[0]
        for field in ("order_id", "payment_status", "order_status"):
            assert field in sample, f"Missing field '{field}' in admin order"


class TestAdminTickets:

    def test_includes_all_statuses(self):
        """admin/tickets must include tickets of all statuses."""
        r = requests.get(f"{BASE_URL}/admin/tickets", headers=admin_headers())
        tickets = r.json()
        statuses = set(t.get("status") for t in tickets)
        for s in ("OPEN", "IN_PROGRESS", "CLOSED"):
            assert s in statuses, f"Status '{s}' not found in admin tickets"

    def test_ticket_has_required_fields(self):
        """Each ticket must include ticket_id, user_id, status, subject, message."""
        r = requests.get(f"{BASE_URL}/admin/tickets", headers=admin_headers())
        sample = r.json()[0]
        for field in ("ticket_id", "user_id", "status", "subject", "message"):
            assert field in sample, f"Missing field '{field}' in admin ticket"


class TestAdminAddresses:

    def test_includes_all_label_types(self):
        """admin/addresses must include HOME, OFFICE, and OTHER labels."""
        r = requests.get(f"{BASE_URL}/admin/addresses", headers=admin_headers())
        addresses = r.json()
        labels = set(a.get("label") for a in addresses)
        for lbl in ("HOME", "OFFICE", "OTHER"):
            assert lbl in labels, f"Label '{lbl}' not found in admin addresses"

    def test_address_has_required_fields(self):
        """Each address must include address_id, user_id, label, street, city, pincode, is_default."""
        r = requests.get(f"{BASE_URL}/admin/addresses", headers=admin_headers())
        sample = r.json()[0]
        for field in ("address_id", "user_id", "label", "street", "city", "pincode", "is_default"):
            assert field in sample, f"Missing field '{field}' in admin address"


class TestAdminCarts:

    def test_cart_has_items_and_total(self):
        """Each cart must include items (list) and total."""
        r = requests.get(f"{BASE_URL}/admin/carts", headers=admin_headers())
        sample = r.json()[0]
        assert "items" in sample, "Missing 'items' in admin cart"
        assert "total" in sample, "Missing 'total' in admin cart"
