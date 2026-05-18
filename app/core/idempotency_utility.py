"""Request Hash Utility"""

import hashlib
import json


ESSENTIAL_FIELDS = [
    "user_id",
    "amount",
    "currency",
    "provider",
]


def generate_request_hash(payload: dict) -> str:
    pass