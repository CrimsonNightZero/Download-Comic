# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64

class Cryption:
    def __init__(self):
        self.BLOCK_SIZE = 32
        self.PADDING = '{'
        random = Random.new()
        self.iv = base64.b64encode(random.read(16)).decode("utf-8")
#        self.pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING

    def pad(self, data):
        return data + (self.BLOCK_SIZE - len(data) % self.BLOCK_SIZE) * self.PADDING

    def sha256(self, data):
        sha256 = hashlib.sha256()
        sha256.update(data.encode('utf-8'))
        return sha256.hexdigest()

    # Encryption
    def encryption(self, key, data):
        iv = base64.b64decode(self.iv)
        encryption_suite = AES.new(key[::4], AES.MODE_CBC, iv)
        cipher_text = encryption_suite.encrypt(self.pad(data))
        print("cipher_text:", cipher_text)
        base = base64.b64encode(cipher_text).decode("utf-8")
        print("base:", base)
        return base

    # Decryption
    def decryption(self, key, iv, cipher_text):
        iv = base64.b64decode(iv)
        debase = base64.b64decode(cipher_text)
        print("debase:", debase)
        decryption_suite = AES.new(key[::4], AES.MODE_CBC, iv)
        plain_text = decryption_suite.decrypt(debase)
        plain_text = plain_text.decode("utf-8").replace(self.PADDING,'')
        print("plain_text:", plain_text)
        return plain_text


def check_contain_chinese(check_str):
     for ch in check_str.decode('utf-8'):
         if u'\u4e00' <= ch <= u'\u9fff':
             return True
     return False
 
#from Crypto.Cipher import AES
#
#_IV = 16 * '\x00'
#
#def aes_encrypt(data, key):
#    cryptor = AES.new(key, AES.MODE_CBC, _IV)
#    return cryptor.encrypt(data)
#
#def aes_decrypt(data, key):
#    cryptor = AES.new(key, AES.MODE_CBC, _IV)
#    return cryptor.decrypt(data)


if __name__ == "__main__":
    cryption = Cryption()
    key = cryption.sha256("a")
    print(key)
    print(key[:16])
    print(cryption.iv)
    base = cryption.encryption(key, cryption.iv,"aaaaa")
    # iv = random.read(16)
    content = cryption.decryption(key, cryption.iv, base)
    a="3200".encode('utf-8')
    print(type(a))
    print(type(a.decode(("utf-8"))))
    print(check_contain_chinese(a))
    print("content:",content)
    a = "aaa"

    print(a)
    b = u'adassd'
    print(type(b))
    


