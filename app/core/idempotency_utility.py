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


class MissingFieldError(ValueError):
    pass


def validate_payload(payload: dict):
    missing = [field for field in ESSENTIAL_FIELDS if payload.get(field) is None]
    if missing:
        raise MissingFieldError(f"Missing required fields: {missing}")

def generate_request_hash(payload: dict) -> str:
    validate_payload(payload)

    canonical_payload = {
        "user_id": payload.get("user_id"),
        "amount": payload.get("amount"),
        "currency": (
            payload.get("currency", "").upper()
        ),
        "provider": payload.get("provider"),
        "reference": payload.get("reference"), 
    }

    serialized = json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(serialized.encode()).hexdigest()