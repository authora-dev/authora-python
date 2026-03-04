from __future__ import annotations

import base64
import hashlib
from typing import NamedTuple

from nacl.signing import SigningKey, VerifyKey


class KeyPair(NamedTuple):
    private_key: str
    public_key: str


def to_base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def from_base64url(b64url: str) -> bytes:
    padding = 4 - len(b64url) % 4
    if padding != 4:
        b64url += "=" * padding
    return base64.urlsafe_b64decode(b64url)


def generate_key_pair() -> KeyPair:
    sk = SigningKey.generate()
    return KeyPair(
        private_key=to_base64url(bytes(sk)),
        public_key=to_base64url(bytes(sk.verify_key)),
    )


def get_public_key(private_key_b64: str) -> str:
    sk = SigningKey(from_base64url(private_key_b64))
    return to_base64url(bytes(sk.verify_key))


def sha256_hash(input_str: str) -> str:
    digest = hashlib.sha256(input_str.encode("utf-8")).digest()
    return to_base64url(digest)


def build_signature_payload(
    method: str,
    path: str,
    timestamp: str,
    body: str | None,
) -> str:
    body_hash = sha256_hash(body) if body else ""
    return f"{method.upper()}\n{path}\n{timestamp}\n{body_hash}"


def sign(message: str, private_key_b64: str) -> str:
    sk = SigningKey(from_base64url(private_key_b64))
    signed = sk.sign(message.encode("utf-8"))
    return to_base64url(signed.signature)


def verify(message: str, signature_b64: str, public_key_b64: str) -> bool:
    vk = VerifyKey(from_base64url(public_key_b64))
    try:
        vk.verify(message.encode("utf-8"), from_base64url(signature_b64))
        return True
    except Exception:
        return False
