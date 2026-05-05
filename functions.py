## This file contains helper functions for encrypting and submitting the form data.
## use [pip install cryptography]
import json
import base64
import os
from urllib import request as urllib_request

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------- Helpers ----------
def buf_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')


def base64_to_buf(b64: str) -> bytes:
    return base64.b64decode(b64)


# ---------- Fetch public key ----------
def get_server_public_key():
    url = "http://localhost:5000/publicKey"
    with urllib_request.urlopen(url) as res:
        if res.status != 200:
            raise Exception("Could not fetch public key")
        data = json.loads(res.read().decode())
        return base64_to_buf(data["key"])


# ---------- Encrypt payload ----------
def encrypt_payload(payload: dict):
    spki_bytes = get_server_public_key()

    # Load RSA public key
    public_key = serialization.load_der_public_key(spki_bytes)

    # Generate AES key
    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)

    # IV (12 bytes)
    iv = os.urandom(12)

    # Encrypt payload
    encoded = json.dumps(payload).encode('utf-8')
    encrypted = aesgcm.encrypt(iv, encoded, None)

    # Split ciphertext and tag (last 16 bytes)
    ciphertext = encrypted[:-16]
    tag = encrypted[-16:]

    # Encrypt AES key with RSA
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return {
        "key": buf_to_base64(encrypted_key),
        "iv": buf_to_base64(iv),
        "ciphertext": buf_to_base64(ciphertext),
        "tag": buf_to_base64(tag)
    }


# ---------- Submit ----------
def submit_form():
    payload = {
        "firstName": "John",
        "middleInitial": "A",
        "lastName": "Doe",
        "ssn": "123-45-6789",
        "dob": "1990-01-01",
        "address": "123 Main St",
        "city": "Portland",
        "state": "OR",
        "zip": "97030",
        "annualIncome": "50000"
    }

    try:
        print("Encrypting and sending...")

        encrypted = encrypt_payload(payload)

        data = json.dumps(encrypted).encode('utf-8')

        req = urllib_request.Request(
            "http://localhost:5000/submit",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib_request.urlopen(req) as res:
            if res.status != 200:
                raise Exception("Server error")

        print("Submission successful.")

    except Exception as err:
        print("Submission failed:", err)


if __name__ == "__main__":
    submit_form()