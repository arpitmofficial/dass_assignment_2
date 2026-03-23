"""
test_profile_addresses.py — Tests for Profile and Addresses APIs.

Profile Endpoints:
  GET /api/v1/profile
  PUT /api/v1/profile  Body: {"name": str, "phone": str}

Address Endpoints:
  GET    /api/v1/addresses
  POST   /api/v1/addresses
  PUT    /api/v1/addresses/{address_id}
  DELETE /api/v1/addresses/{address_id}

Test Cases (Profile):
  TC-PRF-01: GET profile returns 200 with user data                   → 200
  TC-PRF-02: Update name with 1 char (below min=2) → 400             → 400
  TC-PRF-03: Update name with 51 chars (above max=50) → 400          → 400
  TC-PRF-04: Update phone with 9 digits (below 10) → 400             → 400
  TC-PRF-05: Update phone with 11 digits (above 10) → 400            → 400
  TC-PRF-06: Valid update (name 2-50 chars, phone 10 digits) → 200   → 200

Test Cases (Addresses):
  TC-ADDR-01: Add valid HOME address → 201 with address object        → 201
  TC-ADDR-02: Add address with invalid label (HOTEL) → 400           → 400
  TC-ADDR-03: Add address with short street (<5 chars) → 400         → 400
  TC-ADDR-04: Add address with pincode ≠ 6 digits → 400             → 400
  TC-ADDR-05: Only one address is default at a time                  → verify
  TC-ADDR-06: Update street and is_default only — label unchanged    → verify
  TC-ADDR-07: Delete non-existent address → 404                     → 404

Justification: Profile validation protects data integrity. Address
uniqueness of default ensures no billing confusion.
"""

import requests
import pytest
from conftest import BASE_URL, user_headers, json_headers

PROFILE_URL  = f"{BASE_URL}/profile"
ADDR_URL     = f"{BASE_URL}/addresses"
ADDR_ID_URL  = lambda aid: f"{BASE_URL}/addresses/{aid}"

# Use user 70 for profile/address tests
UID = 70
H   = user_headers(UID)
JH  = json_headers(UID)


