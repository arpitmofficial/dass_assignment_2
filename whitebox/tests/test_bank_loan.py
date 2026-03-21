import pytest
from moneypoly.bank import Bank
from moneypoly.player import Player

def test_bank_loan_deduction():
    """
    Test Case: Verify that issuing a loan decreases the bank's total funds.
    Reason: A bank loan transfers money from the bank to the player. The bank's funds must decrease.
    Expected: Bank funds = Initial Funds - Loan Amount
    Actual Error Found: give_loan() adds money to player but ignores deducting from self._funds.
    """
    bank = Bank()
    player = Player("Alice", balance=0)
    
    initial_funds = bank.get_balance()
    loan_amount = 500
    
    bank.give_loan(player, loan_amount)
    
    assert bank.get_balance() == initial_funds - loan_amount, "Bank funds were not reduced after giving a loan."
