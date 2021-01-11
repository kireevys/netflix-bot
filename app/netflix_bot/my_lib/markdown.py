def escape(text: str) -> str:
    """Экранирует для MarkdownV2 telegram."""
    return (
        str(text)
        .replace("_", r"\_")
        .replace("*", r"\*")
        .replace("-", r"\-")
        .replace("(", r"\(")
        .replace(")", r"\)")
        .replace(".", r"\.")
    )
