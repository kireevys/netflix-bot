def escape(text: str) -> str:
    """Экранирует для MarkdownV2 telegram."""
    return str(text).replace("!", r"\!").replace(".", r"\.")
