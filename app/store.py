import functools

from app.config import DATA_LOCATION
from berlin import load


@functools.cache
def get_db(location: str = DATA_LOCATION):
    db = load(location)
    return db
