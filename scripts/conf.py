import logging
import os

try:
    with open(".env") as f:
        env = dict(kv.strip().split('=') for kv in f.readlines())
except FileNotFoundError:
    env = os.environ

logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")
