from bulkmail.models import DjangoBulkmail, Envelope
from bulkmail.repos import ORMBulkmailRepository
from django.db.models import Q
from netflix_bot.models import User


def test_create_bulkmail(bulkmail, db):
    User.objects.create(user_id=bulkmail.recipients_list[0].address)

    repos = ORMBulkmailRepository()
    repos.save(bulkmail=bulkmail)

    bulkmails = DjangoBulkmail.objects.all()
    assert bulkmails.exists()

    d_bulkmail: DjangoBulkmail = bulkmails.first()

    assert d_bulkmail.bulkmail_info == bulkmail.info

    envelops = Envelope.objects.filter(bulkmail=d_bulkmail)
    assert len(envelops) == len(bulkmail.recipients_list)

    envelope = envelops[0]

    assert envelope.text == bulkmail.message.text
    assert envelope.media == bulkmail.message.media.link
    assert envelope.status == Envelope.Status.NEW
    assert envelope.buttons == bulkmail.message.buttons
    assert envelope.user.user_id == bulkmail.recipients_list[0].address

    assert envelops.filter(~Q(status=Envelope.Status.NEW)).count() == 0
