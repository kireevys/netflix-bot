from bulkmail.internal.core.bulkmail import BulkmailPlan


def test_create_bulkmail_plan(message, bulkmail):
    bp = BulkmailPlan(bulkmail=bulkmail)

    assert bp.bulkmail == bulkmail
