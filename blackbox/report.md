# Question 3: Black-Box API Testing — QuickCart REST API

## Setup

```bash
# Load and start the server
docker load -i quickcart_image_x86.tar
docker run -d -p 8080:8080 --name quickcart quickcart

# Install dependencies and run all tests
pip install requests pytest
cd blackbox/
pytest tests/ -v
```

**Base URL:** `http://localhost:8080/api/v1`  
**Roll Number:** `2024101112`  
**Required Headers on every request:** `X-Roll-Number: 2024101112`  
**Additional header on user endpoints:** `X-User-ID: <user_id>`

---

## 3.1 Test Case Design

Test cases are organised by API module. Each entry lists:
- **Input** — HTTP method, URL, headers, and request body
- **Expected Output** — status code and key response fields as per API docs
- **Justification** — why this case is necessary

---

### Module 1: Authentication Headers

---

#### TC-AUTH-01 — Missing X-Roll-Number on admin endpoint
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users` (no headers) |
| **Expected** | `401 Unauthorized` |
| **Actual** | `401` (Passed) |
| **Justification** | The API doc states every request must include X-Roll-Number. Missing it must gate access at 401. |

---

#### TC-AUTH-02 — Non-integer X-Roll-Number (letters)
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users` with `X-Roll-Number: abc` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Roll number must be a valid integer. Alphabetic values are type errors and must be rejected. |

---

#### TC-AUTH-03 — Symbol X-Roll-Number
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users` with `X-Roll-Number: !@#` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Symbols are also invalid integers. Tests that the parser rejects any non-numeric input. |

---

#### TC-AUTH-04 — Valid X-Roll-Number
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users` with `X-Roll-Number: 2024101112` |
| **Expected** | `200 OK` |
| **Actual** | `200` (Passed) |
| **Justification** | Positive control — valid header must be accepted. |

---

#### TC-AUTH-05 — Missing X-User-ID on user endpoint
| | |
|---|---|
| **Input** | `GET /api/v1/profile` with only `X-Roll-Number` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | User-scoped endpoints require both headers. Missing X-User-ID must be rejected. |

---

#### TC-AUTH-06 — Non-integer X-User-ID
| | |
|---|---|
| **Input** | `GET /api/v1/profile` with `X-User-ID: abc` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | X-User-ID must be a positive integer. Type mismatch must be caught. |

---

#### TC-AUTH-07 — Non-existent X-User-ID
| | |
|---|---|
| **Input** | `GET /api/v1/profile` with `X-User-ID: 999999` |
| **Expected** | `400 Bad Request` (doc says invalid → 400) |
| **Actual** | `404 Not Found` (Bug Found) |
| **Justification** | Tests that the system validates user existence. The API doc says "If missing or invalid, the server returns a 400 error". The server returns 404 instead — documented as Bug #20. |

---

#### TC-AUTH-08 — Valid headers on user endpoint
| | |
|---|---|
| **Input** | `GET /api/v1/profile` with both headers valid |
| **Expected** | `200 OK` |
| **Actual** | `200` (Passed) |
| **Justification** | Positive control for user-scoped endpoint access. |

---

### Module 2: Products

---

#### TC-PROD-01 — List products returns array
| | |
|---|---|
| **Input** | `GET /api/v1/products` |
| **Expected** | `200 OK`, JSON array of active products |
| **Actual** | `200` (Passed) |
| **Justification** | Foundation test — product list must work and return an array. |

---

#### TC-PROD-02 — Inactive product not in public list
| | |
|---|---|
| **Input** | `GET /api/v1/products`, check if product_id=214 (inactive) appears |
| **Expected** | Product 214 absent from list |
| **Actual** | Absent (Passed) |
| **Justification** | Doc: "The product list only returns products that are active." Showing inactive items would allow users to order unavailable products. |

---

#### TC-PROD-05 — Price matches admin/products exactly
| | |
|---|---|
| **Input** | `GET /api/v1/products` vs `GET /api/v1/admin/products` for same product IDs |
| **Expected** | Prices identical |
| **Actual** | Product 8 shows price=100 in public list but price=95 in admin view (Bug Found) |
| **Justification** | Doc: "The price shown for every product must be the exact real price stored in the database." A wrong price causes customers to be charged incorrectly at checkout. |

---

#### TC-PROD-06 — Filter by category
| | |
|---|---|
| **Input** | `GET /api/v1/products?category=Fruits` |
| **Expected** | `200 OK`, all returned products have category="Fruits" |
| **Actual** | `200` (Passed) |
| **Justification** | Category filter must not leak products from other categories. |

---

#### TC-PROD-08/09 — Sort ascending and descending
| | |
|---|---|
| **Input** | `GET /api/v1/products?sort=price_asc` and `sort=price_desc` |
| **Expected** | Prices in correct order |
| **Actual** | Both `200` (Passed) |
| **Justification** | Sort correctness ensures customers can find cheapest/most expensive items accurately. |

---

#### TC-PROD-04 — Non-existent product returns 404
| | |
|---|---|
| **Input** | `GET /api/v1/products/999999` |
| **Expected** | `404 Not Found` |
| **Actual** | `404` (Passed) |
| **Justification** | Looking up a missing product must not crash or return empty data silently. |

---

### Module 3: Cart

---

#### TC-CART-02 — Add valid product
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 1, "quantity": 2}` |
| **Expected** | `200/201` |
| **Actual** | `200` (Passed) |
| **Justification** | Basic add-to-cart functionality must work. |

---

#### TC-CART-03 — Add quantity=0 must be rejected
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 1, "quantity": 0}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `200 OK` (Bug Found) |
| **Justification** | Doc: "When adding an item, the quantity must be at least 1. Sending 0 or a negative number must be rejected with a 400 error." The server silently accepts 0-quantity additions. |

---

#### TC-CART-04 — Add negative quantity must be rejected
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 1, "quantity": -1}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Negative quantity is nonsensical and must be rejected. |

---

