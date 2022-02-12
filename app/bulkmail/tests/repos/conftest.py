import pytest
from bulkmail.models import DjangoBulkmail


@pytest.fixture
def django_bulkmail(bulkmail) -> DjangoBulkmail:
    return DjangoBulkmail.objects.create(
        title=bulkmail.info.title,
        customer=bulkmail.info.customer,
        price=bulkmail.info.price,
    )
