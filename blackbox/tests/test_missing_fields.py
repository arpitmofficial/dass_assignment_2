"""
test_missing_fields.py — Tests for missing required fields in request bodies.

The assignment requires testing 'Missing fields' as a category.
These tests send POST/PUT requests with required fields deliberately omitted,
verifying the API correctly returns 400 for each case.

Test Cases:
  TC-MF-01: POST cart/add — missing product_id                   → 400
  TC-MF-02: POST cart/add — missing quantity                     → 400
  TC-MF-03: POST cart/add — completely empty body                → 400
  TC-MF-04: POST checkout — missing payment_method               → 400
  TC-MF-05: POST coupon/apply — missing coupon_code              → 400
  TC-MF-06: POST wallet/add — missing amount                     → 400
  TC-MF-07: POST wallet/pay — missing amount                     → 400
  TC-MF-08: POST support/ticket — missing subject                → 400
  TC-MF-09: POST support/ticket — missing message                → 400
  TC-MF-10: POST addresses — missing street                      → 400
  TC-MF-11: POST addresses — missing pincode                     → 400
  TC-MF-12: POST addresses — missing label                       → 400
  TC-MF-13: PUT profile — missing name                           → 400
  TC-MF-14: PUT profile — missing phone                          → 400
  TC-MF-15: POST reviews — missing rating                        → 400
  TC-MF-16: POST reviews — missing comment                       → 400

Justification: Missing required fields are one of the most common sources
of API bugs. The server must return 400 for each missing field instead of
crashing (500) or silently accepting the request with null/default values.
"""

import requests
from conftest import BASE_URL, PRODUCT_APPLE, user_headers, json_headers

# Use user 15 for missing field tests
UID = 15
H   = user_headers(UID)
JH  = json_headers(UID)

ADD_URL      = f"{BASE_URL}/cart/add"
CLEAR_URL    = f"{BASE_URL}/cart/clear"
CHECKOUT_URL = f"{BASE_URL}/checkout"
COUPON_URL   = f"{BASE_URL}/coupon/apply"
WALLET_ADD   = f"{BASE_URL}/wallet/add"
WALLET_PAY   = f"{BASE_URL}/wallet/pay"
TICKET_URL   = f"{BASE_URL}/support/ticket"
ADDR_URL     = f"{BASE_URL}/addresses"
PROFILE_URL  = f"{BASE_URL}/profile"
REVIEW_URL   = f"{BASE_URL}/products/{PRODUCT_APPLE}/reviews"


class TestMissingCartFields:

    def test_TC_MF_01_cart_add_missing_product_id(self):
        """POST cart/add without product_id must return 400."""
        r = requests.post(ADD_URL, headers=JH, json={"quantity": 2})
        assert r.status_code == 400, (
            f"Expected 400 when product_id is missing, got {r.status_code}"
        )

    def test_TC_MF_02_cart_add_missing_quantity(self):
        """POST cart/add without quantity must return 400."""
        r = requests.post(ADD_URL, headers=JH, json={"product_id": PRODUCT_APPLE})
        assert r.status_code == 400, (
            f"Expected 400 when quantity is missing, got {r.status_code}"
        )

    def test_TC_MF_03_cart_add_empty_body(self):
        """POST cart/add with completely empty JSON body must return 400."""
        r = requests.post(ADD_URL, headers=JH, json={})
        assert r.status_code == 400, (
            f"Expected 400 for empty body, got {r.status_code}"
        )


class TestMissingCheckoutFields:

    def test_TC_MF_04_checkout_missing_payment_method(self):
        """POST checkout without payment_method must return 400."""
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 1})
        r = requests.post(CHECKOUT_URL, headers=JH, json={})
        assert r.status_code == 400, (
            f"Expected 400 when payment_method is missing, got {r.status_code}"
        )
        requests.delete(CLEAR_URL, headers=H)


