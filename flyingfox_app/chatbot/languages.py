SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "native_name": "English",
    },

    "ml": {
        "name": "Malayalam",
        "native_name": "മലയാളം",
    },

    "hi": {
        "name": "Hindi",
        "native_name": "हिंदी",
    },

    "ta": {
        "name": "Tamil",
        "native_name": "தமிழ்",
    },
}


def get_language(language):
    """
    Return a safe supported language code.
    """

    language = str(language or "").strip().lower()

    if language in SUPPORTED_LANGUAGES:
        return language

    return "en"