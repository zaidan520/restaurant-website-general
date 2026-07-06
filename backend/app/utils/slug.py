import re
import unicodedata

def make_slug(value: str) -> str:
    # Normalize string to remove accents/diacritics
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Remove non-word characters (except spaces and hyphens)
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    # Replace spaces and multiple hyphens with a single hyphen
    value = re.sub(r'[-\s]+', '-', value)
    return value
