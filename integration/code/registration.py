class CrewMember:
    def __init__(self, name: str):
        self.name = name
        self.role = "Unassigned"  # Role is assigned AFTER registration

class Registration:
    """Registers new crew members, storing name and role."""
    def __init__(self):
        self.members_db = {}

    def register_member(self, name: str):
        if name in self.members_db:
            raise ValueError(f"Member '{name}' is already registered!")
        
        member = CrewMember(name)
        self.members_db[name] = member
        print(f"Successfully registered: {name}")

    def get_member(self, name: str) -> CrewMember:
        if name not in self.members_db:
            raise ValueError(f"Member '{name}' is not registered.")
        return self.members_db[name]

    def fire_member(self, name: str):
        """Common Sense Feature: Removing someone from the crew."""
        if name not in self.members_db:
            raise ValueError(f"Cannot fire '{name}' because they are not registered.")
        
        self.members_db.pop(name)
        print(f"You have fired {name} from the crew.")

    def is_registered(self, name: str) -> bool:
        return name in self.members_db