class TestMissingCouponFields:

    def test_TC_MF_05_coupon_apply_missing_coupon_code(self):
        """POST coupon/apply without coupon_code must return 400."""
        r = requests.post(COUPON_URL, headers=JH, json={})
        assert r.status_code == 400, (
            f"Expected 400 when coupon_code is missing, got {r.status_code}"
        )


class TestMissingWalletFields:

    def test_TC_MF_06_wallet_add_missing_amount(self):
        """POST wallet/add without amount must return 400."""
        r = requests.post(WALLET_ADD, headers=JH, json={})
        assert r.status_code == 400, (
            f"Expected 400 when amount is missing in wallet/add, got {r.status_code}"
        )

    def test_TC_MF_07_wallet_pay_missing_amount(self):
        """POST wallet/pay without amount must return 400."""
        r = requests.post(WALLET_PAY, headers=JH, json={})
        assert r.status_code == 400, (
            f"Expected 400 when amount is missing in wallet/pay, got {r.status_code}"
        )


class TestMissingTicketFields:

    def test_TC_MF_08_ticket_missing_subject(self):
        """POST support/ticket without subject must return 400."""
        r = requests.post(TICKET_URL, headers=JH,
                          json={"message": "I need help."})
        assert r.status_code == 400, (
            f"Expected 400 when subject is missing, got {r.status_code}"
        )

    def test_TC_MF_09_ticket_missing_message(self):
        """POST support/ticket without message must return 400."""
        r = requests.post(TICKET_URL, headers=JH,
                          json={"subject": "Help needed"})
        assert r.status_code == 400, (
            f"Expected 400 when message is missing, got {r.status_code}"
        )


class TestMissingAddressFields:

    def test_TC_MF_10_address_missing_street(self):
        """POST addresses without street must return 400."""
        r = requests.post(ADDR_URL, headers=JH,
                          json={"label": "HOME", "city": "Hyderabad",
                                "pincode": "500001", "is_default": False})
        assert r.status_code == 400, (
            f"Expected 400 when street is missing, got {r.status_code}"
        )

    def test_TC_MF_11_address_missing_pincode(self):
        """POST addresses without pincode must return 400."""
        r = requests.post(ADDR_URL, headers=JH,
                          json={"label": "HOME", "street": "Main Street",
                                "city": "Hyderabad", "is_default": False})
        assert r.status_code == 400, (
            f"Expected 400 when pincode is missing, got {r.status_code}"
        )

    def test_TC_MF_12_address_missing_label(self):
        """POST addresses without label must return 400."""
        r = requests.post(ADDR_URL, headers=JH,
                          json={"street": "Main Street", "city": "Hyderabad",
                                "pincode": "500001", "is_default": False})
        assert r.status_code == 400, (
            f"Expected 400 when label is missing, got {r.status_code}"
        )


class TestMissingProfileFields:

    def test_TC_MF_13_profile_update_missing_name(self):
        """PUT profile without name must return 400."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"phone": "9876543210"})
        assert r.status_code == 400, (
            f"Expected 400 when name is missing, got {r.status_code}"
        )

    def test_TC_MF_14_profile_update_missing_phone(self):
        """PUT profile without phone must return 400."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "Valid Name"})
        assert r.status_code == 400, (
            f"Expected 400 when phone is missing, got {r.status_code}"
        )


class TestMissingReviewFields:

    def test_TC_MF_15_review_missing_rating(self):
        """POST review without rating must return 400."""
        r = requests.post(REVIEW_URL, headers=JH,
                          json={"comment": "Great product!"})
        assert r.status_code == 400, (
            f"Expected 400 when rating is missing, got {r.status_code}"
        )

    def test_TC_MF_16_review_missing_comment(self):
        """POST review without comment must return 400."""
        r = requests.post(REVIEW_URL, headers=JH,
                          json={"rating": 4})
        assert r.status_code == 400, (
            f"Expected 400 when comment is missing, got {r.status_code}"
        )
