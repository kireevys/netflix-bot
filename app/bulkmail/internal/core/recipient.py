from typing import Any


class User:
    def __init__(self, user_id: Any):
        self.user_id = user_id

    def __hash__(self):
        return hash(self.user_id)


class Recipient:
    def __init__(self, address: Any, user: User):
        self.address = address
        self.user = user

    def get_address(self) -> Any:
        return self.address

    def __eq__(self, other: "Recipient"):
        return self.address == other.address and self.user.user_id == other.user.user_id

    def __hash__(self):
        return hash(f"{self.address}{self.user}")

    def __repr__(self):
        return str(hash(self))
