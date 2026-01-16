import base64
import binascii
from pathlib import Path
from typing import Union

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


HexSeed = str


def load_private_key(path: Union[str, Path]) -> rsa.RSAPrivateKey:
    data = Path(path).read_bytes()
    return serialization.load_pem_private_key(data, password=None)


def load_public_key(path: Union[str, Path]) -> rsa.RSAPublicKey:
    data = Path(path).read_bytes()
    return serialization.load_pem_public_key(data)


def validate_hex_seed(hex_seed: str) -> None:
    if len(hex_seed) != 64:
        raise ValueError("Seed must be 64 hex characters")
    try:
        binascii.unhexlify(hex_seed)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Seed is not valid hex") from exc


def decrypt_seed(encrypted_seed_b64: str, private_key: rsa.RSAPrivateKey) -> HexSeed:
    ciphertext = base64.b64decode(encrypted_seed_b64)
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    hex_seed = plaintext.decode("utf-8")
    validate_hex_seed(hex_seed)
    return hex_seed


def sign_message(message: str, private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.sign(
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def encrypt_with_public_key(data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
