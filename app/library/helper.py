import hashlib

from unicodedata import normalize
from typing import List


def paginator(pg: int, pg_total: int) -> List[int]:
    if pg_total > 5:
        if pg > 3:
            pg_init = pg - 2
            if (pg + 1) > pg_total:
                pg_init = pg_init - 2
                pg_end = pg_total
            elif (pg + 2) > pg_total:
                pg_init = pg_init - 1
                pg_end = pg_total
            else:
                pg_init = pg - 2
                pg_end = pg + 2
        else:
            pg_init = 1
            pg_end = 5
    else:
        pg_init = 1
        pg_end = pg_total
    return list(range(pg_init, (pg_end + 1)))


def compare_values(value_1, value_2):
    return normalize_for_match(value_1) == normalize_for_match(value_2)


def normalize_for_match(value):
    return normalize('NFKD', value).encode('ASCII', 'ignore').decode('ASCII').lower().strip()


def generate_hash(value: str) -> str:
    return hashlib.md5(str(value).encode()).hexdigest()