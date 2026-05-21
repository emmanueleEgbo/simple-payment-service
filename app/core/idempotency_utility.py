"""Request Hash Utility to ensure same key + different payload fail"""

import hashlib
import json


ESSENTIAL_FIELDS = [
    "user_id",
    "amount",
    "currency",
    "provider",
    "reference",
]


def generate_request_hash(payload: dict) -> str:
    canonical_payload = {
        
    }

    serialized = json.dumps(
        canonical_payload,
        sort_keys=True,
    )

    return hashlib.sha256(
        serialized.encode()
    ).hexdigest()