#### TC-CART-05 — Add non-existent product returns 404
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 999999, "quantity": 1}` |
| **Expected** | `404 Not Found` |
| **Actual** | `404` (Passed) |
| **Justification** | Doc: "If the product being added does not exist, the server returns a 404 error." |

---

#### TC-CART-06 — Same product added twice accumulates
| | |
|---|---|
| **Input** | Add product 3 qty=2, then add product 3 qty=3 |
| **Expected** | Cart shows product 3 with qty=5 |
| **Actual** | `qty=5` (Passed) |
| **Justification** | Doc: "If the same product is added more than once, the quantities are added together." |

---

#### TC-CART-07 — Item subtotal = quantity × unit price
| | |
|---|---|
| **Input** | Add product 1 (price=120) qty=3. Check subtotal field. |
| **Expected** | `subtotal = 360` |
| **Actual** | `subtotal = 104` (Bug Found) |
| **Justification** | Doc: "Each item in the cart must show the correct subtotal, which is the quantity times the unit price." The subtotal field is completely wrong — not even close to qty×price. |

---

#### TC-CART-08 — Cart total = sum of all item subtotals
| | |
|---|---|
| **Input** | Add Apple qty=2 + Banana qty=3, check cart total |
| **Expected** | `total = (2×120) + (3×40) = 360` |
| **Actual** | `total = -16` (Bug Found) |
| **Justification** | Doc: "The cart total must be the sum of all item subtotals. Every item must be counted, including the last one." The cart total is wildly wrong — negative value. |

---

#### TC-CART-09 — Remove non-existent item returns 404
| | |
|---|---|
| **Input** | `POST /api/v1/cart/remove` `{"product_id": 999999}` |
| **Expected** | `404 Not Found` |
| **Actual** | `404` (Passed) |
| **Justification** | Doc: "When removing an item, if the product is not in the cart, the server returns a 404 error." |

---

#### TC-CART-11 — Add more than stock quantity returns 400
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 5, "quantity": 999}` (stock=56) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "If the quantity asked for is more than what is in stock, the server returns a 400 error." |

---

### Module 4: Coupons

---

#### TC-CPN-01 — Valid FIXED coupon applied correctly
| | |
|---|---|
| **Input** | Cart ≥ $750, apply `BONUS75` (FIXED $75 off) |
| **Expected** | `200 OK`, discount=75 |
| **Actual** | `200`, discount=75 (Passed) |
| **Justification** | Positive test for FIXED coupon — discount must be exactly the declared value. |

---

#### TC-CPN-02 — PERCENT coupon calculates correct percentage
| | |
|---|---|
| **Input** | Cart = $360 (3 apples), apply `FIRSTORDER` (15% off, min $200) |
| **Expected** | `200 OK`, discount = 360 × 0.15 = 54.0 |
| **Actual** | discount = 15 (Bug Found) |
| **Justification** | Doc: "A PERCENT coupon takes a percentage off the total." The server returned the percentage value (15) instead of calculating 15% of the cart total — the discount formula is broken. |

---

#### TC-CPN-03 — Expired coupon rejected
| | |
|---|---|
| **Input** | Apply `EXPIRED100` (expired Feb 28 2026) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Expired coupons must not be honoured. |

---

#### TC-CPN-04 — Cart below minimum rejected
| | |
|---|---|
| **Input** | Cart = $120 (1 apple), apply `BONUS75` (min cart = $750) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Minimum cart value is a coupon eligibility requirement. |

---

#### TC-CPN-05 — Percent coupon capped at max_discount
| | |
|---|---|
| **Input** | Cart = $1200 (10 apples), apply `LOYALTY20` (20% off, cap=$180) |
| **Expected** | discount = 180 (20% of 1200 = 240, capped at 180) |
| **Actual** | discount = 20 (Bug Found) |
| **Justification** | Doc: "If the coupon has a maximum discount cap, the discount must not go above that cap." The server again returned the raw percentage value (20) instead of applying it. This confirms the PERCENT coupon calculation is fundamentally broken. |

---

### Module 5: Checkout

---

#### TC-CHK-01 — CARD payment sets status PAID
| | |
|---|---|
| **Input** | `POST /api/v1/checkout` `{"payment_method": "CARD"}` |
| **Expected** | `200 OK`, `payment_status = "PAID"` |
| **Actual** | `200`, `payment_status = "PAID"` (Passed) |
| **Justification** | Doc: "When paying with CARD, it starts as PAID." |

---

#### TC-CHK-02 — COD payment sets status PENDING
| | |
|---|---|
| **Input** | `POST /api/v1/checkout` `{"payment_method": "COD"}` |
| **Expected** | `200 OK`, `payment_status = "PENDING"` |
| **Actual** | `200`, `payment_status = "PENDING"` (Passed) |
| **Justification** | Doc: "When paying with COD or WALLET, the order starts with a payment status of PENDING." |

---

#### TC-CHK-04 — Invalid payment method rejected
| | |
|---|---|
| **Input** | `POST /api/v1/checkout` `{"payment_method": "CASH"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Only COD, WALLET, CARD are valid. All others must be rejected. |

---

#### TC-CHK-05 — Empty cart checkout rejected
| | |
|---|---|
| **Input** | `POST /api/v1/checkout` with empty cart |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "The cart must not be empty. If it is empty, the server returns a 400 error." |

---

#### TC-CHK-06 — COD blocked when order > $5000
| | |
|---|---|
| **Input** | Cart with Mango qty=21 (total > 5000), checkout with COD |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "COD is not allowed if the order total is more than 5000." |

---

#### TC-CHK-07 — GST is exactly 5%
| | |
|---|---|
| **Input** | 2 × Apple ($240), checkout. Invoice: subtotal=240, GST=12, total=252 |
| **Expected** | `total = subtotal × 1.05` |
| **Actual** | GST calculation correct (Passed) |
| **Justification** | Doc: "GST is 5 percent and is added only once." |

---

### Module 6: Wallet

---

#### TC-WAL-02 — Add valid amount
| | |
|---|---|
| **Input** | `POST /api/v1/wallet/add` `{"amount": 100}` |
| **Expected** | `200 OK`, balance increases by 100 |
| **Actual** | `200` (Passed) |
| **Justification** | Basic wallet add must work. |

---

#### TC-WAL-03/04 — Zero and negative amount rejected
| | |
|---|---|
| **Input** | amount=0 and amount=-50 |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "the amount must be more than 0." |

---

#### TC-WAL-05 — Boundary max 100000 accepted
| | |
|---|---|
| **Input** | `POST /api/v1/wallet/add` `{"amount": 100000}` |
| **Expected** | `200 OK` |
| **Actual** | `200` (Passed) |
| **Justification** | Doc: "at most 100000." Boundary value must succeed. |

---

#### TC-WAL-06 — Over-limit 100001 rejected
| | |
|---|---|
| **Input** | `POST /api/v1/wallet/add` `{"amount": 100001}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | One above boundary must be rejected. |

