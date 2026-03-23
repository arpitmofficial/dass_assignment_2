from integration.code.registration import Registration
from integration.code.inventory import Inventory

class RepairShop:
    """Custom Module 1: Fixes damaged cars using mechanics and inventory parts."""

    def __init__(self, registration_module: Registration, inventory_module: Inventory):
        self.registration = registration_module
        self.inventory = inventory_module

    def fix_car(self, car_name: str, mechanic_name: str, parts_cost: int):
        """Repairs a car. Requires a mechanic and spare parts."""
        
        # Integration Rule 1: We must verify this person is actually a mechanic
        member = self.registration.get_member(mechanic_name)
        if member.role.lower() != "mechanic":
            raise ValueError(f"Repair failed! {mechanic_name} is a {member.role}, not a mechanic.")

        # Integration Rule 2: We must have enough spare parts in the generic inventory
        try:
            self.inventory.use_parts(parts_cost)
        except ValueError as e:
            raise ValueError(f"Repair on {car_name} failed due to Inventory: {e}")

        print(f"Repair Shop: {mechanic_name} successfully repaired {car_name} using {parts_cost} parts.")
        return True
