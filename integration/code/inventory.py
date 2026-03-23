class Inventory:
    """Tracks cars, spare parts, tools, and the cash balance."""
    
    def __init__(self, initial_cash: int = 10000):
        self.cash_balance = initial_cash
        self.cars = {}  # Maps car name directly to its status ("ready" or "damaged")
        self.spare_parts = 0
        self.tools = 0

    def add_car(self, car_name: str):
        self.cars[car_name] = "ready"
        print(f"Added car '{car_name}' to the Garage.")

    def set_car_damaged(self, car_name: str):
        if car_name in self.cars:
            self.cars[car_name] = "damaged"

    def repair_car(self, car_name: str):
        if car_name in self.cars:
            self.cars[car_name] = "ready"

    def is_car_ready(self, car_name: str) -> bool:
        return self.cars.get(car_name) == "ready"

    def update_cash(self, amount: int):
        self.cash_balance += amount
        print(f"Updated cash balance: ${self.cash_balance}")

    def add_parts(self, amount: int):
        self.spare_parts += amount

    def buy_parts(self, amount: int, cost_per_part: int = 100):
        # A common sense feature: Buying parts costs cash!
        total_cost = amount * cost_per_part
        self.update_cash(-total_cost)
        self.spare_parts += amount
        print(f"Bought {amount} parts for ${total_cost}.")

    def use_parts(self, amount: int):
        # Subtract the required amount of parts from the garage
        self.spare_parts -= amount
