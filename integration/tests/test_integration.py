"""
Integration Tests for StreetRace Manager
=========================================
These tests verify cross-module interactions as required by the assignment spec.
"""

import pytest
import sys
import os

# Ensure the root folder is in the python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from integration.code.registration import Registration
from integration.code.crew_management import CrewManagement
from integration.code.inventory import Inventory
from integration.code.race_management import RaceManagement
from integration.code.results import Results
from integration.code.mission_planning import MissionPlanning
from integration.code.repair_shop import RepairShop
from integration.code.hall_of_fame import HallOfFame

@pytest.fixture
def system():
    """Initialises and wires together all modules to simulate the live system."""
    reg = Registration()
    inv = Inventory(initial_cash=10000)
    crew = CrewManagement(reg)
    race = RaceManagement(reg, inv)
    results = Results(inv)
    mission = MissionPlanning(reg, inv)
    repair = RepairShop(reg, inv)
    hof = HallOfFame(inv)
    return {"reg": reg, "inv": inv, "crew": crew, "race": race, "results": results, "mission": mission, "repair": repair, "hof": hof}

# 0. Assigning a role without registration should fail
def test_role_assignment_requires_registration(system):
    crew = system["crew"]

    with pytest.raises(ValueError, match="not registered"):
        crew.assign_role("Ghost", "driver")

# 0b. Assigning an invalid role should fail
def test_invalid_role_is_rejected(system):
    reg, crew = system["reg"], system["crew"]

    reg.register_member("Eve")
    with pytest.raises(ValueError, match="Invalid role"):
        crew.assign_role("Eve", "hacker")

# 1. Registering a driver and then entering the driver into a race
def test_valid_driver_can_enter_race(system):
    reg, crew, inv, race = system["reg"], system["crew"], system["inv"], system["race"]
    
    reg.register_member("Alice")
    crew.assign_role("Alice", "driver")
    inv.add_car("SkylineGT")
    
    # Should succeed without ValueError
    payload = race.create_race("Alice", "SkylineGT")
    assert payload["driver"] == "Alice"
    assert payload["car"] == "SkylineGT"

# 2. Attempting to enter a race without a registered driver
def test_unregistered_driver_cannot_race(system):
    inv, race = system["inv"], system["race"]
    inv.add_car("SkylineGT")
    
    # Attempting to race with someone who does not exist in the registration database
    with pytest.raises(ValueError):
        race.create_race("Ghost", "SkylineGT")

# 3. Attempting to enter a race with a registered member who is NOT a driver
def test_non_driver_cannot_race(system):
    reg, crew, inv, race = system["reg"], system["crew"], system["inv"], system["race"]
    
    reg.register_member("Bob")
    crew.assign_role("Bob", "mechanic")
    inv.add_car("SkylineGT")
    
    # Bob is registered, but is a mechanic, not a driver
    with pytest.raises(ValueError, match="not a 'driver'"):
        race.create_race("Bob", "SkylineGT")

# 4. Attempting to race with a damaged car
def test_damaged_car_cannot_race(system):
    reg, crew, inv, race = system["reg"], system["crew"], system["inv"], system["race"]
    
    reg.register_member("Alice")
    crew.assign_role("Alice", "driver")
    inv.add_car("SkylineGT")
    inv.set_car_damaged("SkylineGT")
    
    with pytest.raises(ValueError):
        race.create_race("Alice", "SkylineGT")

# 4b. Attempting to race with a missing car
def test_missing_car_cannot_race(system):
    reg, crew, race = system["reg"], system["crew"], system["race"]

    reg.register_member("Alice")
    crew.assign_role("Alice", "driver")

    with pytest.raises(ValueError):
        race.create_race("Alice", "MissingCar")

# 5. Completing a race and verifying results and prize money update the inventory
def test_race_win_updates_inventory_and_hall_of_fame(system):
    reg, crew, inv, race, results, hof = system["reg"], system["crew"], system["inv"], system["race"], system["results"], system["hof"]
    
    reg.register_member("Alice")
    crew.assign_role("Alice", "driver")
    inv.add_car("SkylineGT")
    
    race_data = race.create_race("Alice", "SkylineGT")
    initial_cash = inv.cash_balance
    
    # Win race, get $2000 prize
    results.record_outcome(race_data, placement=1, prize_money=2000, car_damaged=False)
    hof.add_win("Alice")
    
    # Results module should deposit money into inventory via update_cash
    assert inv.cash_balance == initial_cash + 2000
    assert results.driver_rankings["Alice"] == 10

