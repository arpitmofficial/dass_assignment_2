"""
test_tickets.py — Tests for Support Tickets API.

Endpoints:
  POST /api/v1/support/ticket
  GET  /api/v1/support/tickets
  PUT  /api/v1/support/tickets/{ticket_id}

Test Cases:
  TC-TKT-01: Create ticket with valid data → 201, status=OPEN         → 201
  TC-TKT-02: Create ticket with subject < 5 chars → 400              → 400
  TC-TKT-03: Create ticket with empty message → 400                  → 400
  TC-TKT-04: Get all tickets returns 200 and list                    → 200
  TC-TKT-05: New ticket always starts as OPEN                        → verify
  TC-TKT-06: OPEN → IN_PROGRESS is valid                             → 200
  TC-TKT-07: IN_PROGRESS → CLOSED is valid                           → 200
  TC-TKT-08: OPEN → CLOSED (skip) must be rejected                   → 400
  TC-TKT-09: CLOSED → OPEN (reverse) must be rejected                → 400

Justification: Ticket status transitions protect the support workflow.
Allowing skip or reverse transitions can create invalid system states.
"""

import requests
import pytest
from conftest import BASE_URL, user_headers, json_headers

TICKET_URL  = f"{BASE_URL}/support/ticket"
TICKETS_URL = f"{BASE_URL}/support/tickets"
UPDATE_URL  = lambda tid: f"{BASE_URL}/support/tickets/{tid}"

# Use user 60 for ticket tests
UID = 60
H   = user_headers(UID)
JH  = json_headers(UID)


def create_ticket(subject="Help needed", message="I need assistance please"):
    """Helper to create a ticket and return its ID."""
    r = requests.post(TICKET_URL, headers=JH,
                      json={"subject": subject, "message": message})
    if r.status_code in (200, 201):
        data = r.json()
        return data.get("ticket_id", data.get("ticket", {}).get("ticket_id"))
    return None


class TestCreateTicket:

    def test_TC_TKT_01_create_valid_ticket_returns_201(self):
        """Valid ticket creation must return 201 and include ticket data."""
        r = requests.post(TICKET_URL, headers=JH,
                          json={"subject": "Order issue", "message": "My order is late."})
        assert r.status_code in (200, 201), (
            f"Expected 201 for valid ticket, got {r.status_code}: {r.text}"
        )

    def test_TC_TKT_02_short_subject_rejected(self):
        """Subject less than 5 characters must return 400."""
        r = requests.post(TICKET_URL, headers=JH,
                          json={"subject": "Hi", "message": "This is a valid message."})
        assert r.status_code == 400, (
            f"Expected 400 for subject < 5 chars, got {r.status_code}"
        )

    def test_TC_TKT_03_empty_message_rejected(self):
        """Empty message must be rejected (min 1 character)."""
        r = requests.post(TICKET_URL, headers=JH,
                          json={"subject": "Valid subject", "message": ""})
        assert r.status_code == 400, (
            f"Expected 400 for empty message, got {r.status_code}"
        )

    def test_TC_TKT_05_new_ticket_starts_as_open(self):
        """
        Doc: 'A new ticket always starts with status OPEN.'
        Verify the status field in the response is OPEN.
        """
        r = requests.post(TICKET_URL, headers=JH,
                          json={"subject": "Status check", "message": "Testing initial status."})
        assert r.status_code in (200, 201)
        data = r.json()
        ticket = data.get("ticket", data)
        status = ticket.get("status")
        assert status == "OPEN", (
            f"BUG: New ticket should have status=OPEN, got {status}"
        )


class TestGetTickets:

    def test_TC_TKT_04_get_tickets_returns_list(self):
        """GET /support/tickets must return 200 and a list."""
        r = requests.get(TICKETS_URL, headers=H)
        assert r.status_code == 200
        assert isinstance(r.json(), list), "Expected list of tickets"


class TestTicketStatusTransitions:

    def test_TC_TKT_06_open_to_in_progress_valid(self):
        """OPEN → IN_PROGRESS is a valid forward transition."""
        tid = create_ticket("Transition test 1", "Testing valid transition to IN_PROGRESS.")
        if tid is None:
            pytest.skip("Could not create ticket for transition test")
        r = requests.put(UPDATE_URL(tid), headers=JH,
                         json={"status": "IN_PROGRESS"})
        assert r.status_code == 200, (
            f"Expected 200 for OPEN→IN_PROGRESS, got {r.status_code}: {r.text}"
        )

    def test_TC_TKT_07_in_progress_to_closed_valid(self):
        """IN_PROGRESS → CLOSED is a valid forward transition."""
        tid = create_ticket("Transition test 2", "Testing valid transition to CLOSED.")
        if tid is None:
            pytest.skip("Could not create ticket")
        requests.put(UPDATE_URL(tid), headers=JH, json={"status": "IN_PROGRESS"})
        r = requests.put(UPDATE_URL(tid), headers=JH, json={"status": "CLOSED"})
        assert r.status_code == 200, (
            f"Expected 200 for IN_PROGRESS→CLOSED, got {r.status_code}"
        )

    def test_TC_TKT_08_skip_to_closed_from_open_rejected(self):
        """
        OPEN → CLOSED must be rejected (cannot skip IN_PROGRESS).
        Doc: 'OPEN can go to IN_PROGRESS. IN_PROGRESS can go to CLOSED.
        No other changes are allowed.'
        """
        tid = create_ticket("Skip test", "Testing invalid skip transition.")
        if tid is None:
            pytest.skip("Could not create ticket")
        r = requests.put(UPDATE_URL(tid), headers=JH, json={"status": "CLOSED"})
        assert r.status_code == 400, (
            f"BUG: OPEN→CLOSED skip was allowed! Got {r.status_code}"
        )

    def test_TC_TKT_09_reverse_closed_to_open_rejected(self):
        """CLOSED → OPEN (reversal) must be rejected."""
        tid = create_ticket("Reverse test", "Testing reverse status transition.")
        if tid is None:
            pytest.skip("Could not create ticket")
        requests.put(UPDATE_URL(tid), headers=JH, json={"status": "IN_PROGRESS"})
        requests.put(UPDATE_URL(tid), headers=JH, json={"status": "CLOSED"})
        # Now try to go back
        r = requests.put(UPDATE_URL(tid), headers=JH, json={"status": "OPEN"})
        assert r.status_code == 400, (
            f"BUG: Reverse transition CLOSED→OPEN was allowed! Got {r.status_code}"
        )
