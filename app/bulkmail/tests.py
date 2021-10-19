from bulkmail.models import Bulkmail, Button, Message, SendList
from django.test import TestCase
from netflix_bot.models import User


class TestSendBulkmail(TestCase):
    def test_create_bulkmail(self):
        for i in range(10):
            User.objects.create(user_id=i, user_name=i)

        message = Message.objects.create(
            text="Some text",
            content="http://google.com",
            content_type=Message.ContentTypes.PHOTO,
        )
        message.buttons.bulk_create(
            (
                Button(text="first", link="http://some.com"),
                Button(text="second", link="http://some.ru"),
            )
        )
        bulkmail = Bulkmail.objects.create(message=message)

        bulkmail.add_users(User.objects.all())

        result = bulkmail.get_list()

        assert len(result) == 10
        assert result.exclude(status=SendList.Statuses.NEW).count() == 0
