import logging
import os
import re
import time
import unicodedata

logger = logging.getLogger(__name__)

CITY_SLUG_ALIASES = {
    "bruxelles": "brussels",
    "seville": "sevilla",
    "valence": "valencia",
}

try:
    with open(".env") as f:
        env = {}
        for line in f:
            # Strip whitespace and skip comments and empty lines
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            # Split the line into key/value pair if possible
            try:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
            except ValueError:
                # Handle cases where the line can't be split into key/value
                print(f"Skipping invalid line: {line}")
except FileNotFoundError:
    env = os.environ

logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")


def slugify(text, separator="-"):
    # Define a dictionary to map special characters to their replacements
    special_character_map = {
        " ": separator,
        "_": separator,
        ".": separator,
        ",": separator,
        "(": separator,
        ")": separator,
        "[": separator,
        "]": separator,
        "{": separator,
        "}": separator,
        "!": separator,
        "?": separator,
        "@": separator,
        "#": separator,
        "$": separator,
        "%": separator,
        "^": separator,
        "&": separator,
        "*": separator,
        "/": separator,
        "\\": separator,
        "|": separator,
        "+": separator,
        "=": separator,
        "<": separator,
        ">": separator,
        ":": separator,
        ";": separator,
        '"': separator,
        "'": separator,
        "ø": "o",
    }

    # Normalize Unicode characters to NFKD form and remove diacritics
    text = "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )

    # Replace special characters with separators
    for char, replacement in special_character_map.items():
        text = text.replace(char, replacement)

    # Remove any remaining non-word characters and collapse consecutive separators
    text = re.sub(rf"[^\w{separator}]+", separator, text).strip(separator).lower()

    # Remove adjacent separators
    text = text.replace(2 * separator, separator)

    return text


def canonical_city_slug(text):
    """Return the current city slug, including known historical spellings."""
    slug = slugify(text)
    return CITY_SLUG_ALIASES.get(slug, slug)


def exponential_backoff_retry(func, max_attempts, on_attempt=None):
    for attempt in range(1, max_attempts + 1):
        if on_attempt is not None:
            on_attempt(attempt)
        try:
            return func()
        except Exception:
            if attempt < max_attempts:
                wait_time = 2 ** (attempt - 1)  # Exponential wait time
                logger.warning(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
