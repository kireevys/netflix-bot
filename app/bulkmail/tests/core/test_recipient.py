import pytest
from bulkmail.internal.core.recipient import Recipient, User


def test_create_recipient():
    address = 1
    user = User(user_id=1)
    result = Recipient(address, user)

    assert result.get_address() == address


def test_create_user():
    user_id = 123
    user = User(user_id)
    assert user.user_id == user_id


def test_recipients_equals():
    address = 1
    user = User(user_id=1)
    result = Recipient(address, user)

    assert result == result


@pytest.mark.parametrize(
    "recipient_1, recipient_2",
    [
        (Recipient(1, User(user_id=1)), Recipient(2, User(user_id=1))),
        (Recipient(1, User(user_id=1)), Recipient(1, User(user_id=2))),
    ],
    ids=["By address", "By user"],
)
def test_recipients_not_equals(recipient_1, recipient_2):
    assert recipient_1 != recipient_2
