"""
test_wallet.py — Tests for Wallet API.

Endpoints:
  GET  /api/v1/wallet
  POST /api/v1/wallet/add    Body: {"amount": <number>}
  POST /api/v1/wallet/pay    Body: {"amount": <number>}

Test Cases:
  TC-WAL-01: Get wallet returns 200 with balance field               → 200
  TC-WAL-02: Add positive amount within limit → balance increases    → 200
  TC-WAL-03: Add amount=0 must be rejected                          → 400
  TC-WAL-04: Add negative amount must be rejected                   → 400
  TC-WAL-05: Add amount=100000 (boundary max) must succeed          → 200
  TC-WAL-06: Add amount=100001 (over max) must be rejected          → 400
  TC-WAL-07: Pay with wallet, exact amount is deducted              → verify
  TC-WAL-08: Pay more than wallet balance → 400                     → 400

Justification: Wallet is a financial feature — incorrect deductions or
accepting invalid amounts directly affects user money.
"""

import requests
import pytest
from conftest import BASE_URL, user_headers, json_headers

WALLET_URL  = f"{BASE_URL}/wallet"
ADD_URL     = f"{BASE_URL}/wallet/add"
PAY_URL     = f"{BASE_URL}/wallet/pay"

# Use user 30 for wallet tests (isolated)
UID = 30
H   = user_headers(UID)
JH  = json_headers(UID)


class TestWalletView:

    def test_TC_WAL_01_get_wallet_returns_balance(self):
        """GET /wallet must return 200 with a numeric balance field."""
        r = requests.get(WALLET_URL, headers=H)
        assert r.status_code == 200
        data = r.json()
        assert "balance" in data or "wallet_balance" in data, (
            "Response missing 'balance' field"
        )


class TestWalletAdd:

    def test_TC_WAL_02_add_valid_amount_increases_balance(self):
        """Adding $100 must increase balance by exactly $100."""
        before = requests.get(WALLET_URL, headers=H).json()
        bal_before = before.get("balance", before.get("wallet_balance", 0))

        r = requests.post(ADD_URL, headers=JH, json={"amount": 100})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

        after = requests.get(WALLET_URL, headers=H).json()
        bal_after = after.get("balance", after.get("wallet_balance", 0))
        assert abs((bal_after - bal_before) - 100) < 0.01, (
            f"BUG: Balance should increase by 100. Before={bal_before}, After={bal_after}"
        )

    def test_TC_WAL_03_add_zero_rejected(self):
        """Adding amount=0 must be rejected with 400."""
        r = requests.post(ADD_URL, headers=JH, json={"amount": 0})
        assert r.status_code == 400, (
            f"Expected 400 for amount=0, got {r.status_code}"
        )

    def test_TC_WAL_04_add_negative_rejected(self):
        """Adding a negative amount must be rejected with 400."""
        r = requests.post(ADD_URL, headers=JH, json={"amount": -50})
        assert r.status_code == 400, (
            f"Expected 400 for negative amount, got {r.status_code}"
        )

    def test_TC_WAL_05_add_exactly_100000_succeeds(self):
        """Boundary: amount=100000 (the maximum) must succeed."""
        r = requests.post(ADD_URL, headers=JH, json={"amount": 100000})
        assert r.status_code == 200, (
            f"Expected 200 for boundary max 100000, got {r.status_code}"
        )

    def test_TC_WAL_06_add_100001_rejected(self):
        """Boundary+1: amount=100001 (one above max) must be rejected."""
        r = requests.post(ADD_URL, headers=JH, json={"amount": 100001})
        assert r.status_code == 400, (
            f"Expected 400 for amount=100001 (over max), got {r.status_code}"
        )


class TestWalletPay:

    def test_TC_WAL_07_pay_deducts_exact_amount(self):
        """Paying from wallet must deduct exactly the requested amount — no more."""
        requests.post(ADD_URL, headers=JH, json={"amount": 500})
        before = requests.get(WALLET_URL, headers=H).json()
        bal_before = before.get("balance", before.get("wallet_balance", 0))

        r = requests.post(PAY_URL, headers=JH, json={"amount": 100})
        assert r.status_code == 200, f"Payment failed: {r.status_code}"

        after = requests.get(WALLET_URL, headers=H).json()
        bal_after = after.get("balance", after.get("wallet_balance", 0))
        assert abs((bal_before - bal_after) - 100) < 0.01, (
            f"BUG: Expected deduction of 100. Before={bal_before}, After={bal_after}"
        )

    def test_TC_WAL_08_pay_more_than_balance_rejected(self):
        """Paying more than the wallet balance must return 400."""
        r = requests.post(PAY_URL, headers=JH, json={"amount": 9999999})
        assert r.status_code == 400, (
            f"Expected 400 for payment exceeding balance, got {r.status_code}"
        )
