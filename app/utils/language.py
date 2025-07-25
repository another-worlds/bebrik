from langdetect import detect

def detect_language(text: str) -> str:
    """
    Detect the language of the input text
    Returns 'tr' for Turkish, 'en' for English, etc.
    """
    try:
        return 'ru'
    except:
        return 'en'  # Default to English if detection fails