class TestProfile:

    def test_TC_PRF_01_get_profile_returns_200(self):
        """GET /profile must return 200 with user data."""
        r = requests.get(PROFILE_URL, headers=H)
        assert r.status_code == 200
        data = r.json()
        assert "name" in data or "user_id" in data

    def test_TC_PRF_02_name_too_short_rejected(self):
        """Name with 1 character (below min=2) must return 400."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "A", "phone": "9876543210"})
        assert r.status_code == 400, (
            f"Expected 400 for name with 1 char, got {r.status_code}"
        )

    def test_TC_PRF_03_name_too_long_rejected(self):
        """Name with 51 characters (above max=50) must return 400."""
        long_name = "A" * 51
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": long_name, "phone": "9876543210"})
        assert r.status_code == 400, (
            f"Expected 400 for name with 51 chars, got {r.status_code}"
        )

    def test_TC_PRF_04_phone_9_digits_rejected(self):
        """Phone with 9 digits (below required 10) must return 400."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "Test User", "phone": "987654321"})
        assert r.status_code == 400, (
            f"Expected 400 for 9-digit phone, got {r.status_code}"
        )

    def test_TC_PRF_05_phone_11_digits_rejected(self):
        """Phone with 11 digits (above required 10) must return 400."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "Test User", "phone": "98765432101"})
        assert r.status_code == 400, (
            f"Expected 400 for 11-digit phone, got {r.status_code}"
        )

    def test_TC_PRF_06_valid_profile_update(self):
        """Valid name (2-50 chars) and phone (10 digits) must succeed."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "Valid Name", "phone": "9876543210"})
        assert r.status_code == 200, (
            f"Expected 200 for valid profile update, got {r.status_code}: {r.text}"
        )

    def test_TC_PRF_07_name_exact_min_boundary_accepted(self):
        """Name with exactly 2 chars (min boundary) must succeed."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "AB", "phone": "9876543210"})
        assert r.status_code == 200, (
            f"Expected 200 for name=2 chars (min boundary), got {r.status_code}"
        )

    def test_TC_PRF_08_name_exact_max_boundary_accepted(self):
        """Name with exactly 50 chars (max boundary) must succeed."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "A" * 50, "phone": "9876543210"})
        assert r.status_code == 200, (
            f"Expected 200 for name=50 chars (max boundary), got {r.status_code}"
        )

    def test_TC_PRF_09_empty_name_rejected(self):
        """Empty name string must return 400."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "", "phone": "9876543210"})
        assert r.status_code == 400, (
            f"Expected 400 for empty name, got {r.status_code}"
        )

    def test_TC_PRF_10_phone_with_letters_rejected(self):
        """Phone containing letters must return 400 — doc says 'exactly 10 digits'."""
        r = requests.put(PROFILE_URL, headers=JH,
                         json={"name": "Test User", "phone": "98765abcde"})
        assert r.status_code == 400, (
            f"Expected 400 for phone with letters, got {r.status_code}"
        )

    def test_TC_PRF_11_update_persists_on_get(self):
        """After a valid PUT, GET must return the updated values."""
        requests.put(PROFILE_URL, headers=JH,
                     json={"name": "PersistCheck", "phone": "1234567890"})
        r = requests.get(PROFILE_URL, headers=H)
        data = r.json()
        assert data.get("name") == "PersistCheck", (
            f"Name not persisted: got {data.get('name')}"
        )
        assert data.get("phone") == "1234567890", (
            f"Phone not persisted: got {data.get('phone')}"
        )
        # Restore
        requests.put(PROFILE_URL, headers=JH,
                     json={"name": "Test User", "phone": "9876543210"})


class TestAddresses:

    def test_TC_ADDR_01_add_valid_home_address(self):
        """Adding a valid HOME address must return 201 with address object."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME",
            "street": "123 Main Street",
            "city": "Hyderabad",
            "pincode": "500001",
            "is_default": False
        })
        assert r.status_code in (200, 201), (
            f"Expected 201 for valid address, got {r.status_code}: {r.text}"
        )
        data = r.json()
        addr = data.get("address", data)
        assert "address_id" in addr, "Response must include address_id"
        assert addr.get("label") == "HOME"

    def test_TC_ADDR_02_invalid_label_rejected(self):
        """Label must be HOME, OFFICE, or OTHER. 'HOTEL' must return 400."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOTEL",
            "street": "123 Main Street",
            "city": "Hyderabad",
            "pincode": "500001",
            "is_default": False
        })
        assert r.status_code == 400, (
            f"Expected 400 for invalid label HOTEL, got {r.status_code}"
        )

    def test_TC_ADDR_03_short_street_rejected(self):
        """Street with less than 5 characters must return 400."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME",
            "street": "123",
            "city": "Hyderabad",
            "pincode": "500001",
            "is_default": False
        })
        assert r.status_code == 400, (
            f"Expected 400 for street < 5 chars, got {r.status_code}"
        )

    def test_TC_ADDR_04_invalid_pincode_rejected(self):
        """Pincode must be exactly 6 digits. 5-digit and 7-digit must fail."""
        for bad_pin in ("50000", "5000011"):
            r = requests.post(ADDR_URL, headers=JH, json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Hyderabad",
                "pincode": bad_pin,
                "is_default": False
            })
            assert r.status_code == 400, (
                f"Expected 400 for pincode '{bad_pin}', got {r.status_code}"
            )

    def test_TC_ADDR_05_only_one_default_address(self):
        """
        Doc: 'When a new address is added as the default, all other
        addresses must stop being the default first.'
        Add two default addresses — only the last one should be default.
        """
        requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "First Default Street",
            "city": "Mumbai", "pincode": "400001", "is_default": True
        })
        requests.post(ADDR_URL, headers=JH, json={
            "label": "OFFICE", "street": "Second Default Street",
            "city": "Mumbai", "pincode": "400002", "is_default": True
        })
        r = requests.get(ADDR_URL, headers=H)
        addresses = r.json()
        if isinstance(addresses, list):
            defaults = [a for a in addresses if a.get("is_default") is True]
            assert len(defaults) <= 1, (
                f"BUG: Multiple default addresses! Found {len(defaults)} defaults."
            )

    def test_TC_ADDR_06_update_shows_new_data(self):
        """
        After updating an address, the response must show updated data.
        Doc: 'When an address is updated, the response must show the
        new updated data, not the old data.'
        """
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "OTHER", "street": "Old Street Name Here",
            "city": "Delhi", "pincode": "110001", "is_default": False
        })
        if r.status_code not in (200, 201):
            pytest.skip("Could not create address for update test")
        addr_id = r.json().get("address", r.json()).get("address_id")
        if not addr_id:
            pytest.skip("No address_id returned")

        upd = requests.put(ADDR_ID_URL(addr_id), headers=JH,
                           json={"street": "New Updated Street Name"})
        assert upd.status_code == 200
        updated = upd.json().get("address", upd.json())
        assert updated.get("street") == "New Updated Street Name", (
            f"BUG: Update response shows old street. Got: {updated.get('street')}"
        )

    def test_TC_ADDR_07_delete_nonexistent_address_returns_404(self):
        """Deleting an address that does not exist must return 404."""
        r = requests.delete(ADDR_ID_URL(999999), headers=H)
        assert r.status_code == 404, (
            f"Expected 404 for deleting non-existent address, got {r.status_code}"
        )

    def test_TC_ADDR_08_street_exact_min_boundary(self):
        """Street with exactly 5 chars (min) must be accepted."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "12345", "city": "Hyd",
            "pincode": "500001", "is_default": False
        })
        assert r.status_code in (200, 201), f"Expected 200/201 for street=5 chars, got {r.status_code}"

    def test_TC_ADDR_09_street_exact_max_boundary(self):
        """Street with exactly 100 chars (max) must be accepted."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "A" * 100, "city": "Hyd",
            "pincode": "500001", "is_default": False
        })
        assert r.status_code in (200, 201), f"Expected 200/201 for street=100 chars, got {r.status_code}"

    def test_TC_ADDR_10_street_below_min_rejected(self):
        """Street with 4 chars (below min=5) must return 400."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "1234", "city": "Hyd",
            "pincode": "500001", "is_default": False
        })
        assert r.status_code == 400, f"Expected 400 for street=4 chars, got {r.status_code}"

    def test_TC_ADDR_11_street_above_max_rejected(self):
        """Street with 101 chars (above max=100) must return 400."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "A" * 101, "city": "Hyd",
            "pincode": "500001", "is_default": False
        })
        assert r.status_code == 400, f"Expected 400 for street=101 chars, got {r.status_code}"

    def test_TC_ADDR_12_city_exact_min_boundary(self):
        """City with exactly 2 chars (min) must be accepted."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "Main Street", "city": "AB",
            "pincode": "500001", "is_default": False
        })
        assert r.status_code in (200, 201), f"Expected 200/201 for city=2 chars, got {r.status_code}"

    def test_TC_ADDR_13_city_exact_max_boundary(self):
        """City with exactly 50 chars (max) must be accepted."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "Main Street", "city": "A" * 50,
            "pincode": "500001", "is_default": False
        })
        assert r.status_code in (200, 201), f"Expected 200/201 for city=50 chars, got {r.status_code}"

    def test_TC_ADDR_14_city_below_min_rejected(self):
        """City with 1 char (below min=2) must return 400."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "Main Street", "city": "A",
            "pincode": "500001", "is_default": False
        })
        assert r.status_code == 400, f"Expected 400 for city=1 char, got {r.status_code}"

    def test_TC_ADDR_15_city_above_max_rejected(self):
        """City with 51 chars (above max=50) must return 400."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "Main Street", "city": "A" * 51,
            "pincode": "500001", "is_default": False
        })
        assert r.status_code == 400, f"Expected 400 for city=51 chars, got {r.status_code}"

    def test_TC_ADDR_16_pincode_with_letters_rejected(self):
        """Pincode with letters must return 400 — doc says 'exactly 6 digits'."""
        r = requests.post(ADDR_URL, headers=JH, json={
            "label": "HOME", "street": "Main Street", "city": "Hyd",
            "pincode": "50abc1", "is_default": False
        })
        assert r.status_code == 400, (
            f"Expected 400 for pincode with letters, got {r.status_code}"
        )

