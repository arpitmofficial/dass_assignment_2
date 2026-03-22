class CrewMember:
    """Represents a single registered member."""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def __str__(self):
        return f"{self.name} - Role: {self.role}"


class Registration:
    """Module responsible for registering and tracking crew members."""
    def __init__(self):
        # We use a dictionary to store members by name for quick lookup.
        self.members_db = {}

    def register_member(self, name: str, role: str) -> CrewMember:
        """Registers a new crew member with a name and role."""
        if self.is_registered(name):
            raise ValueError(f"Member '{name}' is already registered!")
        
        # Create a new member object and store it
        new_member = CrewMember(name, role)
        self.members_db[name] = new_member
        print(f"Successfully registered: {new_member}")
        return new_member

    def get_member(self, name: str) -> CrewMember:
        """Retrieves a registered member."""
        if not self.is_registered(name):
            raise ValueError(f"Member '{name}' not found. Please register first.")
        return self.members_db[name]

    def is_registered(self, name: str) -> bool:
        """Checks if a person belongs to the crew."""
        return name in self.members_db
