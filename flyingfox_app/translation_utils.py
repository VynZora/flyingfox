from deep_translator import GoogleTranslator


# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ml": "Malayalam",
    "hi": "Hindi",
    "ta": "Tamil",
}


# =========================================================
# GENERAL TRANSLATION FUNCTION
# =========================================================

def translate_text(
    text,
    target_language,
    source_language="auto",
):
    """
    Translate text from one language to another.

    If translation fails, return the original text so
    the chatbot does not crash.
    """

    text = str(text or "").strip()

    if not text:
        return ""

    # No translation required
    if source_language == target_language:
        return text

    try:

        translated = GoogleTranslator(
            source=source_language,
            target=target_language,
        ).translate(text)

        return translated or text

    except Exception as error:

        print(
            "CHATBOT TRANSLATION ERROR:",
            error,
        )

        return text


# =========================================================
# USER LANGUAGE -> ENGLISH
# =========================================================

def translate_to_english(
    text,
    user_language,
):
    """
    Convert Malayalam / Hindi / Tamil user questions
    into English before chatbot rule matching.
    """

    text = str(text or "").strip()

    if not text:
        return ""

    user_language = (
        user_language
        if user_language in SUPPORTED_LANGUAGES
        else "en"
    )

    if user_language == "en":
        return text

    return translate_text(
        text=text,
        source_language=user_language,
        target_language="en",
    )


# =========================================================
# ENGLISH -> USER LANGUAGE
# =========================================================

def translate_from_english(
    text,
    user_language,
):
    """
    Convert the chatbot's English response back into
    the language selected by the visitor.
    """

    text = str(text or "").strip()

    if not text:
        return ""

    user_language = (
        user_language
        if user_language in SUPPORTED_LANGUAGES
        else "en"
    )

    if user_language == "en":
        return text

    return translate_text(
        text=text,
        source_language="en",
        target_language=user_language,
    )