---

#### TC-WAL-07 — Payment deducts exact amount
| | |
|---|---|
| **Input** | Add $500 to wallet, pay $100. Check balance decreases by exactly 100. |
| **Expected** | balance decreases by exactly 100 |
| **Actual** | Balance decreased by 100.40 (Bug Found) |
| **Justification** | Doc: "the exact amount requested is deducted from the balance. No extra amount is taken." The server deducted 0.40 more than requested — floating-point rounding error in payment deduction. |

---

#### TC-WAL-08 — Pay more than balance rejected
| | |
|---|---|
| **Input** | `POST /api/v1/wallet/pay` `{"amount": 9999999}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Prevents users from going into negative wallet balance. |

---

### Module 7: Orders

---

#### TC-ORD-01 — Get orders list
| | |
|---|---|
| **Input** | `GET /api/v1/orders` |
| **Expected** | `200 OK`, JSON array |
| **Actual** | `200` (Passed) |
| **Justification** | Basic read of order history must work. |

---

#### TC-ORD-03/04 — Non-existent order returns 404
| | |
|---|---|
| **Input** | `GET /api/v1/orders/999999` and `POST /api/v1/orders/999999/cancel` |
| **Expected** | `404 Not Found` |
| **Actual** | `404` (Passed) |
| **Justification** | Missing resource must return 404. |

---

#### TC-ORD-06 — Stock restored on cancel
| | |
|---|---|
| **Input** | Place order for 2 × Apple. Cancel. Check stock in admin/products. |
| **Expected** | Apple stock returns to pre-order value |
| **Actual** | Stock decreased by 2 and stayed at -2 after cancel (Bug Found) |
| **Justification** | Doc: "When an order is cancelled, all the items in that order are added back to the product stock." Stock was NOT restored — items permanently disappear from inventory. |

---

#### TC-ORD-07/08 — Invoice totals correct
| | |
|---|---|
| **Input** | Get invoice after checkout. Compare to order total. |
| **Expected** | `invoice.total == order.total`, `gst = subtotal × 0.05` |
| **Actual** | Totals match (Passed) |
| **Justification** | Doc: "The total shown must match the actual order total exactly." |

---

### Module 8: Reviews

---

#### TC-REV-02/03 — Boundary ratings 1 and 5 accepted
| | |
|---|---|
| **Input** | `POST /api/v1/products/1/reviews` with rating=1, then rating=5 |
| **Expected** | `201 Created` |
| **Actual** | `201` (Passed) |
| **Justification** | Exact boundary values must be valid. |

---

#### TC-REV-04/05 — Out-of-range ratings rejected
| | |
|---|---|
| **Input** | rating=0 and rating=6 |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "A review rating must be between 1 and 5. Anything outside that range must be rejected." |

---

#### TC-REV-06 — Empty comment rejected
| | |
|---|---|
| **Input** | `{"rating": 3, "comment": ""}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "A comment must be between 1 and 200 characters." Empty string violates minimum. |

---

#### TC-REV-07 — Average rating is decimal, not integer-truncated
| | |
|---|---|
| **Input** | Add reviews: rating=3 and rating=4. Get product reviews. |
| **Expected** | `average_rating = 3.5` |
| **Actual** | `average_rating = 4` (Bug Found) |
| **Justification** | Doc: "The average rating shown must be a proper decimal calculation, not a rounded-down integer." The server uses integer division — (3+4)//2 = 3 or rounds incorrectly. This misleads customers about product quality. |

---

#### TC-REV-09/10 — Comment boundary values
| | |
|---|---|
| **Input** | comment=200 chars (max boundary) and comment=201 chars (above max) |
| **Expected** | `200/201` for 200 chars, `400` for 201 chars |
| **Actual** | Both correct (Passed) |
| **Justification** | Doc: "A comment must be between 1 and 200 characters." |

---

#### TC-REV-11 — Review on non-existent product accepted (should be 404)
| | |
|---|---|
| **Input** | `POST /api/v1/products/999999/reviews` `{"rating": 3, "comment": "Test"}` |
| **Expected** | `404 Not Found` |
| **Actual** | `200 OK` (Bug Found) |
| **Justification** | A review on a non-existent product must not succeed. The server creates orphan reviews. |

---

