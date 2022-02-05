import pytest
from bulkmail.internal.core.recipient import Recipient


def test_create_recipient():
    address = 1
    result = Recipient(address)

    assert result.get_address() == address


def test_recipients_equals():
    address = 1
    result = Recipient(address)

    assert result == result


@pytest.mark.parametrize(
    "recipient_1, recipient_2",
    [
        (Recipient(1), Recipient(2)),
    ],
    ids=["By address"],
)
def test_recipients_not_equals(recipient_1, recipient_2):
    assert recipient_1 != recipient_2
