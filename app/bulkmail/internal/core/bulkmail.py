import datetime
from typing import List

from bulkmail.internal.core.message import Message
from bulkmail.internal.core.recipient import Recipient
from bulkmail.internal.exceptions import EmptyBulkmailError


class BulkmailInfo:
    def __init__(self, title: str, created: datetime, customer: str, price: float):
        self.customer = customer
        self.price = price
        self.title = title

    def __eq__(self, other: "BulkmailInfo"):
        return all(
            (
                self.customer == other.customer,
                self.price == other.price,
                self.title == other.title,
            )
        )


class Bulkmail:
    def __init__(
        self, message: Message, recipients_list: List[Recipient], info: BulkmailInfo
    ):
        if not recipients_list:
            raise EmptyBulkmailError

        self.info = info
        self.message = message
        self.recipients_list = recipients_list

    def get_price_by_recipient(self) -> float:
        return round(self.info.price / len(self.recipients_list), 2)

    def __eq__(self, other: "Bulkmail"):
        return (
            self.info == other.info
            and self.message == other.message
            and self.recipients_list == other.recipients_list
        )