#### TC-REV-12 — Negative rating rejected
| | |
|---|---|
| **Input** | `{"rating": -1, "comment": "Test"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Negative rating is outside the 1–5 range. |

---

### Module 9: Support Tickets

---

#### TC-TKT-01 — Create valid ticket
| | |
|---|---|
| **Input** | `POST /api/v1/support/ticket` `{"subject": "Order issue", "message": "My order is late."}` |
| **Expected** | `201 Created` |
| **Actual** | `201` (Passed) |
| **Justification** | Basic ticket creation must work. |

---

#### TC-TKT-02 — Short subject rejected
| | |
|---|---|
| **Input** | `{"subject": "Hi", "message": "..."}` (2 chars, min=5) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "the subject must be between 5 and 100 characters." |

---

#### TC-TKT-05 — New ticket is OPEN
| | |
|---|---|
| **Input** | Create ticket, check status field |
| **Expected** | `status = "OPEN"` |
| **Actual** | `status = "OPEN"` (Passed) |
| **Justification** | Doc: "A new ticket always starts with status OPEN." |

---

#### TC-TKT-06/07 — Valid transitions
| | |
|---|---|
| **Input** | OPEN → IN_PROGRESS, then IN_PROGRESS → CLOSED |
| **Expected** | Both `200 OK` |
| **Actual** | `200` (Passed) |
| **Justification** | Forward transitions in the defined direction must be accepted. |

---

#### TC-TKT-08 — Skip OPEN → CLOSED rejected
| | |
|---|---|
| **Input** | From OPEN status, `PUT {"status": "CLOSED"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `200 OK` (Bug Found) |
| **Justification** | Doc: "No other changes are allowed." Skipping IN_PROGRESS violates the state machine. The server allows it, which can break support workflows. |

---

#### TC-TKT-09 — Reverse CLOSED → OPEN rejected
| | |
|---|---|
| **Input** | From CLOSED status, `PUT {"status": "OPEN"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `200 OK` (Bug Found) |
| **Justification** | Once closed, a ticket must not be reopened. The server allows arbitrary status changes. |

---

### Module 10: Profile and Addresses

---

#### TC-PRF-01 — Get profile returns 200
| | |
|---|---|
| **Input** | `GET /api/v1/profile` |
| **Expected** | `200 OK` with user fields |
| **Actual** | `200` (Passed) |
| **Justification** | Basic profile read. |

---

#### TC-PRF-02/03 — Name length boundaries
| | |
|---|---|
| **Input** | name with 1 char (below min), name with 51 chars (above max=50) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "the name must be between 2 and 50 characters." |

---

#### TC-PRF-04/05 — Phone length boundaries
| | |
|---|---|
| **Input** | phone="987654321" (9 digits) and phone="98765432101" (11 digits) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "The phone number must be exactly 10 digits." |

---

#### TC-ADDR-01 — Add valid address
| | |
|---|---|
| **Input** | `POST /api/v1/addresses` with valid HOME address |
| **Expected** | `201 Created` with address_id in response |
| **Actual** | `201` (Passed) |
| **Justification** | Address creation must return a proper object with assigned ID. |

---

#### TC-ADDR-02 — Invalid label rejected
| | |
|---|---|
| **Input** | `{"label": "HOTEL", ...}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "the label must be HOME, OFFICE, or OTHER." |

---

#### TC-ADDR-04 — Pincode boundary
| | |
|---|---|
| **Input** | pincode="50000" (5 digits) and pincode="5000011" (7 digits) |
| **Expected** | `400 Bad Request` for both |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "The pincode must be exactly 6 digits." |

---

#### TC-ADDR-05 — Only one default address at a time
| | |
|---|---|
| **Input** | Add two addresses both with `is_default: true` |
| **Expected** | Only 1 address has `is_default: true` |
| **Actual** | 3 addresses have `is_default: true` (Bug Found) |
| **Justification** | Doc: "When a new address is added as the default, all other addresses must stop being the default first. Only one address can be default at a time." Multiple defaults cause billing ambiguity. |

---

#### TC-ADDR-07 — Delete non-existent address returns 404
| | |
|---|---|
| **Input** | `DELETE /api/v1/addresses/999999` |
| **Expected** | `404 Not Found` |
| **Actual** | `404` (Passed) |
| **Justification** | Deleting a missing resource must return 404. |

---

#### TC-ADDR-08/09 — Street boundary values (5 min, 100 max)
| | |
|---|---|
| **Input** | street=5 chars (min), street=100 chars (max), street=4 chars (below), street=101 chars (above) |
| **Expected** | 200/201 for 5 and 100, 400 for 4 and 101 |
| **Actual** | All correct (Passed) |
| **Justification** | Exact boundary testing on street length. |

---

#### TC-ADDR-12/13 — City boundary values (2 min, 50 max)
| | |
|---|---|
| **Input** | city=2 chars (min), city=50 chars (max), city=1 char (below), city=51 chars (above) |
| **Expected** | 200/201 for 2 and 50, 400 for 1 and 51 |
| **Actual** | All correct (Passed) |
| **Justification** | Exact boundary testing on city length. |

---

#### TC-ADDR-16 — Pincode with letters accepted (should be rejected)
| | |
|---|---|
| **Input** | `POST /api/v1/addresses` with `"pincode": "50abc1"` |
| **Expected** | `400 Bad Request` — doc says "exactly 6 digits" |
| **Actual** | `200 OK` (Bug Found) |
| **Justification** | Server only checks length, not that all characters are digits. Same class of bug as phone validation. |

---

### Module 16: Loyalty Points

---

#### TC-LOY-01 — GET loyalty returns 200
| | |
|---|---|
| **Input** | `GET /api/v1/loyalty` |
| **Expected** | `200 OK` with `loyalty_points` field |
| **Actual** | `200` (Passed) |
| **Justification** | Basic loyalty read. |

---

#### TC-LOY-02 — Redeem points=1 (min valid)
| | |
|---|---|
| **Input** | `POST /api/v1/loyalty/redeem` `{"points": 1}` |
| **Expected** | `200 OK` |
| **Actual** | `200` (Passed) |
| **Justification** | Doc: "The amount to redeem must be at least 1." Minimum valid must work. |

---

#### TC-LOY-03/04 — Zero and negative points rejected
| | |
|---|---|
| **Input** | points=0 and points=-5 |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "The amount to redeem must be at least 1." |

---

#### TC-LOY-05 — Redeem more than available rejected
| | |
|---|---|
| **Input** | `{"points": 999999}` (user has ~500 points) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Doc: "the user must have enough points." |

---

#### TC-LOY-06 — Wrong data type rejected
| | |
|---|---|
| **Input** | `{"points": "five"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | String value must not be accepted for a numeric field. |

---

#### TC-PRF-07/08 — Name exact boundary values accepted
| | |
|---|---|
| **Input** | name="AB" (exactly 2 chars, min) and name="A"×50 (exactly 50 chars, max) |
| **Expected** | `200 OK` for both |
| **Actual** | `200` (Passed) |
| **Justification** | Exact boundary values must be accepted. Tests both ends of the valid range. |

---

#### TC-PRF-09 — Empty name rejected
| | |
|---|---|
| **Input** | `PUT /api/v1/profile` `{"name": "", "phone": "9876543210"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Empty string is below the 2-char minimum. |

---

#### TC-PRF-10 — Phone with letters accepted (should be rejected)
| | |
|---|---|
| **Input** | `PUT /api/v1/profile` `{"name": "Test User", "phone": "98765abcde"}` |
| **Expected** | `400 Bad Request` — doc says "exactly 10 digits" |
| **Actual** | `200 OK` (Bug Found) |
| **Justification** | The server only checks length (10 chars) but not that all characters are digits. Letters pass validation when they should not. |

---

#### TC-PRF-11 — Update persists on subsequent GET
| | |
|---|---|
| **Input** | PUT name="PersistCheck", phone="1234567890", then GET /profile |
| **Expected** | GET returns the updated name and phone |
| **Actual** | Both values persisted correctly (Passed) |
| **Justification** | Verifies that PUT actually modifies the stored data, not just returns 200 without saving. |

---

## 3.2 Bug Report

### Bug #1 — Cart Item Subtotal is Wrong

| | |
|---|---|
| **Endpoint** | `GET /api/v1/cart` |
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/cart` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 10` |
| **Body** | *(none)* |
| **Expected** | Item subtotal = quantity × unit_price. For Apple (price=120) qty=3 → subtotal=360 |
| **Actual** | subtotal=104 (completely wrong value, not related to qty×price) |

---

### Bug #2 — Cart Total is Wrong (Negative Value)

| | |
|---|---|
| **Endpoint** | `GET /api/v1/cart` |
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/cart` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 10` |
| **Body** | *(none — cart has Apple qty=2 + Banana qty=3)* |
| **Expected** | `total = 240 + 120 = 360` |
| **Actual** | `total = -16` (negative, mathematically impossible) |

---

### Bug #3 — Cart Accepts qty=0 (Should Reject with 400)

| | |
|---|---|
| **Endpoint** | `POST /api/v1/cart/add` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/cart/add` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 10`, `Content-Type: application/json` |
| **Body** | `{"product_id": 1, "quantity": 0}` |
| **Expected** | `400 Bad Request` — doc says quantity must be at least 1 |
| **Actual** | `200 OK` — server accepted the zero-quantity add |

---

### Bug #4 — Product Price Mismatch (Public vs Admin)

| | |
|---|---|
| **Endpoint** | `GET /api/v1/products` |
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/products` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 1` |
| **Body** | *(none)* |
| **Expected** | Product 8 price = 95 (as stored in database, visible in admin view) |
| **Actual** | Product 8 price = 100 (inflated by $5) |

---

### Bug #5 — PERCENT Coupon Returns Percentage Value Instead of Calculated Discount

| | |
|---|---|
| **Endpoint** | `POST /api/v1/coupon/apply` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/coupon/apply` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 11`, `Content-Type: application/json` |
| **Body** | `{"coupon_code": "FIRSTORDER"}` (cart = $360, 15% off) |
| **Expected** | `discount = 54.0` (15% of 360) |
| **Actual** | `discount = 15` (returned the percentage number, not the calculated amount) |

---

### Bug #6 — PERCENT Coupon Cap Not Enforced

| | |
|---|---|
| **Endpoint** | `POST /api/v1/coupon/apply` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/coupon/apply` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 11`, `Content-Type: application/json` |
| **Body** | `{"coupon_code": "LOYALTY20"}` (cart = $1200, 20% off, max_discount=$180) |
| **Expected** | `discount = 180` (20% of 1200 = 240, capped at 180) |
| **Actual** | `discount = 20` (returned raw percentage value — same root cause as Bug #5) |

---

### Bug #7 — Order Cancel Does Not Restore Product Stock

| | |
|---|---|
| **Endpoint** | `POST /api/v1/orders/{order_id}/cancel` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/orders/42/cancel` (example order) |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 40` |
| **Body** | *(none)* |
| **Expected** | After cancel, Apple stock returns to pre-order value (restored by 2 units) |
| **Actual** | Apple stock stays at the post-order value — 2 units permanently lost from inventory |

---

### Bug #8 — Review Average Rating is Integer-Truncated

| | |
|---|---|
| **Endpoint** | `GET /api/v1/products/{product_id}/reviews` |
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/products/3/reviews` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 50` |
| **Body** | *(none)* |
| **Expected** | `average_rating = 3.5` (two reviews: rating 3 and rating 4) |
| **Actual** | `average_rating = 4` (integer, not decimal — truncation or rounding error) |

---

### Bug #9 — Ticket Status Can Skip (OPEN → CLOSED Allowed)

| | |
|---|---|
| **Endpoint** | `PUT /api/v1/support/tickets/{ticket_id}` |
| **Method** | PUT |
| **URL** | `http://localhost:8080/api/v1/support/tickets/5` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 60`, `Content-Type: application/json` |
| **Body** | `{"status": "CLOSED"}` (ticket is currently OPEN) |
| **Expected** | `400 Bad Request` — OPEN can only go to IN_PROGRESS |
| **Actual** | `200 OK` — skip transition was accepted |

---

### Bug #10 — Ticket Status Can Reverse (CLOSED → OPEN Allowed)

| | |
|---|---|
| **Endpoint** | `PUT /api/v1/support/tickets/{ticket_id}` |
| **Method** | PUT |
| **URL** | `http://localhost:8080/api/v1/support/tickets/6` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 60`, `Content-Type: application/json` |
| **Body** | `{"status": "OPEN"}` (ticket is currently CLOSED) |
| **Expected** | `400 Bad Request` — CLOSED is a terminal state |
| **Actual** | `200 OK` — reverse transition was accepted |

---

### Bug #11 — Multiple Default Addresses Allowed

| | |
|---|---|
| **Endpoint** | `POST /api/v1/addresses` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/addresses` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 70`, `Content-Type: application/json` |
| **Body** | `{"label": "OFFICE", "street": "Second Default Street", "city": "Mumbai", "pincode": "400002", "is_default": true}` |
| **Expected** | Previous default address should have `is_default` set to `false` |
| **Actual** | Both addresses (and pre-existing ones) remain `is_default: true` — 3 defaults found |

---

### Bug #12 — Wallet Payment Deducts Wrong Amount (Floating Point Error)

| | |
|---|---|
| **Endpoint** | `POST /api/v1/wallet/pay` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/wallet/pay` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 30`, `Content-Type: application/json` |
| **Body** | `{"amount": 100}` |
| **Expected** | Balance decreases by exactly 100.00 |
| **Actual** | Balance decreased by 100.40 ($0.40 extra deducted) |

---

### Module 14: Admin User Detail

---

#### TC-ADM-01 — Valid user lookup returns 200
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users/1` with valid `X-Roll-Number` |
| **Expected** | `200 OK`, response contains correct `user_id` and other fields |
| **Actual** | `200` (Passed) |
| **Justification** | Positive control for looking up a single user by ID. |

---

#### TC-ADM-02 — Non-existent user returns 404
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users/999999` |
| **Expected** | `404 Not Found` |
| **Actual** | `404` (Passed) |
| **Justification** | Missing resource lookup must fail explicitly with 404. |

---

#### TC-ADM-03 — Wrong Data Type for user_id
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users/abc` |
| **Expected** | `400 Bad Request` |
| **Actual** | `404 Not Found` (Bug Found) |
| **Justification** | `user_id` must be an integer. Alphabetic values must be rejected as bad request, instead of pretending missing. |

---

#### TC-ADM-04 — Works without X-User-ID
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users/1` (without `X-User-ID` header) |
| **Expected** | `200 OK` |
| **Actual** | `200` (Passed) |
| **Justification** | Admin endpoints strictly do not require user scoping parameters. |

---

#### TC-ADM-05 — Missing X-Roll-Number
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users/1` (no headers) |
| **Expected** | `401 Unauthorized` |
| **Actual** | `401` (Passed) |
| **Justification** | Mandatory authentication layer must prevent unauthorized access. |

---

### Module 15: Admin Collection Endpoints

These tests cover the 6 admin GET collection endpoints. Each endpoint is tested against three equivalence classes: valid auth (200), missing auth (401), invalid auth (400). Data-specific assertions verify that each response contains the correct fields and includes special records (inactive products, expired coupons, all ticket statuses, all address labels).

---

#### TC-AC-01/02/03 — admin/carts: auth equivalence classes
| | |
|---|---|
| **Input** | EC1: valid header → 200. EC2: no header → 401. EC3: `X-Roll-Number: abc` → 400 |
| **Expected** | 200 / 401 / 400 respectively |
| **Actual** | All correct (Passed) |
| **Justification** | Basic auth gate must apply uniformly to all admin endpoints. |

---

#### TC-AC-04 — admin/carts has items and total fields
| | |
|---|---|
| **Input** | `GET /api/v1/admin/carts` |
| **Expected** | Each cart object contains `items` (list) and `total` (number) |
| **Actual** | Present (Passed) |
| **Justification** | Clients depend on these fields to render cart contents. |

---

#### TC-AC-05/06/07 — admin/orders: auth equivalence classes
| | |
|---|---|
| **Input** | EC1/EC2/EC3 (same pattern) |
| **Expected** | 200 / 401 / 400 |
| **Actual** | All correct (Passed) |
| **Justification** | Auth gate must apply. |

---

#### TC-AC-08 — admin/orders has payment_status and order_status
| | |
|---|---|
| **Input** | `GET /api/v1/admin/orders` |
| **Expected** | Each order has `order_id`, `payment_status`, `order_status` |
| **Actual** | Present (Passed) |
| **Justification** | These are the key fields for order inspection. |

---

#### TC-AC-09/10/11 — admin/products: auth equivalence classes
| | |
|---|---|
| **Input** | EC1/EC2/EC3 |
| **Expected** | 200 / 401 / 400 |
| **Actual** | All correct (Passed) |
| **Justification** | Auth gate must apply. |

---

#### TC-AC-12 — admin/products includes inactive products
| | |
|---|---|
| **Input** | `GET /api/v1/admin/products`, check for `is_active=false` |
| **Expected** | At least one inactive product in the list |
| **Actual** | 40 inactive products found (Passed) |
| **Justification** | Doc: "returns all products including those marked inactive." |

---

#### TC-AC-13/14/15 — admin/coupons: auth equivalence classes
| | |
|---|---|
| **Input** | EC1/EC2/EC3 |
| **Expected** | 200 / 401 / 400 |
| **Actual** | All correct (Passed) |
| **Justification** | Auth gate must apply. |

---

#### TC-AC-16 — admin/coupons includes expired coupons
| | |
|---|---|
| **Input** | `GET /api/v1/admin/coupons`, check for past `expiry_date` |
| **Expected** | At least one expired coupon |
| **Actual** | 6 expired coupons found (e.g. EXPIRED100, DEAL5) (Passed) |
| **Justification** | Doc: "returns all coupons including expired ones." |

---

#### TC-AC-17/18/19 — admin/tickets: auth equivalence classes
| | |
|---|---|
| **Input** | EC1/EC2/EC3 |
| **Expected** | 200 / 401 / 400 |
| **Actual** | All correct (Passed) |
| **Justification** | Auth gate must apply. |

---

#### TC-AC-20 — admin/tickets includes all statuses
| | |
|---|---|
| **Input** | `GET /api/v1/admin/tickets`, check status values |
| **Expected** | OPEN, IN_PROGRESS, and CLOSED all present |
| **Actual** | All three statuses found (Passed) |
| **Justification** | Doc: "returns all support tickets across all users." |

---

#### TC-AC-21/22/23 — admin/addresses: auth equivalence classes
| | |
|---|---|
| **Input** | EC1/EC2/EC3 |
| **Expected** | 200 / 401 / 400 |
| **Actual** | All correct (Passed) |
| **Justification** | Auth gate must apply. |

---

#### TC-AC-24 — admin/addresses includes all label types
| | |
|---|---|
| **Input** | `GET /api/v1/admin/addresses`, check label values |
| **Expected** | HOME, OFFICE, and OTHER all present |
| **Actual** | All three labels found (Passed) |
| **Justification** | Verifies that all three valid address labels exist in the dataset. |

---

### Module 11: Missing Required Fields

These tests send requests with required fields deliberately omitted. The server must reject all of them with `400 Bad Request` rather than crashing or silently accepting null values.

---

#### TC-MF-01 — cart/add missing product_id
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"quantity": 2}` (no product_id) |
| **Expected** | `400 Bad Request` |
| **Actual** | `404 Not Found` (Bug Found) |
| **Justification** | Missing required field should be a client error (400), not a resource-not-found (404). |

---

#### TC-MF-02 — cart/add missing quantity
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 1}` (no quantity) |
| **Expected** | `400 Bad Request` |
| **Actual** | `200 OK` (Bug Found) |
| **Justification** | Server accepted the add with no quantity — quantity defaulted silently instead of being rejected. |

---

#### TC-MF-03 — cart/add empty body
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `404 Not Found` (Bug Found) |
| **Justification** | Empty body means all fields missing — must be 400, not 404. |

---

#### TC-MF-04 — checkout missing payment_method
| | |
|---|---|
| **Input** | `POST /api/v1/checkout` `{}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | payment_method is mandatory. Missing it must be caught. |

---

#### TC-MF-05 — coupon/apply missing coupon_code
| | |
|---|---|
| **Input** | `POST /api/v1/coupon/apply` `{}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | coupon_code is the only input field. Empty body must fail. |

---

#### TC-MF-06/07 — wallet/add and wallet/pay missing amount
| | |
|---|---|
| **Input** | `POST /api/v1/wallet/add` `{}` and `POST /api/v1/wallet/pay` `{}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Amount is required for all wallet operations. Missing it must be rejected. |

---

#### TC-MF-08/09 — support/ticket missing subject or message
| | |
|---|---|
| **Input** | Send ticket with only message (no subject), then with only subject (no message) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Both fields are required. Either missing must be rejected. |

---

#### TC-MF-10/11/12 — addresses missing street, pincode, label
| | |
|---|---|
| **Input** | POST address omitting each required field one at a time |
| **Expected** | `400 Bad Request` for each |
| **Actual** | `400` (Passed) |
| **Justification** | All address fields are mandatory. Missing any one must fail validation. |

---

#### TC-MF-13/14 — profile update missing name or phone
| | |
|---|---|
| **Input** | PUT profile with only phone (no name), then only name (no phone) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Both name and phone are required for profile update. |

---

#### TC-MF-15/16 — reviews missing rating or comment
| | |
|---|---|
| **Input** | POST review with only comment (no rating), then only rating (no comment) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Both fields are required to create a review. |

---

### Module 12: Wrong Data Types

These tests send the correct field names but with the wrong data type (e.g., string where integer is required). The server must reject them with `400`.

---

#### TC-WT-01 — cart/add quantity as string "two"
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 1, "quantity": "two"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | quantity must be an integer. String values must be caught before processing. |

---

#### TC-WT-02 — cart/add product_id as string "abc"
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": "abc", "quantity": 1}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | product_id must be an integer. Alphabetic input must not be looked up. |

---

#### TC-WT-03 — cart/add quantity as float 1.5
| | |
|---|---|
| **Input** | `POST /api/v1/cart/add` `{"product_id": 1, "quantity": 1.5}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Fractional quantities are meaningless for discrete items. Float must be rejected. |

---

#### TC-WT-04 — wallet/add amount as string "hundred"
| | |
|---|---|
| **Input** | `POST /api/v1/wallet/add` `{"amount": "hundred"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Amount must be numeric. A word string must not be coerced to 0 silently. |

---

#### TC-WT-05 — wallet/pay amount as boolean true
| | |
|---|---|
| **Input** | `POST /api/v1/wallet/pay` `{"amount": true}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Boolean `true` coerces to `1` in many languages. Must be explicitly rejected for financial fields. |

---

#### TC-WT-06 — checkout payment_method as integer 1
| | |
|---|---|
| **Input** | `POST /api/v1/checkout` `{"payment_method": 1}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | payment_method must be a string enum (COD/WALLET/CARD). Integer input must fail. |

---

#### TC-WT-07/08 — reviews rating as string or float
| | |
|---|---|
| **Input** | `{"rating": "five", "comment": "Test"}` and `{"rating": 4.5, "comment": "Test"}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Rating must be a whole integer 1–5. Strings and floats must be rejected. |

---

#### TC-WT-09 — addresses pincode as integer 500001
| | |
|---|---|
| **Input** | `POST /api/v1/addresses` with `"pincode": 500001` (integer, not string) |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Pincode must be a string (to preserve leading zeros). Integer type must be rejected. |

---

#### TC-WT-10 — support/ticket subject as integer
| | |
|---|---|
| **Input** | `{"subject": 12345, "message": "Valid message."}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | subject must be a string. An integer must not be accepted as a subject. |

---

#### TC-WT-11 — profile phone as integer
| | |
|---|---|
| **Input** | `PUT /api/v1/profile` `{"name": "Valid Name", "phone": 9876543210}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | Phone must be a string of exactly 10 digits. Integer format cannot preserve leading zeros. |

---

#### TC-WT-12 — coupon/apply coupon_code as integer
| | |
|---|---|
| **Input** | `POST /api/v1/coupon/apply` `{"coupon_code": 75}` |
| **Expected** | `400 Bad Request` |
| **Actual** | `400` (Passed) |
| **Justification** | coupon_code is a string key. Integer 75 must not be cast to "75" and looked up. |

---

## 3.2 Additional Bug Reports (from Missing Field Tests)

### Bug #13 — cart/add with missing product_id returns 404 instead of 400

| | |
|---|---|
| **Endpoint** | `POST /api/v1/cart/add` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/cart/add` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 15`, `Content-Type: application/json` |
| **Body** | `{"quantity": 2}` |
| **Expected** | `400 Bad Request` — product_id is a required field |
| **Actual** | `404 Not Found` — server tried to look up product None and returned 404 |

---

### Bug #14 — cart/add with missing quantity returns 200 (silently accepted)

| | |
|---|---|
| **Endpoint** | `POST /api/v1/cart/add` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/cart/add` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 15`, `Content-Type: application/json` |
| **Body** | `{"product_id": 1}` |
| **Expected** | `400 Bad Request` — quantity is a required field |
| **Actual** | `200 OK` — server added the item with a default/null quantity, corrupting cart state |

---

### Bug #15 — cart/add with empty body returns 404 instead of 400

| | |
|---|---|
| **Endpoint** | `POST /api/v1/cart/add` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/cart/add` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 15`, `Content-Type: application/json` |
| **Body** | `{}` |
| **Expected** | `400 Bad Request` — all required fields missing |
| **Actual** | `404 Not Found` — same root cause as Bug #13 |

---

### Bug #16 — admin/users/{user_id} Wrong Error Code on non-integer Input

| | |
|---|---|
| **Endpoint** | `GET /api/v1/admin/users/{user_id}` |
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/admin/users/abc` |
| **Headers** | `X-Roll-Number: 2024101112` |
| **Body** | *(none)* |
| **Expected** | `400 Bad Request` — `abc` is an invalid integer data-type |
| **Actual** | `404 Not Found` — returning generic missing not-found instead of explicit data parsing error |

---

### Bug #17 — Phone Accepts Letters (Only Checks Length, Not Digits)

| | |
|---|---|
| **Endpoint** | `PUT /api/v1/profile` |
| **Method** | PUT |
| **URL** | `http://localhost:8080/api/v1/profile` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 70`, `Content-Type: application/json` |
| **Body** | `{"name": "Test User", "phone": "98765abcde"}` |
| **Expected** | `400 Bad Request` — doc says "The phone number must be exactly 10 digits" |
| **Actual** | `200 OK` — server only validates string length (10 chars), not that all chars are digits |

---

### Bug #18 — Address Pincode Accepts Letters (Only Checks Length, Not Digits)

| | |
|---|---|
| **Endpoint** | `POST /api/v1/addresses` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/addresses` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 70`, `Content-Type: application/json` |
| **Body** | `{"label": "HOME", "street": "Main Street", "city": "Hyd", "pincode": "50abc1", "is_default": false}` |
| **Expected** | `400 Bad Request` — doc says "The pincode must be exactly 6 digits" |
| **Actual** | `200 OK` — server only validates length (6 chars), not that all chars are digits |

---

### Bug #19 — Review on Non-Existent Product Returns 200

| | |
|---|---|
| **Endpoint** | `POST /api/v1/products/{product_id}/reviews` |
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/products/999999/reviews` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 90`, `Content-Type: application/json` |
| **Body** | `{"rating": 3, "comment": "Test review"}` |
| **Expected** | `404 Not Found` — product 999999 does not exist |
| **Actual** | `200 OK` — server creates an orphan review for a non-existent product |

---

### Bug #20 — Non-existent X-User-ID Returns 404 Instead of 400

| | |
|---|---|
| **Endpoint** | `GET /api/v1/profile` |
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/profile` |
| **Headers** | `X-Roll-Number: 2024101112`, `X-User-ID: 999999` |
| **Body** | *(none)* |
| **Expected** | `400 Bad Request` — doc says "If missing or invalid, the server returns a 400 error" |
| **Actual** | `404 Not Found` — server returns 404 for non-existent resource instead of 400 validation error |

---

### Module 13: JSON Response Structures

These tests verify that every major endpoint returns a proper JSON object with the correct fields. A 200 status code alone is not sufficient — the response must contain all the fields that clients depend on.

---

#### TC-STR-01 — Admin users response has all required fields
| | |
|---|---|
| **Input** | `GET /api/v1/admin/users` |
| **Expected** | `200 OK`, each user has: `user_id`, `name`, `email`, `phone`, `wallet_balance`, `loyalty_points` |
| **Actual** | All fields present (Passed) |
| **Justification** | Clients crash if expected fields are absent. Structure must be stable. |

---

#### TC-STR-02 — Admin products response has all fields
| | |
|---|---|
| **Input** | `GET /api/v1/admin/products` |
| **Expected** | Each product has: `product_id`, `name`, `category`, `price`, `stock_quantity`, `is_active` |
| **Actual** | All fields present (Passed) |
| **Justification** | `is_active` field is critical — its absence would break inactive product filtering. |

---

#### TC-STR-03 — Admin coupons response includes discount fields
| | |
|---|---|
| **Input** | `GET /api/v1/admin/coupons` |
| **Expected** | Each coupon has: `coupon_code`, `discount_type`, `discount_value`, `min_cart_value`, `expiry_date` |
| **Actual** | All fields present (Passed) |
| **Justification** | Verifies coupon rule fields are returned so discount calculations can be validated. |

---

#### TC-STR-05 — Profile response has user fields
| | |
|---|---|
| **Input** | `GET /api/v1/profile` |
| **Expected** | Object with `user_id`, `name`, `email`, `phone` |
| **Actual** | All fields present (Passed) |
| **Justification** | Profile is the identity source. Missing fields break the UI display. |

---

#### TC-STR-06/07 — Products list and detail have correct fields
| | |
|---|---|
| **Input** | `GET /api/v1/products` and `GET /api/v1/products/1` |
| **Expected** | Both have `product_id`, `name`, `category`, `price`, `stock_quantity` |
| **Actual** | All fields present (Passed) |
| **Justification** | Product cards depend on all these fields to render correctly. |

---

#### TC-STR-08 — Cart response has `items` list and `total`
| | |
|---|---|
| **Input** | `GET /api/v1/cart` |
| **Expected** | Object with `items` (list) and `total`/`cart_total` (number) |
| **Actual** | Both fields present (Passed) |
| **Justification** | Cart UI breaks if `items` or `total` is missing from the response. |

---

#### TC-STR-09/10 — Wallet and Loyalty return balance/points
| | |
|---|---|
| **Input** | `GET /api/v1/wallet` and `GET /api/v1/loyalty` |
| **Expected** | Wallet: `balance` field. Loyalty: `points` field. |
| **Actual** | Both present (Passed) |
| **Justification** | These are the primary display values for each feature. |

---

#### TC-STR-11/12/13 — Orders, Addresses, Tickets return lists
| | |
|---|---|
| **Input** | `GET /orders`, `GET /addresses`, `GET /support/tickets` |
| **Expected** | All return JSON arrays |
| **Actual** | All return arrays (Passed) |
| **Justification** | List endpoints must return arrays. A dict or null would crash list rendering. |

---

#### TC-STR-14 — Reviews response has `average_rating` and `reviews` list
| | |
|---|---|
| **Input** | `GET /api/v1/products/1/reviews` |
| **Expected** | Object with `average_rating` (number) and `reviews` (list) |
| **Actual** | Both present (Passed) |
| **Justification** | The average rating display is a key feature — its field must be present and named correctly. |

---

#### TC-STR-16 — POST address response includes `address_id`
| | |
|---|---|
| **Input** | `POST /api/v1/addresses` with valid data |
| **Expected** | `201 Created`, response includes `address_id` |
| **Actual** | `address_id` present (Passed) |
| **Justification** | Clients need `address_id` immediately after creation for update/delete operations. |

---

## 3.3 Test Results Summary

| Module | Tests Run | Passed | Failed |
|--------|-----------|--------|--------|
| Authentication | 8 | 7 | 1 |
| Products | 10 | 9 | 1 |
| Cart | 12 | 9 | 3 |
| Coupons | 6 | 4 | 2 |
| Checkout | 6 | 6 | 0 |
| Wallet | 8 | 7 | 1 |
| Orders | 6 | 5 | 1 |
| Reviews | 12 | 11 | 1 |
| Tickets | 9 | 7 | 2 |
| Profile & Addresses | 27 | 24 | 3 |
| Missing Fields | 16 | 13 | 3 |
| Wrong Data Types | 12 | 12 | 0 |
| Admin User Detail | 5 | 4 | 1 |
| Admin Collections | 28 | 28 | 0 |
| Loyalty Points | 6 | 6 | 0 |
| **JSON Response Structures** | **16** | **16** | **0** |
| **TOTAL** | **187** | **168** | **19 bugs** |

---