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
    canonical_payload = {
        key: payload[key]
        for key in ESSENTIAL_FIELDS
    }

    serialized = json.dumps(
        canonical_payload,
        sort_keys=True,
    )

    return hashlib.sha256(
        serialized.encode()
    ).hexdigest()