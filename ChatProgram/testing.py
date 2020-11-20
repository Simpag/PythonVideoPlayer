import base64
import hashlib
import json
import os
from enum import Enum
import threading as thread
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import utils


class test:
    this = "is"

    def __init__(self, arg):
        self.arg = arg

    def method(self):
        print(self.arg)


class Types(Enum):
    message = 0
    createRoom = 2
    connectRoom = 3
    publicKey = 4


class threadingTest:
    def testThread(self, arg):
        print(arg)
        for i in range(10):
            print("Retard: ", i)
        self.another(" lol")

    def another(self, t):
        print("Another", t)

    def __init__(self):
        t = thread.Thread(target=self.testThread, args=("Test",), name="Client", daemon=True)
        t.start()
        t.join()


if __name__ == '__main__':



    m = {
        "type": "test"
    }
    ownPublicKey = ""
    ownPrivateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    ownPublicKey = ownPrivateKey.public_key()

    # print("is type ", type(ownPublicKey))

    # te = test("string")
    # te.method()

    # print(Types.message.value)

    t = threadingTest()
    _id = uuid.uuid1()
    print(_id)
    print((str(_id)))
    """
    _msg = {
        "type": 1,
        "alias": 2,
        "roomName": 3,
        "password": 4,
        "private": 6,
        "publicKey": 5,
    }

    for _m in _msg:
        print(_m)
    # Encrypting
    message = "This is a normal string".encode()

    # message_bytes = bytes(message, encoding='utf8') if not isinstance(message, bytes) else message
    ciphertext = ownPublicKey.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    ciphertext2 = str(base64.b64encode(ciphertext), encoding='utf-8')

    signer = ownPrivateKey.sign(
        message,
        padding.PSS(
            mgf = padding.MGF1(hashes.SHA256()),
            salt_length = padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature = str(
        base64.b64encode(signer),
        encoding='utf8'
    )

    j = json.dumps({"message": ciphertext2, "signature": signature})

    # Decrypting
    load = json.loads(j)

    ciphertext_decoded = base64.b64decode(load["message"]) if not isinstance(ciphertext, bytes) else ciphertext

    original_message = ownPrivateKey.decrypt(
        ciphertext_decoded,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    plain_text = str(original_message, encoding='utf8')
    print(original_message)
    print(plain_text)

    try:
        signature = base64.b64decode(
            signature
        ) if not isinstance(signature, bytes) else signature

        verifier = ownPublicKey.verify(
            signature,
            original_message,
            padding.PSS(
                mgf = padding.MGF1(hashes.SHA256()),
                salt_length = padding.PSS.MAX_LENGTH
             ),
            hashes.SHA256()
        )

        print("True")
    except InvalidSignature:
        print("False")"""
