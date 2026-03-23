from integration.code.registration import Registration
from integration.code.inventory import Inventory

class RaceManagement:
    """Creates races and selects appropriate drivers and cars."""

    def __init__(self, registration_module: Registration, inventory_module: Inventory):
        self.registration = registration_module
        self.inventory = inventory_module

    def create_race(self, driver_name: str, car_name: str):
        # Business Rule: Only crew members with the driver role may be entered in a race.
        member = self.registration.get_member(driver_name)
        if member.role != "driver":
            raise ValueError(f"Race entry failed! {driver_name} is a {member.role}, not a 'driver'.")

        # Business Rule: The car must exist and be ready to race.
        if not self.inventory.is_car_ready(car_name):
            raise ValueError(
                f"Race entry failed! Car '{car_name}' is not ready or not in inventory."
            )

        print(f"Race started! Driver: {driver_name} | Car: {car_name}")
        # Return a race payload dictionary that can be passed to Results
        return {"driver": driver_name, "car": car_name}
