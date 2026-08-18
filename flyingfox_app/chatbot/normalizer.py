import re
import unicodedata


def normalize_text(text):

    text = str(
        text or ""
    )

    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    text = (
        text
        .casefold()
        .strip()
    )


    cleaned = []


    for char in text:

        category = (
            unicodedata.category(
                char
            )
        )


        # Letters
        if category.startswith("L"):

            cleaned.append(
                char
            )

            continue


        # Combining marks
        # Needed for Malayalam,
        # Hindi and Tamil
        if category.startswith("M"):

            cleaned.append(
                char
            )

            continue


        # Numbers
        if category.startswith("N"):

            cleaned.append(
                char
            )

            continue


        # Everything else becomes space
        cleaned.append(
            " "
        )


    text = "".join(
        cleaned
    )


    text = re.sub(
        r"\s+",
        " ",
        text,
    )


    return text.strip()