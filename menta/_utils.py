import base64


def b64decode(b: bytes) -> bytes:
    # artificially add padding to make Python's base64 decoder accept it
    r = len(b) % 4
    if r > 0:
        b += b"=" * (4 - r)
    return base64.urlsafe_b64decode(b)


def b64encode(b: bytes) -> bytes:
    # strip any padding added by the encoder
    return base64.urlsafe_b64encode(b).replace(b"=", b"")
