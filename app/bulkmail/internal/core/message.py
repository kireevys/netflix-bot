from typing import List


class Media:
    def __init__(self, link: str):
        self.link = link

    def __eq__(self, other: "Media"):
        return self.link == other.link

    def __repr__(self):
        return str(hash(self.link))


class Button:
    def __init__(self, text: str, link: str):
        self.text = text
        self.link = link

    def __eq__(self, other: "Button"):
        return self.link == other.link and self.text == other.text

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return f"{self.link}-{self.text}"


class Message:
    def __init__(self, text: str, media: Media, buttons: List[Button]):
        self.text = text
        self.media = media
        self.buttons = buttons

    def __eq__(self, other: "Message"):
        return (
            self.text == other.text
            and self.media == other.media
            and set(self.buttons) == set(other.buttons)
        )

    def __str__(self):
        return f"Message {self.media}-{self.buttons}"

    def __repr__(self):
        return str(self)
