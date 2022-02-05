from typing import Any


class Recipient:
    def __init__(self, address: Any):
        self.address = address

    def get_address(self) -> Any:
        return self.address

    def __eq__(self, other: "Recipient"):
        return self.address == other.address

    def __hash__(self):
        return hash(f"{self.address}")

    def __repr__(self):
        return str(hash(self))
