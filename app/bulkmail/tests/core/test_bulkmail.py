import datetime

import pytest
from bulkmail.internal.core.bulkmail import Bulkmail, BulkmailInfo
from bulkmail.internal.core.recipient import Recipient
from bulkmail.internal.exceptions import EmptyBulkmailError


def test_create_bulmail_info(freezer):
    bi = BulkmailInfo(
        title="Title",
        created=datetime.datetime.now(),
        customer="Customer_name",
        price=10.5,
    )
    assert bi.title == "Title"
    assert bi.customer == "Customer_name"
    assert bi.price == 10.5


def test_bulkmail_info_equals(freezer):
    assert BulkmailInfo(
        title="Title",
        created=datetime.datetime.now(),
        customer="Customer_name",
        price=10.5,
    ) == BulkmailInfo(
        title="Title",
        created=datetime.datetime.now(),
        customer="Customer_name",
        price=10.5,
    )


@pytest.mark.parametrize(
    "f, s",
    [
        (
            BulkmailInfo(
                title="Title",
                created=datetime.datetime.now(),
                customer="Customer_name",
                price=10.4,
            ),
            BulkmailInfo(
                title="Title",
                created=datetime.datetime.now(),
                customer="Customer_name",
                price=10.5,
            ),
        ),
        (
            BulkmailInfo(
                title="Title",
                created=datetime.datetime.now(),
                customer="Customer_1",
                price=10.5,
            ),
            BulkmailInfo(
                title="Title",
                created=datetime.datetime.now(),
                customer="Customer_2",
                price=10.5,
            ),
        ),
        (
            BulkmailInfo(
                title="Title_1",
                created=datetime.datetime.now(),
                customer="Customer_1",
                price=10.5,
            ),
            BulkmailInfo(
                title="Title_2",
                created=datetime.datetime.now(),
                customer="Customer_1",
                price=10.5,
            ),
        ),
    ],
    ids=[
        "By price",
        "By customer",
        "By title",
    ],
)
def test_bulkmail_info_not_equal(f: BulkmailInfo, s: BulkmailInfo, freezer):
    assert f != s


@pytest.mark.parametrize("count", [1, 2, 3, 10, 123])
def test_get_price_by_recipient(message, bulkmail_info, count):
    recipients_list = [Recipient(address=123) for _ in range(count)]
    bulkmail = Bulkmail(
        message=message, recipients_list=recipients_list, info=bulkmail_info
    )

    assert bulkmail.get_price_by_recipient() == round(
        bulkmail_info.price / len(recipients_list), 2
    )
    print(bulkmail.get_price_by_recipient())


def test_create_bulkmail(message, bulkmail_info, recipients_list):
    bulkmail = Bulkmail(
        message=message, recipients_list=recipients_list, info=bulkmail_info
    )

    assert bulkmail.message == message
    assert bulkmail.recipients_list == recipients_list
    assert bulkmail.info == bulkmail_info


def test_create_bulkmail_without_recipients(message, bulkmail_info):
    with pytest.raises(EmptyBulkmailError):
        recipients_list = []
        Bulkmail(message=message, recipients_list=recipients_list, info=bulkmail_info)


def test_bulkmail_equals(message, recipients_list, bulkmail_info):
    assert Bulkmail(
        message=message, recipients_list=recipients_list, info=bulkmail_info
    ) == Bulkmail(message=message, recipients_list=recipients_list, info=bulkmail_info)


def test_bulkmail_not_equals(message, recipients_list, bulkmail_info):
    # TODO: Parametrize it
    other_info = BulkmailInfo(
        title="Title_1",
        created=datetime.datetime.now(),
        customer="Customer_name",
        price=10.5,
    )
    other_recipients_list = [Recipient(address=321)]

    assert Bulkmail(
        message=message, recipients_list=recipients_list, info=bulkmail_info
    ) != Bulkmail(
        message=message, recipients_list=other_recipients_list, info=other_info
    )
