from integration.code.inventory import Inventory

class Results:
    """Records race outcomes, updates rankings, and handles prize money."""

    def __init__(self, inventory_module: Inventory):
        self.inventory = inventory_module
        self.driver_rankings = {} # Tracks ranking points for each driver

    def record_outcome(self, race_data: dict, placement: int, prize_money: int, car_damaged: bool = False):
        driver = race_data["driver"]
        car = race_data["car"]

        # 1. Update Rankings
        if driver not in self.driver_rankings:
            self.driver_rankings[driver] = 0
            
        if placement == 1:
            self.driver_rankings[driver] += 10 # 10 points for 1st place
            print(f"Ranking updated: {driver} earned 10 ranking points!")

        # 2. Business Rule: Race results should update the cash balance in the Inventory.
        if prize_money > 0:
            # We calculate and display the prize allocation
            print(f"Prize money allocated: ${prize_money}")
            self.inventory.update_cash(prize_money)

        # 3. Handle car damage during race
        if car_damaged:
            self.inventory.set_car_damaged(car)
            print(f"WARNING: The {car} sustained damage during the race and needs repairs!")
