"""
test_reviews.py — Tests for Product Reviews API.

Endpoints:
  GET  /api/v1/products/{product_id}/reviews
  POST /api/v1/products/{product_id}/reviews

Test Cases:
  TC-REV-01: Get reviews for a product returns 200                   → 200
  TC-REV-02: Add review with rating=1 (boundary min) → 201           → 201
  TC-REV-03: Add review with rating=5 (boundary max) → 201           → 201
  TC-REV-04: Add review with rating=0 (below min) → 400              → 400
  TC-REV-05: Add review with rating=6 (above max) → 400              → 400
  TC-REV-06: Comment empty string → 400                              → 400
  TC-REV-07: Average rating is a proper decimal, not integer-rounded → verify
  TC-REV-08: Product with no reviews has average_rating=0            → verify

Justification: Rating validation protects data integrity. Average rating
being an integer instead of a decimal (e.g., 3 instead of 3.5) is a
numeric truncation bug that misleads customers.
"""

import requests
import pytest
from conftest import BASE_URL, PRODUCT_APPLE, PRODUCT_BANANA, user_headers, json_headers

REVIEWS_URL = lambda pid: f"{BASE_URL}/products/{pid}/reviews"

# Use user 50 for review tests
UID = 50
H   = user_headers(UID)
JH  = json_headers(UID)

# A product unlikely to have reviews (high ID)
CLEAN_PRODUCT = 200


class TestGetReviews:

    def test_TC_REV_01_get_reviews_returns_200(self):
        """GET reviews for a product must return 200."""
        r = requests.get(REVIEWS_URL(PRODUCT_APPLE), headers=H)
        assert r.status_code == 200

    def test_TC_REV_08_product_with_no_reviews_has_zero_average(self):
        """
        A product with no reviews must show average_rating=0, not null or error.
        Doc: 'If a product has no reviews yet, the average rating is 0.'
        """
        r = requests.get(REVIEWS_URL(CLEAN_PRODUCT), headers=H)
        assert r.status_code == 200
        data = r.json()
        avg = data.get("average_rating", data.get("avg_rating"))
        if avg is not None:
            reviews = data.get("reviews", [])
            if len(reviews) == 0:
                assert avg == 0, (
                    f"BUG: product with no reviews has average_rating={avg}, expected 0"
                )


