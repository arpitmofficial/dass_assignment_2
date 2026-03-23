from integration.code.inventory import Inventory

class HallOfFame:
    """Custom Module 2: Tracks legendary drivers and provides massive cash bonuses."""

    def __init__(self, inventory_module: Inventory):
        self.inventory = inventory_module
        self.driver_wins = {}
        self.inducted_members = []

    def add_win(self, driver_name: str):
        """Called by the Results module whenever a driver wins."""
        self.driver_wins[driver_name] = self.driver_wins.get(driver_name, 0) + 1
        
        # Rule: 3 wins gets you into the Hall of Fame
        wins = self.driver_wins[driver_name]
        
        if wins >= 3 and driver_name not in self.inducted_members:
            self.inducted_members.append(driver_name)
            
            print(f"*** HALL OF FAME: {driver_name} has been inducted! ***")
            print("*** HALL OF FAME: Awarded a massive $5,000 sponsorship bonus! ***")
            
            # Integration Rule: The bonus gets deposited directly into the main inventory
            self.inventory.update_cash(5000)
