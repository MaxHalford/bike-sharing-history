import logging
import os
import re
import time
import unicodedata

try:
    with open(".env") as f:
        env = dict(kv.strip().split("=") for kv in f.readlines())
except FileNotFoundError:
    env = os.environ

logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")

def slugify(text, separator='-'):
    # Define a dictionary to map special characters to their replacements
    special_character_map = {
        ' ': separator,
        '_': separator,
        '.': separator,
        ',': separator,
        '(': separator,
        ')': separator,
        '[': separator,
        ']': separator,
        '{': separator,
        '}': separator,
        '!': separator,
        '?': separator,
        '@': separator,
        '#': separator,
        '$': separator,
        '%': separator,
        '^': separator,
        '&': separator,
        '*': separator,
        '/': separator,
        '\\': separator,
        '|': separator,
        '+': separator,
        '=': separator,
        '<': separator,
        '>': separator,
        ':': separator,
        ';': separator,
        '"': separator,
        "'": separator,
        "ø": "o",
    }

    # Normalize Unicode characters to NFKD form and remove diacritics
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

    # Replace special characters with separators
    for char, replacement in special_character_map.items():
        text = text.replace(char, replacement)

    # Remove any remaining non-word characters and collapse consecutive separators
    text = re.sub(r'[^\w%s]+' % separator, separator, text).strip(separator).lower()

    # Remove adjacent separators
    text = text.replace(2 * separator, separator)

    return text


def exponential_backoff_retry(func, max_attempts):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as exc:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # Exponential wait time
                logging.warning(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise exc