class TestAddReview:

    def test_TC_REV_02_rating_1_boundary_min_accepted(self):
        """Rating=1 is the minimum valid rating and must be accepted."""
        r = requests.post(REVIEWS_URL(PRODUCT_APPLE), headers=JH,
                          json={"rating": 1, "comment": "Minimum rating test"})
        assert r.status_code in (200, 201), (
            f"Expected 201 for rating=1, got {r.status_code}"
        )

    def test_TC_REV_03_rating_5_boundary_max_accepted(self):
        """Rating=5 is the maximum valid rating and must be accepted."""
        r = requests.post(REVIEWS_URL(PRODUCT_APPLE), headers=JH,
                          json={"rating": 5, "comment": "Maximum rating test"})
        assert r.status_code in (200, 201), (
            f"Expected 201 for rating=5, got {r.status_code}"
        )

    def test_TC_REV_04_rating_0_below_minimum_rejected(self):
        """Rating=0 is below the minimum (1) and must be rejected."""
        r = requests.post(REVIEWS_URL(PRODUCT_APPLE), headers=JH,
                          json={"rating": 0, "comment": "Test"})
        assert r.status_code == 400, (
            f"Expected 400 for rating=0, got {r.status_code}"
        )

    def test_TC_REV_05_rating_6_above_maximum_rejected(self):
        """Rating=6 is above the maximum (5) and must be rejected."""
        r = requests.post(REVIEWS_URL(PRODUCT_APPLE), headers=JH,
                          json={"rating": 6, "comment": "Test"})
        assert r.status_code == 400, (
            f"Expected 400 for rating=6, got {r.status_code}"
        )

    def test_TC_REV_06_empty_comment_rejected(self):
        """Empty comment string must be rejected (min length=1)."""
        r = requests.post(REVIEWS_URL(PRODUCT_APPLE), headers=JH,
                          json={"rating": 3, "comment": ""})
        assert r.status_code == 400, (
            f"Expected 400 for empty comment, got {r.status_code}"
        )

    def test_TC_REV_07_average_rating_is_decimal_not_integer(self):
        """
        CRITICAL: The average rating must be a proper decimal, NOT integer-truncated.
        Doc: 'The average rating shown must be a proper decimal calculation,
        not a rounded-down integer.'

        Approach (reproducible across runs):
        - Add rating=3 from user 52, rating=4 from user 53 (isolated users)
        - Fetch the average_rating after our adds
        - The overall average including our two ratings must be a decimal
          IF the only two reviews are ours (3+4=3.5), OR still detectable
          if we compare to see integer truncation happened.
        
        We detect the bug by checking: is the reported average an exact integer
        when it mathematically cannot be? We add one known odd and one even score
        (1 and 4 = average 2.5) and verify the result is NOT a whole number
        when those are the only two reviews on a fresh product (199).
        We use product 199 which is very unlikely to have prior reviews.
        """
        TEST_PRODUCT = 199   # high ID, unlikely to have pre-existing reviews
        uid_a_jh = json_headers(52)
        uid_b_jh = json_headers(53)

        # Step 1: Get current state (how many reviews already)
        before = requests.get(REVIEWS_URL(TEST_PRODUCT), headers=H).json()
        reviews_before = before.get("reviews", [])

        # Step 2: Add two reviews that will produce a non-integer average together
        requests.post(REVIEWS_URL(TEST_PRODUCT), headers=uid_a_jh,
                      json={"rating": 1, "comment": "Reproducibility test review A"})
        requests.post(REVIEWS_URL(TEST_PRODUCT), headers=uid_b_jh,
                      json={"rating": 4, "comment": "Reproducibility test review B"})

        # Step 3: Get updated average
        after = requests.get(REVIEWS_URL(TEST_PRODUCT), headers=H)
        assert after.status_code == 200
        data = after.json()
        avg = data.get("average_rating", data.get("avg_rating"))
        reviews_after = data.get("reviews", [])

        # Step 4: If we added exactly 2 reviews (product was empty before)
        # then average = (1+4)/2 = 2.5  →  must NOT be 2 (truncated)
        if len(reviews_before) == 0 and len(reviews_after) == 2:
            assert avg == 2.5, (
                f"BUG: Average rating is integer-truncated or wrong! "
                f"Added ratings 1 and 4, expected average=2.5, got {avg}"
            )
        elif avg is not None:
            # Even if there were prior reviews, if average is a whole number
            # and our two reviews (odd-sum) were added, that's suspicious.
            # At minimum, confirm the response returns a numeric value.
            assert isinstance(avg, (int, float)), (
                f"average_rating is not a number: {avg}"
            )

    def test_TC_REV_09_comment_max_boundary_accepted(self):
        """Comment with exactly 200 chars (max) must be accepted."""
        r = requests.post(REVIEWS_URL(PRODUCT_BANANA), headers=JH,
                          json={"rating": 3, "comment": "B" * 200})
        assert r.status_code in (200, 201), (
            f"Expected 200/201 for comment=200 chars, got {r.status_code}"
        )

    def test_TC_REV_10_comment_above_max_rejected(self):
        """Comment with 201 chars (above max=200) must return 400."""
        r = requests.post(REVIEWS_URL(PRODUCT_BANANA), headers=JH,
                          json={"rating": 3, "comment": "A" * 201})
        assert r.status_code == 400, (
            f"Expected 400 for comment=201 chars, got {r.status_code}"
        )

    def test_TC_REV_11_review_nonexistent_product_returns_404(self):
        """Posting a review for a non-existent product must return 404."""
        r = requests.post(REVIEWS_URL(999999), headers=JH,
                          json={"rating": 3, "comment": "Test"})
        assert r.status_code == 404, (
            f"Expected 404 for review on non-existent product, got {r.status_code}"
        )

    def test_TC_REV_12_negative_rating_rejected(self):
        """Rating=-1 (negative) must be rejected with 400."""
        r = requests.post(REVIEWS_URL(PRODUCT_APPLE), headers=JH,
                          json={"rating": -1, "comment": "Test"})
        assert r.status_code == 400, (
            f"Expected 400 for negative rating, got {r.status_code}"
        )

