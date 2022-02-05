from bulkmail.internal.core.recipient import Recipient, User
from bulkmail.models import UserTag
from bulkmail.repos import ORMRecipientRepository
from netflix_bot import models as netflix_models


def test_read(db):
    user_id = 1
    address = 123
    netflix_models.User.objects.create(user_id=address)

    repos = ORMRecipientRepository()
    query = ORMRecipientRepository.Filters.ANY

    result = repos.read(query)

    assert len(result) == 1
    assert isinstance(result[0], Recipient)

    assert result[0].get_address() == address
    assert result[0].user.user_id == user_id


def test_read_with_filter_test(db):
    address = 123
    user_test = netflix_models.User.objects.create(user_id=address)
    netflix_models.User.objects.create(user_id=432)

    UserTag.objects.create(user=user_test, tag=UserTag.Tags.TEST)

    core_test_user = Recipient(
        address=user_test.user_id, user=User(user_id=user_test.pk)
    )

    repos = ORMRecipientRepository()
    query = ORMRecipientRepository.Filters.TEST

    result = repos.read(query)

    assert len(result) == 1
    assert result[0] == core_test_user


def test_orm_to_core(db):
    address = 123

    d_user = netflix_models.User.objects.create(user_id=address)

    core_recipient = Recipient(address=d_user.user_id, user=User(d_user.pk))

    repos = ORMRecipientRepository()

    result = repos._orm_to_core(d_user)

    print()
    print(core_recipient.address, core_recipient.user.user_id)
    print(result.address, result.user.user_id)

    assert result == core_recipient
