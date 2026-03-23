from integration.code.registration import Registration
from integration.code.inventory import Inventory

class MissionPlanning:
    """Assigns missions and verifies required roles are available."""

    def __init__(self, registration_module: Registration, inventory_module: Inventory):
        self.registration = registration_module
        self.inventory = inventory_module

    def assign_mission(self, mission_name: str, required_role: str, member_name: str):
        member = self.registration.get_member(member_name)

        # Business Rule: Missions cannot start if required roles are unavailable/mismatched.
        if member.role != required_role:
            raise ValueError(f"Mission failed! '{mission_name}' requires a {required_role}.")

        # Business Rule: If a car is damaged during a race, a mission requiring a mechanic 
        # must check for availability before proceeding.
        if required_role == "mechanic":
            damaged_cars = [c for c, status in self.inventory.cars.items() if status == "damaged"]
            if damaged_cars:
                raise ValueError(
                    f"Mechanic '{member_name}' is unavailable for missions right now! "
                    f"They must stay at the garage to fix damaged cars: {damaged_cars}"
                )

        print(f"Mission '{mission_name}' assigned to {member_name} successfully.")
        return True