# 5b. Race damage must mark the car as damaged in Inventory
def test_race_damage_marks_car_damaged(system):
    reg, crew, inv, race, results = system["reg"], system["crew"], system["inv"], system["race"], system["results"]

    reg.register_member("Alice")
    crew.assign_role("Alice", "driver")
    inv.add_car("SkylineGT")

    race_data = race.create_race("Alice", "SkylineGT")
    results.record_outcome(race_data, placement=3, prize_money=0, car_damaged=True)

    assert inv.cars["SkylineGT"] == "damaged"

# 6. Assigning a mission and ensuring correct crew roles are validated
def test_mission_role_validation(system):
    reg, crew, inv, mission = system["reg"], system["crew"], system["inv"], system["mission"]
    
    reg.register_member("Carol")
    crew.assign_role("Carol", "strategist")
    
    # Supposed to work since Carol is indeed a strategist
    assert mission.assign_mission("Recon", "strategist", "Carol") is True
    
    # Supposed to fail since Carol is not a driver
    with pytest.raises(ValueError):
        mission.assign_mission("Delivery", "driver", "Carol")

# 6b. Mission assignment should fail for unregistered member
def test_mission_requires_registered_member(system):
    mission = system["mission"]

    with pytest.raises(ValueError):
        mission.assign_mission("Recon", "strategist", "Ghost")

# 6c. Mechanic missions are allowed when no damaged cars exist
def test_mechanic_mission_allowed_when_no_damage(system):
    reg, crew, mission = system["reg"], system["crew"], system["mission"]

    reg.register_member("Bob")
    crew.assign_role("Bob", "mechanic")

    assert mission.assign_mission("Garage Audit", "mechanic", "Bob") is True

# 7. Mechanic availability blocked if car is damaged from a previous race
def test_mechanic_cannot_start_mission_if_car_is_damaged(system):
    reg, crew, inv, race, results, mission = system["reg"], system["crew"], system["inv"], system["race"], system["results"], system["mission"]
    
    # Driver races and damages a car
    reg.register_member("Alice")
    crew.assign_role("Alice", "driver")
    inv.add_car("SkylineGT")
    race_data = race.create_race("Alice", "SkylineGT")
    results.record_outcome(race_data, placement=2, prize_money=0, car_damaged=True)
    
    # Mechanic tries to take a mission
    reg.register_member("Bob")
    crew.assign_role("Bob", "mechanic")
    
    # Should fail because inventory says a car is damaged, so mechanic must stay at garage
    with pytest.raises(ValueError, match="unavailable"):
        mission.assign_mission("Parts Retrieval", "mechanic", "Bob")

# 8. Repairing a car consumes parts and requires a real mechanic
def test_repair_shop_integration(system):
    reg, crew, inv, repair = system["reg"], system["crew"], system["inv"], system["repair"]
    
    reg.register_member("Bob")
    crew.assign_role("Bob", "mechanic")
    inv.add_car("SkylineGT")
    inv.set_car_damaged("SkylineGT")
    inv.add_parts(10)
    
    repair.fix_car("SkylineGT", "Bob", parts_cost=4)
    inv.repair_car("SkylineGT")  # Complete the repair
    
    assert inv.spare_parts == 6  # 4 parts consumed
    assert inv.is_car_ready("SkylineGT") is True

# 8b. Repair should fail if the assigned member is not a mechanic
def test_repair_shop_requires_mechanic(system):
    reg, crew, inv, repair = system["reg"], system["crew"], system["inv"], system["repair"]

    reg.register_member("Dan")
    crew.assign_role("Dan", "driver")
    inv.add_car("SkylineGT")
    inv.set_car_damaged("SkylineGT")
    inv.add_parts(5)

    with pytest.raises(ValueError, match="not a mechanic"):
        repair.fix_car("SkylineGT", "Dan", parts_cost=2)

# 8c. Repair should fail if there are not enough parts
def test_repair_shop_requires_parts(system):
    reg, crew, inv, repair = system["reg"], system["crew"], system["inv"], system["repair"]

    reg.register_member("Bob")
    crew.assign_role("Bob", "mechanic")
    inv.add_car("SkylineGT")
    inv.set_car_damaged("SkylineGT")
    inv.add_parts(2)

    with pytest.raises(ValueError):
        repair.fix_car("SkylineGT", "Bob", parts_cost=5)

# 9. Hall of Fame bonus is awarded once after three wins
def test_hall_of_fame_bonus_once(system):
    inv, hof = system["inv"], system["hof"]

    initial_cash = inv.cash_balance
    hof.add_win("Alice")
    hof.add_win("Alice")
    hof.add_win("Alice")

    assert inv.cash_balance == initial_cash + 5000

    hof.add_win("Alice")
    assert inv.cash_balance == initial_cash + 5000
