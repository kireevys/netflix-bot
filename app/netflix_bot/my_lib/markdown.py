def escape(text):
    return (
        str(text)
        .replace("_", r"\_")
        .replace("*", r"\*")
        .replace("-", r"\-")
        .replace("(", r"\(")
        .replace(")", r"\)")
    )
