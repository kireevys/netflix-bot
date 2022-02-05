from bulkmail.repos import ORMBulkmailRepository
from django.db.models import Q


def test_read(bulkmail, user, db):
    repos = ORMBulkmailRepository()
    repos.save(bulkmail=bulkmail)

    bulkmails = repos.read(Q())

    assert len(bulkmails) == 1
    result = bulkmails[0]

    assert result == bulkmail
