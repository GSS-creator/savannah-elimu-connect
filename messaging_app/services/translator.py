from flask import current_app

class TranslationService:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'fr': 'French',
            'sw': 'Swahili',
            'ar': 'Arabic'
        }
    
    @staticmethod
    def detect_language(text):
        """Detect the language of the given text"""
        # For now, return English as default
        return 'en'

    @staticmethod
    def translate_text(text, target_language, source_language=None):
        """Translate text to target language"""
        # For now, return original text and detected language
        return text, source_language or 'en'

    def get_supported_languages(self):
        """Get list of supported languages."""
        return self.supported_languages
    
    @staticmethod
    def is_language_supported(language_code):
        """Check if a language is supported"""
        supported_languages = [
            'en', 'fr', 'es', 'sw', 'ar', 'zh', 'hi', 'pt', 'ru', 'ja',
            'ko', 'de', 'it', 'nl', 'tr', 'pl', 'vi', 'th', 'id', 'ms'
        ]
        return language_code in supported_languages
