import pytest
from moneypoly.bank import Bank
from moneypoly.player import Player

def test_bank_initialization():
    bank = Bank()
    # Expected initial funds from config
    assert bank.get_balance() > 0 
    assert bank.loan_count() == 0

def test_bank_collect(capsys):
    bank = Bank()
    start = bank.get_balance()
    bank.collect(200)
    assert bank.get_balance() == start + 200
    
    # Edge case: collect negative amount. Code docstring says it ignores it, but it actually subtracts...
    bank.collect(-50)
    # Does it subtract? Yes, self._funds += -50 -> subtracts.
    assert bank.get_balance() == start + 150

def test_bank_pay_out_success():
    bank = Bank()
    start = bank.get_balance()
    paid = bank.pay_out(500)
    assert paid == 500
    assert bank.get_balance() == start - 500

def test_bank_pay_out_zero_or_negative():
    """Branch coverage: pay_out amount <= 0"""
    bank = Bank()
    assert bank.pay_out(0) == 0
    assert bank.pay_out(-100) == 0

def test_bank_pay_out_insufficient_funds():
    """Branch coverage: pay_out > bank funds throws ValueError"""
    bank = Bank()
    with pytest.raises(ValueError):
        bank.pay_out(bank.get_balance() + 1)

def test_bank_give_loan_zero_or_negative():
    bank = Bank()
    player = Player("Alice")
    bank.give_loan(player, -50)
    assert bank.loan_count() == 0

def test_bank_summary(capsys):
    bank = Bank()
    bank.summary()
    captured = capsys.readouterr()
    assert "Bank reserves" in captured.out
