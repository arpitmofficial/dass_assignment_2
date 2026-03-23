"""
test_wrong_types.py — Tests for wrong data types in request fields.

The assignment requires testing 'Wrong data types' as a category.
These tests send the correct fields but with the wrong type (e.g., string
where an integer is expected), verifying the API rejects them with 400.

Test Cases:
  TC-WT-01: POST cart/add — quantity as string ("two")              → 400
  TC-WT-02: POST cart/add — product_id as string ("abc")            → 400
  TC-WT-03: POST cart/add — quantity as float (1.5)                 → 400
  TC-WT-04: POST wallet/add — amount as string ("hundred")          → 400
  TC-WT-05: POST wallet/pay — amount as boolean (true)              → 400
  TC-WT-06: POST checkout — payment_method as integer (1)           → 400
  TC-WT-07: POST reviews — rating as string ("five")                → 400
  TC-WT-08: POST reviews — rating as float (4.5)                    → 400
  TC-WT-09: POST addresses — pincode as integer (500001)            → 400 (must be string)
  TC-WT-10: POST support/ticket — subject as integer (123)          → 400
  TC-WT-11: PUT profile — phone as integer (9876543210)             → 400 (must be string)
  TC-WT-12: POST coupon/apply — coupon_code as integer (75)         → 400

Justification: Type safety is critical in financial systems. If the server
accepts a string "100" for amount and interprets it as 100, that might work —
but "abc" must not silently become 0 or crash the server. The server must
validate types and return 400 for all type mismatches.
"""

import requests
from conftest import BASE_URL, PRODUCT_APPLE, user_headers, json_headers

# Use user 16 for type error tests
UID = 16
H   = user_headers(UID)
JH  = json_headers(UID)

ADD_URL      = f"{BASE_URL}/cart/add"
CHECKOUT_URL = f"{BASE_URL}/checkout"
COUPON_URL   = f"{BASE_URL}/coupon/apply"
WALLET_ADD   = f"{BASE_URL}/wallet/add"
WALLET_PAY   = f"{BASE_URL}/wallet/pay"
TICKET_URL   = f"{BASE_URL}/support/ticket"
ADDR_URL     = f"{BASE_URL}/addresses"
PROFILE_URL  = f"{BASE_URL}/profile"
REVIEW_URL   = f"{BASE_URL}/products/{PRODUCT_APPLE}/reviews"
CLEAR_URL    = f"{BASE_URL}/cart/clear"


class TestWrongTypesCart:

    def test_TC_WT_01_quantity_as_string_rejected(self):
        """Quantity must be an integer. Sending a word string must return 400."""
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": PRODUCT_APPLE, "quantity": "two"})
        assert r.status_code == 400, (
            f"Expected 400 for quantity='two' (string), got {r.status_code}"
        )

    def test_TC_WT_02_product_id_as_string_rejected(self):
        """product_id must be an integer. Sending an alphabetic string must return 400."""
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": "abc", "quantity": 1})
        assert r.status_code == 400, (
            f"Expected 400 for product_id='abc' (string), got {r.status_code}"
        )

    def test_TC_WT_03_quantity_as_float_rejected(self):
        """Quantity must be a whole integer. A float like 1.5 must be rejected."""
        r = requests.post(ADD_URL, headers=JH,
                          json={"product_id": PRODUCT_APPLE, "quantity": 1.5})
        assert r.status_code == 400, (
            f"Expected 400 for quantity=1.5 (float), got {r.status_code}"
        )


class TestWrongTypesWallet:

    def test_TC_WT_04_wallet_add_amount_as_string(self):
        """Amount must be numeric. Sending 'hundred' as string must return 400."""
        r = requests.post(WALLET_ADD, headers=JH,
                          json={"amount": "hundred"})
        assert r.status_code == 400, (
            f"Expected 400 for amount='hundred', got {r.status_code}"
        )

    def test_TC_WT_05_wallet_pay_amount_as_boolean(self):
        """Amount must be a number. Sending boolean true must return 400."""
        r = requests.post(WALLET_PAY, headers=JH,
                          json={"amount": True})
        assert r.status_code == 400, (
            f"Expected 400 for amount=True (boolean), got {r.status_code}"
        )


class TestWrongTypesCheckout:

    def test_TC_WT_06_payment_method_as_integer(self):
        """payment_method must be a string. Sending integer 1 must return 400."""
        requests.post(ADD_URL, headers=JH,
                      json={"product_id": PRODUCT_APPLE, "quantity": 1})
        r = requests.post(CHECKOUT_URL, headers=JH,
                          json={"payment_method": 1})
        assert r.status_code == 400, (
            f"Expected 400 for payment_method=1 (integer), got {r.status_code}"
        )
        requests.delete(CLEAR_URL, headers=H)


class TestWrongTypesReviews:

    def test_TC_WT_07_rating_as_string_rejected(self):
        """Rating must be an integer 1–5. String 'five' must return 400."""
        r = requests.post(REVIEW_URL, headers=JH,
                          json={"rating": "five", "comment": "Test"})
        assert r.status_code == 400, (
            f"Expected 400 for rating='five' (string), got {r.status_code}"
        )

    def test_TC_WT_08_rating_as_float_rejected(self):
        """Rating must be a whole integer. Float 4.5 must return 400."""
        r = requests.post(REVIEW_URL, headers=JH,
                          json={"rating": 4.5, "comment": "Test"})
        assert r.status_code == 400, (
            f"Expected 400 for rating=4.5 (float), got {r.status_code}"
        )


class TestWrongTypesAddresses:

    def test_TC_WT_09_pincode_as_integer_rejected(self):
        """Pincode must be a 6-digit string. Sending as integer (no leading zero support) must be 400."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME",
            "street": "123 Main Street",
            "city": "Hyderabad",
            "pincode": 500001,   # integer instead of string "500001"
            "is_default": False
        })
        assert r.status_code == 400, (
            f"Expected 400 for pincode as integer, got {r.status_code}"
        )


class TestWrongTypesTickets:

    def test_TC_WT_10_subject_as_integer_rejected(self):
        """Subject must be a string. Sending an integer must return 400."""
        r = requests.post(TICKET_URL, headers=JH,
                          json={"subject": 12345, "message": "Valid message here."})
        assert r.status_code == 400, (
            f"Expected 400 for subject=12345 (integer), got {r.status_code}"
        )


class TestWrongTypesProfile:

    def test_TC_WT_11_phone_as_integer_rejected(self):
        """Phone must be a string of exactly 10 digits. Integer may lose leading zeros."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "Valid Name", "phone": 9876543210})
        assert r.status_code == 400, (
            f"Expected 400 for phone as integer, got {r.status_code}"
        )


class TestWrongTypesCoupon:

    def test_TC_WT_12_coupon_code_as_integer_rejected(self):
        """coupon_code must be a string. Sending integer 75 must return 400."""
        r = requests.post(COUPON_URL, headers=JH,
                          json={"coupon_code": 75})
        assert r.status_code == 400, (
            f"Expected 400 for coupon_code=75 (integer), got {r.status_code}"
        )
