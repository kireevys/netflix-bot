from bulkmail.internal.core.recipient import Recipient
from bulkmail.models import UserTag
from bulkmail.repos import ORMRecipientRepository
from netflix_bot import models as netflix_models


def test_read(db):
    address = 123
    netflix_models.User.objects.create(user_id=address)

    repos = ORMRecipientRepository()
    query = ORMRecipientRepository.Filters.ANY

    result = repos.read(query)

    assert len(result) == 1
    assert isinstance(result[0], Recipient)

    assert result[0].get_address() == address


def test_read_with_filter_test(db):
    address = 123
    user_test = netflix_models.User.objects.create(user_id=address)
    netflix_models.User.objects.create(user_id=432)

    UserTag.objects.create(user=user_test, tag=UserTag.Tags.TEST)

    core_test_user = Recipient(address=user_test.user_id)

    repos = ORMRecipientRepository()
    query = ORMRecipientRepository.Filters.TEST

    result = repos.read(query)

    assert len(result) == 1
    assert result[0] == core_test_user


def test_orm_to_core(db):
    address = 123

    d_user = netflix_models.User.objects.create(user_id=address)

    core_recipient = Recipient(address=d_user.user_id)

    repos = ORMRecipientRepository()
    result = repos._orm_to_core(d_user)

    assert result == core_recipient
