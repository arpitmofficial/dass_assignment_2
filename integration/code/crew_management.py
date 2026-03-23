from integration.code.registration import Registration

class CrewManagement:
    """Manages roles and records skill levels for each."""
    
    VALID_ROLES = ["driver", "mechanic", "strategist"]

    def __init__(self, registration_module: Registration):
        self.registration = registration_module
        self.skills = {}

    def assign_role(self, name: str, role: str):
        """Business Rule: A crew member must be registered before a role can be assigned."""
        if not self.registration.is_registered(name):
            raise ValueError(f"Cannot assign role: {name} is not registered!")
            
        if role.lower() not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {role}")

        # Assign the role securely
        member = self.registration.get_member(name)
        member.role = role.lower()
        print(f"Assigned role '{role}' to {name}.")

    def assign_skill_level(self, name: str, level: int):
        if not self.registration.is_registered(name):
            raise ValueError(f"Cannot assign skill: {name} is not registered!")
            
        self.skills[name] = level
        print(f"Recorded skill level {level}/100 for {name}.")

    def get_skill_level(self, name: str) -> int:
        return self.skills.get(name, 0)
