import hashlib
import binascii
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


def generate_wallet() -> dict:
    private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
    public_key = private_key.public_key()

    private_hex = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ).decode()

    public_hex = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    address = _public_key_to_address(public_hex)
    return {"private_key": private_hex, "public_key": public_hex, "address": address}


def _public_key_to_address(public_pem: str) -> str:
    pub_bytes = public_pem.encode()
    sha256 = hashlib.sha256(pub_bytes).digest()
    ripemd160 = hashlib.new("ripemd160", sha256).digest()
    return "1" + binascii.hexlify(ripemd160).decode()


def sign_transaction(private_pem: str, data: str) -> str:
    private_key = serialization.load_pem_private_key(
        private_pem.encode(), password=None, backend=default_backend()
    )
    signature = private_key.sign(data.encode(), ec.ECDSA(hashes.SHA256()))
    return binascii.hexlify(signature).decode()


def verify_signature(public_pem: str, data: str, signature_hex: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(
            public_pem.encode(), backend=default_backend()
        )
        public_key.verify(
            binascii.unhexlify(signature_hex),
            data.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except (InvalidSignature, Exception):
        return False
