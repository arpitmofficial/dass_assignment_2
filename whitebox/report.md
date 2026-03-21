# White Box Testing Report - Code Quality Analysis

# 1.2

## Iteration 1: `moneypoly/main.py`
- **Fixes Applied**:
  - Added module-level docstring.
  - Added function documentations for `get_player_names()` and `main()`.

## Iteration 2: `moneypoly/bank.py`
- **Fixes Applied**:
  - Inserted missing module docstring.
  - Inserted missing class docstring for `Bank`.
  - Removed unused `math` import.

## Iteration 3: `moneypoly/board.py`
- **Fixes Applied**:
  - Added missing module docstring.
  - Fixed singleton comparison (`== True` to `is True`).

## Iteration 4: `moneypoly/cards.py`
- **Fixes Applied**:
  - Added module-level docstring.
  - Formatted dictionaries to resolve line-too-long warnings.

## Iteration 5: `moneypoly/config.py`
- **Fixes Applied**:
  - Added module-level docstring.

## Iteration 6: `moneypoly/dice.py`
- **Fixes Applied**:
  - Added module docstring.
  - Removed unused `BOARD_SIZE` import.
  - Initialized `doubles_streak` in `__init__` to fix `attribute-defined-outside-init`.

## Iteration 7: `moneypoly/game.py`
- **Fixes Applied**:
  - Added module-level docstring.
  - Removed unused `os` and `GO_TO_JAIL_POSITION` imports.
  - Fixed f-string without interpolation.
  - Removed unnecessary `elif` after `break`.
  - Removed superfluous parentheses around `not` conditions.
  - Added missing final newline.

## Iteration 8: `moneypoly/player.py`
- **Fixes Applied**:
  - Added missing module docstring.
  - Removed unused `sys` import.
  - Resolved unused `old_position` variable by properly implementing the Go salary award logic.
  - Added missing final newline.

## Iteration 9: `moneypoly/property.py`
- **Fixes Applied**:
  - Added missing module docstring.
  - Added missing class docstring for `PropertyGroup`.
  - Removed unnecessary `else` block after `return` in `unmortgage()`.

## Iteration 10: `moneypoly/ui.py`
- **Fixes Applied**:
  - Added module docstring.
  - Specified `ValueError` for the bare `except` block in `safe_int_input()`.

## Iteration 11: `moneypoly/player.py` (Too Many Attributes)
- **Fixes Applied**:
  - Removed unused `is_eliminated` attribute from `Player` class in `player.py` and its assignment in `game.py`.
  - This successfully dropped the `Player` instance attribute count from 8 to 7, resolving the `too-many-instance-attributes (R0902)` warning without pylint disable comments.

## Iteration 12: `moneypoly/game.py`
- **Fixes Applied**:
  - Fixed `too-many-instance-attributes` by removing redundant attributes and combining some.
  - Fixed `too-many-branches` by combining identical branches and moving a specific branch loop to a new helper function.

## Iteration 13: `moneypoly/property.py` and `moneypoly/board.py`
- **Fixes Applied**:
  - Fixed `too-many-arguments` and `too-many-positional-arguments` by removing the `group` argument from the `Property` constructor. Properties are now added to their group after instantiation in `board.py`.
  - Fixed `too-many-instance-attributes` by removing the unused `self.houses` variable and converting `self.mortgage_value` into a dynamically calculated `@property`.



