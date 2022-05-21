# menta [![build](https://github.com/alexbakker/menta/actions/workflows/build.yaml/badge.svg)](https://github.com/alexbakker/menta/actions/workflows/build.yaml?query=branch%3Amaster) ![coverage](https://alexbakker.me/gh/targets/menta/artifacts/coverage/coverage.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) ![PyPi version](https://img.shields.io/pypi/v/menta)

__menta__ is a secure, simple and easy to use API token format. It uses
__XChaCha20-Poly1305__ symmetric authenticated encryption to create encrypted
tokens and to ensure their integrity. There is no asymmetric option, and there
is zero cryptographic agility.

__Menta is currently experimental__. The first stable version will be __v1__.
When it's released, it'll be frozen and it will never be changed. A completely
new version will be released if we ever need to make changes or want to add new
features. If you start using this library today, you can be certain that it'll
still only accept v1 tokens tomorrow. Support for new versions will never be
silently introduced into your existing authentication code path.

Menta was inspired by [Branca](https://www.branca.io/) and is very similar to
it. There are a couple of differences:
* The timestamp is included in the ciphertext and thus is not readable to anyone
  without the key. This makes it less likely that users will trust the timestamp
  without verifying the token first.
* The timestamp is a 64-bit unsigned integer. So instead of overflowing in 2106,
  we'll be good for the next couple of hundred billion years.
* Base64 instead of base62 for better library support across programming
  languages.

## Usage

This repository serves as the reference implementation of Menta (in Python). It
can be used as follows:

```python
from menta import Menta, TokenData

# create a new menta instance with an existing key
key = bytes.fromhex("1df408259cdbba9492c2d01ad4dd942de4047f03ff32515fc6f333627f0e22b8")
menta = Menta(key)

# encode the text "hi!" into a new token
token = menta.encode(TokenData("hi!"))
print("encoded:", token)

# decode the token we just generated
data = menta.decode(token)
print("decoded:", data)

# encoded: v1:uhViDSxQNyaSd0BjXPqgmT53N6t2uSwC3KzxhMEsGis00pSgcqmfaLlhkAFJIun8mZCH
# decoded: TokenData(payload=b'hi!', timestamp=1653137637)
```

There's also a utility for generating a new key:

```python
from menta import Menta

# create a new menta instance with a freshly generated key
menta = Menta.generate()
print(menta.key.hex())
```

## Format

Menta tokens start with a version indicator, followed by a __base64url__
encoding of a concatenation of the nonce, the ciphertext and authentication tag:

```
"v1:" || nonce (24 bytes) || body ciphertext (? bytes) || tag (16 bytes)
```

The contents of the body consists of a concatenation of a timestamp and the
payload

```
timestamp (8 bytes) || payload (? bytes)
```

### Key

Menta requires a 256-bit key for use with __XChaCha20-Poly1305__. These 32 bytes
must be randomly generated using the operating system's CSPRNG.

### Fields

#### Version indicator

Every Menta token starts with a version indicator: ``v1:``

#### Body

##### Timestamp

Every Menta token contains the time at which it was generated: A Unix timestamp
(seconds elapsed since 00:00:00 UTC on 1 January 1970).

##### Payload

The payload is a binary blob of arbitrary length. We recommend using a
serialization format like [MessagePack](https://pydantic-docs.helpmanual.io/) or
[Protocol Buffers](https://developers.google.com/protocol-buffers) to encode the
payload. If you prefer JSON, use a strict library like
[Pydantic](https://pydantic-docs.helpmanual.io/) to validate the payload.

#### Nonce

The 196-bit nonce used in encryption and decryption of the ciphertext. It must
be randomly generated using the operating system's CSPRNG.

#### Authentication tag

The 128-bit tag used to authenticate the ciphertext.

### Generating

To generate a new token, given a key and payload:

1. Take note of the current time for the timestamp field.
2. Construct the token body.

    ```
    timestamp (64-bit big-endian unsigned integer) || payload (? bytes)
    ```

3. Generate a random nonce.
4. Construct the AAD by concatenating the version indicator and the nonce:

    ```
    "v1:" (ASCII) || nonce (24 bytes)
    ```

5. Calculate the ciphertext and authentication tag by encrypting the token body
   using __XChaCha20-Poly1305__. Pass the result of the previous step as AAD.
6. Concatenate the nonce, ciphertext and authentication tag. Encode the result
   using __base64url__ as defined in [RFC
   4648](https://datatracker.ietf.org/doc/html/rfc4648#section-5). Strip any
   padding from the result that may have been added by the base64 encoding.

    ```
    nonce (24 bytes) || ciphertext (? bytes) || tag (16 bytes)
    ```

7. Construct the token by concatenating the version indicator and the result of
   the previous step:

    ```
    "v1:" || base64url(nonce || ciphertext || tag)
    ```

### Decoding

To decode a token, given a key:

1. Split the token on the ``:`` character into two parts called ``version`` and
   ``body``. Verify that the result of the split is exactly 2 parts.
2. Verify that the ``version`` is equal to exactly ``"v1"``.
3. Decode the ``body`` using __base64url__ as defined in [RFC
   4648](https://datatracker.ietf.org/doc/html/rfc4648#section-5). If the base64
   library you're using expects padding, artificially add it beforehand.
4. Split up the decoded body as follows:

    ```
    nonce (24 bytes) | ciphertext (? bytes) | tag (16 bytes)
    ```

5. Construct the AAD by concatenating the version indicator and the nonce:

    ```
    "v1:" (ASCII) || nonce (24 bytes)
    ```

5. Decrypt the ciphertext using __XChaCha20-Poly1305__ with the given key, and
   the nonce and tag obtained in the previous steps.
6. Deconstruct the resulting plaintext as follows:

    ```
    timestamp (64-bit big-endian unsigned integer) | payload (? bytes)
    ```

7. Optionally, if the user has configured a TTL, verify that the token hasn't
   expired by adding the TTL to the timestamp and compare the result with the
   current time.

## Security

The format and implementation have not undergone a third-party security audit.
The goal is to keep Menta so simple that you can confidently say: "I trust
menta, because I trust XChaCha20-Poly1305".

Menta depends on [libsodium](https://doc.libsodium.org/) through
[PyNaCl](https://pynacl.readthedocs.io/en/latest/). It does not implement any
cryptographic primitives itself.
