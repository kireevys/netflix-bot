import pytest
from bulkmail.internal.core.message import Media


def test_create_media():
    media_link = "https://example.com/static/pic.jpg"
    media = Media(link=media_link)

    assert media.link == media_link


def test_media_equal():
    media_link = "https://example.com/static/pic.jpg"
    assert Media(link=media_link) == Media(link=media_link)


@pytest.mark.parametrize(
    "first_media, second_media",
    [
        (
            {"link": "http://example.com/static/pic_1.jpg"},
            {"link": "http://example.com/static/pic_2.jpg"},
        )
    ],
    ids=["By link"],
)
def test_media_not_equal(first_media: dict, second_media: dict):
    assert Media(**first_media) != Media(**second_media)
