import pytest
from bulkmail.internal.core.message import Media


def test_create_media():
    media_link = "https://example.com/static/pic.jpg"
    media_caption = "Message Media"
    media = Media(link=media_link, caption=media_caption)

    assert media.link == media_link
    assert media.caption == media_caption


def test_media_equal():
    media_link = "https://example.com/static/pic.jpg"
    media_caption = "Message Media"
    assert Media(link=media_link, caption=media_caption) == Media(
        link=media_link, caption=media_caption
    )


@pytest.mark.parametrize(
    "first_media, second_media",
    [
        (
            {"link": "http://example.com/static/pic_1.jpg", "caption": "equal"},
            {"link": "http://example.com/static/pic_2.jpg", "caption": "equal"},
        ),
        (
            {"link": "http://example.com/static/equal.jpg", "caption": "caption_1"},
            {"link": "http://example.com/static/equal.jpg", "caption": "caption_2"},
        ),
    ],
    ids=["By link", "By caption"],
)
def test_media_not_equal(first_media: dict, second_media: dict):
    assert Media(**first_media) != Media(**second_media)
