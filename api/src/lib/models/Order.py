from dataclasses import dataclass


@dataclass
class Order:
    title: str
    body: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "body": self.body,
        }
