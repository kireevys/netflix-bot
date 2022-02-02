import pytest
from bulkmail.core.message import Button


def test_create_button():
    text = "Button text"
    link = "http://example.com"
    button = Button(text=text, link=link)

    assert button.text == text
    assert button.link == link


def test_button_equal():
    text = "Button text"
    link = "http://example.com"
    assert Button(text=text, link=link) == Button(text=text, link=link)


@pytest.mark.parametrize(
    "first_button, second_button",
    [
        (
            {"link": "http://example.com/1", "text": "equal"},
            {"link": "http://example.com/2", "text": "equal"},
        ),
        (
            {"link": "http://example.com/", "text": "caption_1"},
            {"link": "http://example.com/", "text": "caption_2"},
        ),
    ],
    ids=["By link", "By caption"],
)
def test_button_not_equal(first_button: dict, second_button: dict):
    assert Button(**first_button) != Button(**second_button)
